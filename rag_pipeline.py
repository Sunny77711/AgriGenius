"""
Reusable RAG pipeline for AgriGenius.

This module keeps the retrieval + generation logic separate from any CLI or UI.
The Streamlit frontend can import AgriGeniusRAG and call answer_query() to get
both the generated answer and the retrieved source passages.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

import chromadb
import numpy as np
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer


CHROMA_DB_PATH = "./chroma_kcc_db"
COLLECTION_NAME = "kcc_agri_advisor"
EMBED_MODEL_NAME = "l3cube-pune/hindi-sentence-bert-nli"
LLM_MODEL_NAME = "gemini-3.5-flash"
DEFAULT_TOP_K = 5
DEFAULT_FETCH_K = 20
MMR_LAMBDA = 0.72


SYSTEM_INSTRUCTION = """You are AgriGenius, a helpful agricultural advisory assistant for farmers in India.

Rules:
- Answer only using the provided Kisan Call Centre advisory context.
- If the context is not enough to answer safely, say that the available evidence is insufficient.
- Respond in the same language as the farmer's question whenever possible.
- Keep the answer practical, specific, and concise.
- Do not invent pesticide doses, fertilizer quantities, dates, schemes, or weather information.
"""


QUESTION_LIKE_PATTERNS = [
    re.compile(r"\?$"),
    re.compile(r"^(what|when|where|why|how|which|provide information|information about)\b", re.I),
    re.compile(r"^(जानकारी|बताइए|क्या|कब|कैसे|कौन)\b", re.I),
]


CROP_ALIASES = {
    "groundnut": "Groundnut (pea nut/mung phalli)",
    "peanut": "Groundnut (pea nut/mung phalli)",
    "मूंगफली": "Groundnut (pea nut/mung phalli)",
    "wheat": "Wheat",
    "गेहूं": "Wheat",
    "गेहूँ": "Wheat",
    "paddy": "Paddy (Dhan)",
    "rice": "Paddy (Dhan)",
    "धान": "Paddy (Dhan)",
    "mango": "Mango",
    "आम": "Mango",
    "sugarcane": "Sugarcane (Noble Cane)",
    "गन्ना": "Sugarcane (Noble Cane)",
    "mustard": "Mustard",
    "सरसों": "Mustard",
    "onion": "Onion",
    "प्याज": "Onion",
    "banana": "Banana",
    "केला": "Banana",
    "potato": "Potato",
    "आलू": "Potato",
    "maize": "Maize (Makka)",
    "corn": "Maize (Makka)",
    "मक्का": "Maize (Makka)",
}


QUERY_TYPE_ALIASES = {
    "irrigation": "Water Management",
    "water": "Water Management",
    "सिंचाई": "Water Management",
    "pest": "Plant Protection",
    "pests": "Plant Protection",
    "disease": "Plant Protection",
    "कीट": "Plant Protection",
    "रोग": "Plant Protection",
    "weed": "Weed Management",
    "weeds": "Weed Management",
    "खरपतवार": "Weed Management",
    "fertilizer": "Fertilizer Use and Availability",
    "fertiliser": "Fertilizer Use and Availability",
    "उर्वरक": "Fertilizer Use and Availability",
    "खाद": "Fertilizer Use and Availability",
    "seed rate": "Seeds",
    "seeds": "Seeds",
    "बीज दर": "Seeds",
}


DUPLICATE_STOPWORDS = {
    "sir",
    "madam",
    "farmer",
    "जी",
    "श्रीमान",
    "महोदय",
    "सर",
    "आप",
    "में",
    "के",
    "की",
    "का",
    "को",
    "लिए",
    "फसल",
}


@dataclass
class RetrievedSource:
    """One source passage retrieved from the KCC vector index."""

    rank: int
    text: str
    similarity: float
    metadata: dict[str, Any]

    def citation_label(self) -> str:
        crop = self.metadata.get("Crop") or "Unknown crop"
        district = self.metadata.get("DistrictName") or "Unknown district"
        query_type = self.metadata.get("QueryType") or "Unknown category"
        return f"KCC source {self.rank}: {crop} | {district} | {query_type}"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip()).lower()


def is_probable_non_answer(text: str) -> bool:
    """Flag obvious rows where KccAns looks like a question rather than advice."""
    clean = _normalize_text(text)
    if len(clean.split()) < 3:
        return True
    return any(pattern.search(clean) for pattern in QUESTION_LIKE_PATTERNS)


def _too_similar(text_a: str, text_b: str, threshold: float = 0.92) -> bool:
    a = _normalize_text(text_a)
    b = _normalize_text(text_b)
    if a == b:
        return True
    if SequenceMatcher(None, a, b).ratio() >= threshold:
        return True
    return _token_overlap(a, b) >= 0.78


def _token_overlap(text_a: str, text_b: str) -> float:
    tokens_a = _content_tokens(text_a)
    tokens_b = _content_tokens(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / min(len(tokens_a), len(tokens_b))


def _content_tokens(text: str) -> set[str]:
    tokens = set(re.findall(r"[\w\u0900-\u097F]+", text.lower()))
    return {token for token in tokens if token not in DUPLICATE_STOPWORDS and len(token) > 1}


def _safe_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    return {key: ("" if value is None else value) for key, value in dict(meta).items()}


def infer_crop_filter(query: str) -> dict[str, Any] | None:
    """Infer an exact Chroma metadata filter when the query names a known crop."""
    clean_query = _normalize_text(query)
    for alias, crop_name in CROP_ALIASES.items():
        if alias in clean_query:
            return {"Crop": crop_name}
    return None


def infer_query_type_filter(query: str) -> dict[str, Any] | None:
    """Infer an exact QueryType filter for clear advisory intents."""
    clean_query = _normalize_text(query)
    for alias, query_type in QUERY_TYPE_ALIASES.items():
        if alias in clean_query:
            return {"QueryType": query_type}
    return None


def infer_metadata_filter(query: str) -> dict[str, Any] | None:
    filters = [item for item in (infer_crop_filter(query), infer_query_type_filter(query)) if item]
    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


class AgriGeniusRAG:
    """Load once, then reuse for CLI, Streamlit, tests, or evaluation scripts."""

    def __init__(
        self,
        chroma_path: str = CHROMA_DB_PATH,
        collection_name: str = COLLECTION_NAME,
        embed_model_name: str = EMBED_MODEL_NAME,
        llm_model_name: str = LLM_MODEL_NAME,
    ) -> None:
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        self.embed_model_name = embed_model_name
        self.llm_model_name = llm_model_name
        self.embedding_model = SentenceTransformer(embed_model_name)
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_collection(collection_name)

    def collection_count(self) -> int:
        return self.collection.count()

    def retrieve_sources(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        fetch_k: int = DEFAULT_FETCH_K,
        where: dict[str, Any] | None = None,
        use_mmr: bool = True,
        drop_non_answers: bool = True,
        auto_metadata_filter: bool = True,
    ) -> list[RetrievedSource]:
        query_embedding = self.embedding_model.encode([query], normalize_embeddings=True)[0]
        n_results = max(fetch_k, top_k)
        query_filter = where or (infer_metadata_filter(query) if auto_metadata_filter else None)
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=query_filter,
            include=["documents", "metadatas", "distances", "embeddings"],
        )

        candidates: list[dict[str, Any]] = []
        embeddings = results.get("embeddings", [[None]])[0]
        for doc, meta, dist, emb in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
            embeddings,
        ):
            if drop_non_answers and is_probable_non_answer(doc):
                continue
            if any(_too_similar(doc, item["text"]) for item in candidates):
                continue
            candidates.append(
                {
                    "text": doc,
                    "metadata": _safe_metadata(meta),
                    "similarity": float(1 - dist),
                    "embedding": np.array(emb, dtype=float) if emb is not None else None,
                }
            )

        if use_mmr and candidates and candidates[0]["embedding"] is not None:
            selected = self._mmr_select(candidates, top_k)
        else:
            selected = candidates[:top_k]

        return [
            RetrievedSource(
                rank=idx + 1,
                text=item["text"],
                similarity=item["similarity"],
                metadata=item["metadata"],
            )
            for idx, item in enumerate(selected)
        ]

    def _mmr_select(self, candidates: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        remaining = candidates.copy()

        while remaining and len(selected) < top_k:
            if not selected:
                best = max(remaining, key=lambda item: item["similarity"])
            else:
                best = max(
                    remaining,
                    key=lambda item: (
                        MMR_LAMBDA * item["similarity"]
                        - (1 - MMR_LAMBDA) * self._max_source_similarity(item, selected)
                    ),
                )
            selected.append(best)
            remaining.remove(best)

        return selected

    @staticmethod
    def _max_source_similarity(candidate: dict[str, Any], selected: list[dict[str, Any]]) -> float:
        candidate_embedding = candidate["embedding"]
        if candidate_embedding is None:
            return 0.0
        similarities = []
        for item in selected:
            selected_embedding = item["embedding"]
            if selected_embedding is not None:
                similarities.append(float(candidate_embedding @ selected_embedding))
        return max(similarities, default=0.0)

    def build_prompt(self, query: str, sources: list[RetrievedSource]) -> str:
        context_block = "\n\n".join(
            f"[Source {source.rank}] "
            f"(Crop: {source.metadata.get('Crop', '?')}; "
            f"District: {source.metadata.get('DistrictName', '?')}; "
            f"Category: {source.metadata.get('QueryType', '?')})\n"
            f"{source.text}"
            for source in sources
        )
        return f"""Kisan Call Centre advisory context:
{context_block}

Farmer question: {query}

Answer:"""

    def generate_answer(self, query: str, sources: list[RetrievedSource]) -> str:
        if not sources:
            return "I do not have enough reliable KCC context to answer this question safely."

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.llm_model_name,
            contents=self.build_prompt(query, sources),
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
        return response.text or ""

    def answer_query(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        fetch_k: int = DEFAULT_FETCH_K,
        where: dict[str, Any] | None = None,
        generate: bool = True,
    ) -> dict[str, Any]:
        sources = self.retrieve_sources(query, top_k=top_k, fetch_k=fetch_k, where=where)
        answer = self.generate_answer(query, sources) if generate else ""
        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "source_count": len(sources),
            "collection_count": self.collection_count(),
        }
