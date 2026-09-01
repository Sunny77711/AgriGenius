"""
kcc_rag_query.py

Basic RAG pipeline: retrieval (ChromaDB) -> grounded LLM generation.
This is step 8 of the project plan -- the first end-to-end working pipeline.

Deliberately basic: no reranking, no multi-turn intent resolution yet
(that's the next step). AgriSci-QA is NOT touched anywhere in this script --
it stays held out until the pipeline is frozen and ready for final eval.

Retrieval model: l3cube-pune/hindi-sentence-bert-nli -- MUST match the model
used in kcc_build_index.py, or the query embedding won't line up with the
stored vectors.

LLM: Gemini 2.5 Flash via the current unified google-genai SDK (the older
google-generativeai package is deprecated). Swap the model name in call_llm()
for gemini-3-flash or gemini-3.1-flash-lite if you want to try the newer
generation -- everything else in this script is model-agnostic.

Setup
-----
pip install chromadb sentence-transformers google-genai

Get a free Gemini API key at https://aistudio.google.com/apikey, then:
    export GEMINI_API_KEY="your-key-here"

Usage
-----
python kcc_rag_query.py                  # runs a small built-in test set
python kcc_rag_query.py --interactive    # type your own queries (Hindi or English)
"""
import os
import sys
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types

# --- Config ------------------------------------------------------------
CHROMA_DB_PATH = "./chroma_kcc_db"
COLLECTION_NAME = "kcc_agri_advisor"
EMBED_MODEL_NAME = "l3cube-pune/hindi-sentence-bert-nli"
LLM_MODEL_NAME = "gemini-3.5-flash"
TOP_K = 5



# Small manual dev set -- stand-in until FarmerChat is integrated.
# Deliberately never draws from AgriSci-QA (held out for final eval only).
TEST_QUERIES = [
    "What is the seed rate for groundnut crop?",
    "गेहूं की फसल में सिंचाई कब करनी चाहिए?",
    "How do I control pests in mango trees?",
    "धान की फसल में खरपतवार को कैसे नियंत्रित करें?",
]

SYSTEM_INSTRUCTION = """You are a helpful agricultural advisory assistant for farmers in India, \
in the style of Kisan Call Centre expert advice.

Rules:
- Answer ONLY using the information in the provided context passages, which are real \
advisory answers given to other farmers by agricultural experts.
- If the context does not contain enough information to answer confidently, say so \
clearly instead of guessing or inventing details.
- Respond in the SAME language the farmer's question was asked in (Hindi or English).
- Keep the answer practical, specific, and concise -- similar in style and length to \
the source advisory answers, not a long essay.
"""


def load_retriever():
    print(f"Loading embedding model: {EMBED_MODEL_NAME} ...")
    model = SentenceTransformer(EMBED_MODEL_NAME)
    print(f"Connecting to ChromaDB at {CHROMA_DB_PATH} ...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Collection loaded: {collection.count():,} vectors.\n")
    return model, collection


def retrieve(query, model, collection, k=TOP_K):
    query_embedding = model.encode([query], normalize_embeddings=True)[0]
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    passages = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        similarity = 1 - dist  # collection uses cosine space: distance = 1 - cosine_similarity
        passages.append({"text": doc, "metadata": meta, "similarity": similarity})
    return passages


def build_prompt(query, passages):
    context_block = "\n\n".join(
        f"[Passage {i + 1}] (Crop: {p['metadata'].get('Crop', '?')}, "
        f"District: {p['metadata'].get('DistrictName', '?')}, "
        f"Category: {p['metadata'].get('QueryType', '?')})\n{p['text']}"
        for i, p in enumerate(passages)
    )
    return f"""Context passages:
{context_block}

Farmer's question: {query}

Answer:"""


def call_llm(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable not set. "
            "Get a free key at https://aistudio.google.com/apikey and run:\n"
            '    export GEMINI_API_KEY="your-key-here"'
        )
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=LLM_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
        ),
    )
    return response.text


def answer_query(query, model, collection):
    print("=" * 100)
    print(f"QUERY: {query}")
    print("=" * 100)

    passages = retrieve(query, model, collection)
    print(f"\nRetrieved {len(passages)} passages:")
    for i, p in enumerate(passages, 1):
        print(f"  [{i}] sim={p['similarity']:.3f} | {p['metadata'].get('Crop', '?')} | "
              f"{p['text'][:100]}")

    prompt = build_prompt(query, passages)
    print("\nGenerating grounded answer ...")
    try:
        answer = call_llm(prompt)
    except RuntimeError as e:
        print(f"\n[LLM call skipped] {e}")
        return

    print(f"\nANSWER:\n{answer}\n")


def main():
    model, collection = load_retriever()

    if "--interactive" in sys.argv:
        print("Interactive mode. Type a query (English or Hindi), or 'quit' to exit.\n")
        while True:
            query = input("Query> ").strip()
            if query.lower() in ("quit", "exit"):
                break
            if not query:
                continue
            answer_query(query, model, collection)
    else:
        for query in TEST_QUERIES:
            answer_query(query, model, collection)


if __name__ == "__main__":
    main()