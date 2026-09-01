"""
qualitative_retrieval_check.py

Purpose
-------
Sanity-check the WINNING embedding model (l3cube-pune/hindi-sentence-bert-nli)
before committing ~30 min of wall-clock time to embedding the full 363K-row
kcc_index_ready.csv.

Why this exists
---------------
The recall@k self-retrieval benchmark uses QueryText (a short, agent-written
CATEGORY LABEL like "Farmer asked query on Weather") as the query, and KccAns
as the passage. Many unrelated rows share near-identical QueryText strings, so
low recall@k may reflect that the query text carries little distinguishing
signal -- NOT that the model is bad at real Hindi/English retrieval.

This script sidesteps that ambiguity: instead of trusting a single recall
number, it lets you eyeball whether retrieved answers are thematically
sensible (right crop/topic) for a handful of real rows. If the top-5 results
look reasonable even when they don't hit the "official" paired row, that's a
green light to proceed with the full-corpus index.

Usage
-----
python qualitative_retrieval_check.py
(edit CSV_PATH below if kcc_index_ready.csv isn't in the same directory)
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "l3cube-pune/hindi-sentence-bert-nli"
CSV_PATH = "kcc_index_ready.csv"
CORPUS_SAMPLE_SIZE = 2000   # subset to search against (fast local check, not the full 363K)
NUM_QUERIES = 15            # how many sample queries to print results for
TOP_K = 5


def main():
    print(f"Loading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows.\n")

    print(f"Loading model: {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)

    # Build a small corpus to search against (swap CORPUS_SAMPLE_SIZE up if you want
    # a harder test closer to full-scale, but 2000 is enough to judge thematic quality)
    corpus_df = df.sample(n=min(CORPUS_SAMPLE_SIZE, len(df)), random_state=42).reset_index(drop=True)
    print(f"Encoding corpus of {len(corpus_df):,} KccAns entries ...")
    corpus_embeddings = model.encode(
        corpus_df["KccAns"].astype(str).tolist(),
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    # Pick sample query rows FROM WITHIN the corpus so a "true match" exists to compare against
    query_rows = corpus_df.sample(n=min(NUM_QUERIES, len(corpus_df)), random_state=7).reset_index(drop=True)
    print(f"\nEncoding {len(query_rows)} sample queries ...")
    query_embeddings = model.encode(
        query_rows["QueryText"].astype(str).tolist(),
        normalize_embeddings=True,
    )

    # Cosine similarity (embeddings are normalized, so dot product = cosine sim)
    sims = query_embeddings @ corpus_embeddings.T

    for i, row in query_rows.iterrows():
        top_idx = np.argsort(-sims[i])[:TOP_K]
        print("=" * 100)
        print(f"QueryText   : {row['QueryText']}")
        crop = row.get("Crop", "?")
        sector = row.get("Sector", "?")
        print(f"Crop/Sector : {crop} / {sector}")
        true_ans = str(row["KccAns"])
        print(f"TRUE KccAns : {true_ans[:150]}")
        print("-" * 100)
        for rank, idx in enumerate(top_idx, 1):
            candidate = str(corpus_df.loc[idx, "KccAns"])
            marker = "  <-- TRUE MATCH" if candidate == true_ans else ""
            print(f"  #{rank} (sim={sims[i][idx]:.3f}): {candidate[:150]}{marker}")
        print()

    print("=" * 100)
    print("Manually judge: do the top-5 results generally stay on-topic (same crop/")
    print("issue area) even when they miss the exact 'true match'? If yes, the model")
    print("is working -- proceed to the full-corpus embedding + ChromaDB indexing step.")


if __name__ == "__main__":
    main()