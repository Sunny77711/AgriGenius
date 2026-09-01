"""
Embedding Model Comparison for KCC Retrieval
==============================================
Compares candidate multilingual/Hindi sentence-embedding models on a
sample of the cleaned KCC corpus (kcc_index_ready.csv), using a simple
self-retrieval test: for each KccAns, its own QueryText (short agent
label) is used as the query, and we check whether the correct KccAns
ends up in the model's top-k retrieved results out of the sample.

This isn't a perfect proxy for real farmer queries (QueryText is a
short agent-written label, not verbatim speech), but it's a fast, fair
way to compare candidate models against EACH OTHER before committing
to embedding the full ~360K-row corpus with whichever one wins.

Usage:
    pip install sentence-transformers --break-system-packages
    python embedding_model_comparison.py

If a model fails to load (wrong repo name, not cached, etc.), the
script skips it and keeps going — you don't need all three to work
to make a decision.
"""

import time
import pandas as pd
from sentence_transformers import SentenceTransformer

# ============================== CONFIG ===================================

CORPUS_PATH = "kcc_index_ready.csv"
SAMPLE_SIZE = 800          # small on purpose — this is a bake-off, not the real index
TOP_K = (1, 5, 10)
RANDOM_SEED = 42

CANDIDATE_MODELS = {
    "multilingual-e5-base": {
        "name": "intfloat/multilingual-e5-base",
        "query_prefix": "query: ",       # E5 models require these literal prefixes
        "passage_prefix": "passage: ",
    },
    "paraphrase-multilingual-mpnet": {
        "name": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "query_prefix": "",
        "passage_prefix": "",
    },
    "hindi-sentence-bert (l3cube)": {
        "name": "l3cube-pune/hindi-sentence-bert-nli",
        "query_prefix": "",
        "passage_prefix": "",
    },
}


# =============================== HELPERS ===================================

def load_sample(path, n, seed):
    df = pd.read_csv(path, low_memory=False)
    df = df.dropna(subset=["QueryText", "KccAns"])
    df = df[df["QueryText"].str.strip().astype(bool)]
    sample = df.sample(min(n, len(df)), random_state=seed).reset_index(drop=True)
    print(f"Loaded {len(df):,} eligible rows, sampled {len(sample):,} for comparison.\n")
    return sample


def evaluate_model(label, config, sample: pd.DataFrame):
    print(f"--- {label} ({config['name']}) ---")
    try:
        model = SentenceTransformer(config["name"])
    except Exception as e:
        print(f"  [skip] Could not load model: {e}\n")
        return None

    queries = [config["query_prefix"] + str(q) for q in sample["QueryText"].tolist()]
    passages = [config["passage_prefix"] + str(a) for a in sample["KccAns"].tolist()]

    t0 = time.time()
    query_emb = model.encode(queries, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
    passage_emb = model.encode(passages, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
    elapsed = time.time() - t0

    sims = query_emb @ passage_emb.T           # cosine similarity (embeddings are normalized)
    ranks = (-sims).argsort(axis=1)             # descending similarity, per query

    n = len(sample)
    results = {}
    for k in TOP_K:
        hits = sum(i in ranks[i, :k] for i in range(n))
        results[f"recall@{k}"] = hits / n

    docs_per_sec = (len(queries) + len(passages)) / elapsed
    print(f"  Encoded {len(queries) + len(passages):,} texts in {elapsed:.1f}s "
          f"({docs_per_sec:.0f} texts/sec on this machine)")
    for k in TOP_K:
        print(f"  Recall@{k}: {results[f'recall@{k}']:.3f}")
    print()

    return {"model": label, "elapsed_sec": round(elapsed, 1),
             "docs_per_sec": round(docs_per_sec, 0), **results}


# ================================= MAIN =====================================

if __name__ == "__main__":
    sample = load_sample(CORPUS_PATH, SAMPLE_SIZE, RANDOM_SEED)

    all_results = []
    for label, config in CANDIDATE_MODELS.items():
        res = evaluate_model(label, config, sample)
        if res:
            all_results.append(res)

    if all_results:
        print("=" * 60)
        print("Summary")
        print("=" * 60)
        summary_df = pd.DataFrame(all_results).set_index("model")
        print(summary_df.round(3).to_string())
        print("\nPick the model with the best recall@5 / recall@10 that still encodes fast "
              "enough for your corpus size — at ~363K rows, even a 2x speed difference in "
              "texts/sec matters a lot once you scale from this 800-row sample to the real index.")
    else:
        print("No models loaded successfully — check error messages above.")