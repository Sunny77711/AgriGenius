"""
retrieval_diagnostics.py

Follow-up checks after the first RAG smoke test surfaced three suspected issues:

1. CROSS-LINGUAL RETRIEVAL GAP: an English query for groundnut seed rate
   returned zero groundnut passages, despite groundnut seed-rate content
   almost certainly existing in the (Hindi) corpus. Tests matched
   English/Hindi query pairs across several crops to see if English queries
   systematically underperform Hindi queries at finding the right crop.

2. NON-ANSWER ROWS: some retrieved "KccAns" text was actually a restated
   question (e.g. "Which pesticide should be used to control stem eating
   insect in mango plant?") rather than real advisory content. Estimates how
   common this is across the corpus.

3. NEAR-DUPLICATE FLOODING: the paddy weed-control query returned 5 nearly
   identical short answers ("do weeding"), suggesting exact-string dedup
   during cleaning didn't catch near-duplicates with minor phrasing
   differences. Estimates how often a row's own nearest neighbors are
   near-duplicates of itself.

Usage
-----
python retrieval_diagnostics.py
"""

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

CSV_PATH = "kcc_index_ready_final.csv"
CHROMA_DB_PATH = "./chroma_kcc_db"
COLLECTION_NAME = "kcc_agri_advisor"
EMBED_MODEL_NAME = "l3cube-pune/hindi-sentence-bert-nli"

# (english, hindi, expected_crop_substring)
PAIRED_QUERIES = [
    ("What is the seed rate for groundnut crop?", "मूंगफली की फसल में बीज दर क्या है?", "Groundnut"),
    ("How to control pests in banana plants?", "केले के पौधों में कीट नियंत्रण कैसे करें?", "Banana"),
    ("What fertilizer should I use for sugarcane?", "गन्ने की फसल में कौन सा उर्वरक इस्तेमाल करें?", "Sugarcane"),
    ("When should I sow mustard seeds?", "सरसों की बुवाई कब करनी चाहिए?", "Mustard"),
    ("How to manage weeds in onion crop?", "प्याज की फसल में खरपतवार प्रबंधन कैसे करें?", "Onion"),
]


def load_retriever():
    model = SentenceTransformer(EMBED_MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    return model, collection


def retrieve(query, model, collection, k=5):
    emb = model.encode([query], normalize_embeddings=True)[0]
    results = collection.query(query_embeddings=[emb.tolist()], n_results=k,
                                include=["documents", "metadatas", "distances"])
    out = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        out.append({"text": doc, "crop": meta.get("Crop", "?"), "similarity": 1 - dist})
    return out


# --- 1. Cross-lingual gap ---------------------------------------------------
def check_cross_lingual_gap(model, collection):
    print("Testing matched English/Hindi query pairs ...\n")
    en_hits, hi_hits = 0, 0
    for en_q, hi_q, expected_crop in PAIRED_QUERIES:
        en_results = retrieve(en_q, model, collection, k=5)
        hi_results = retrieve(hi_q, model, collection, k=5)

        en_crop_hit = any(expected_crop.lower() in r["crop"].lower() for r in en_results)
        hi_crop_hit = any(expected_crop.lower() in r["crop"].lower() for r in hi_results)
        en_hits += en_crop_hit
        hi_hits += hi_crop_hit

        print(f"Expected crop: {expected_crop}")
        print(f"  EN '{en_q}' -> top crops: {[r['crop'] for r in en_results]} "
              f"{'[HIT]' if en_crop_hit else '[MISS]'}")
        print(f"  HI '{hi_q}' -> top crops: {[r['crop'] for r in hi_results]} "
              f"{'[HIT]' if hi_crop_hit else '[MISS]'}")
        print()

    n = len(PAIRED_QUERIES)
    print(f"English query crop-hit rate: {en_hits}/{n} ({en_hits / n * 100:.0f}%)")
    print(f"Hindi query crop-hit rate:   {hi_hits}/{n} ({hi_hits / n * 100:.0f}%)")


# --- 2. Non-answer detection -------------------------------------------------
def check_non_answers(df, sample_size=5000):
    sample = df.sample(n=min(sample_size, len(df)), random_state=1)
    kcc_ans = sample["KccAns"].astype(str)
    query_text = sample["QueryText"].astype(str)

    ends_with_question = kcc_ans.str.strip().str.endswith("?")
    same_prefix = kcc_ans.str[:20].str.lower() == query_text.str[:20].str.lower()
    flagged = ends_with_question | same_prefix

    print(f"Sampled {len(sample):,} rows.")
    print(f"  KccAns ends with '?' (looks like a restated question): {ends_with_question.sum():,} "
          f"({ends_with_question.sum() / len(sample) * 100:.2f}%)")
    print(f"  KccAns shares QueryText's opening (likely echoed question): {same_prefix.sum():,} "
          f"({same_prefix.sum() / len(sample) * 100:.2f}%)")
    print(f"  Total flagged (either signal): {flagged.sum():,} "
          f"({flagged.sum() / len(sample) * 100:.2f}%)")

    if flagged.sum():
        print("\nSample flagged rows:")
        for _, row in sample[flagged].sample(n=min(5, flagged.sum()), random_state=1).iterrows():
            print(f"  QueryText: {row['QueryText'][:80]}")
            print(f"  KccAns   : {row['KccAns'][:80]}")
            print()


# --- 3. Near-duplicate flooding ---------------------------------------------
def check_near_duplicate_flooding(df, model, collection, n_probe=30, dup_threshold=0.95):
    print(f"Probing {n_probe} random corpus rows for near-duplicate flooding "
          f"(excluding exact self-match) ...")
    sample = df.sample(n=n_probe, random_state=2)
    flood_counts = []
    for _, row in sample.iterrows():
        text = str(row["KccAns"])
        results = retrieve(text, model, collection, k=6)  # +1 to allow excluding self
        others = [r for r in results if r["text"] != text][:5]
        near_dups = sum(1 for r in others if r["similarity"] > dup_threshold)
        flood_counts.append(near_dups)

    avg_flood = sum(flood_counts) / len(flood_counts)
    heavily_flooded = sum(1 for c in flood_counts if c >= 3)
    print(f"  Average near-duplicates in top-5 (sim > {dup_threshold}, self excluded): {avg_flood:.2f} / 5")
    print(f"  Rows where >=3 of 5 nearest neighbors are near-duplicates: "
          f"{heavily_flooded}/{n_probe} ({heavily_flooded / n_probe * 100:.1f}%)")


def main():
    print(f"Loading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows.\n")

    print("Loading model + ChromaDB collection ...")
    model, collection = load_retriever()
    print()

    print("=" * 100)
    print("1. CROSS-LINGUAL RETRIEVAL GAP CHECK")
    print("=" * 100)
    check_cross_lingual_gap(model, collection)
    print()

    print("=" * 100)
    print("2. NON-ANSWER ROW CHECK")
    print("=" * 100)
    check_non_answers(df)
    print()

    print("=" * 100)
    print("3. NEAR-DUPLICATE FLOODING CHECK")
    print("=" * 100)
    check_near_duplicate_flooding(df, model, collection)


if __name__ == "__main__":
    main()