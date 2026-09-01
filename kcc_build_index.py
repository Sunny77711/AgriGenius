"""
kcc_build_index.py

Full-corpus embedding + ChromaDB indexing for the KCC retrieval corpus.

Model: l3cube-pune/hindi-sentence-bert-nli (winner of the embedding bake-off:
       best recall@5/recall@10, second-fastest of the three candidates tested)
Input: kcc_index_ready_final.csv (post PII-strip -- run kcc_strip_pii.py first,
       and apply your Sowing Time and Weather decision if you chose to filter it)
Output: a persistent ChromaDB collection on disk at ./chroma_kcc_db, ready for
        the retrieval step of the RAG pipeline.

Resumable: progress is checkpointed to disk (kcc_index_checkpoint.json) after
every batch. If interrupted (sleep, crash, Ctrl-C), just rerun the same
command -- it skips batches already written. If the input CSV path or row
count changes since the last checkpoint, progress is automatically reset
(so it can't silently misalign after you filter the file further).

Estimated time: ~30 minutes on a CPU-only MacBook Air for ~361K rows, based
on the ~206 texts/sec measured during the embedding model comparison.
Actual throughput is measured live and an ETA is printed as it runs.

Install (if not already present):
    pip install chromadb
"""

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import json
import os
import time

# --- Config --------------------------------------------------------------
CSV_PATH = "kcc_index_ready_final.csv"
MODEL_NAME = "l3cube-pune/hindi-sentence-bert-nli"
CHROMA_DB_PATH = "./chroma_kcc_db"
COLLECTION_NAME = "kcc_agri_advisor"
CHECKPOINT_PATH = "kcc_index_checkpoint.json"
BATCH_SIZE = 256
METADATA_COLUMNS = ["Crop", "DistrictName", "StateName", "QueryType", "Sector", "day", "month", "year"]
ID_COLUMN = "KCCCallID"
TEXT_COLUMN = "KccAns"


def load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH) as f:
            return json.load(f)
    return {"completed_batches": [], "csv_path": None, "n_rows": None}


def save_checkpoint(state):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(state, f)


def build_metadata(row):
    meta = {}
    for col in METADATA_COLUMNS:
        val = row.get(col, None)
        if pd.isna(val):
            meta[col] = ""
        elif col in ("day", "month", "year"):
            try:
                meta[col] = int(val)
            except (ValueError, TypeError):
                meta[col] = str(val)
        else:
            meta[col] = str(val)
    meta["source"] = "KCC"
    return meta


def main():
    print(f"Loading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH)
    n = len(df)
    print(f"Loaded {n:,} rows.")

    if df[ID_COLUMN].duplicated().any():
        print(f"WARNING: {ID_COLUMN} has duplicates -- falling back to row-index-based IDs.")
        ids_all = [f"row_{i}" for i in range(n)]
    else:
        ids_all = df[ID_COLUMN].astype(str).tolist()

    texts_all = df[TEXT_COLUMN].astype(str).tolist()

    checkpoint = load_checkpoint()
    if checkpoint.get("csv_path") != CSV_PATH or checkpoint.get("n_rows") != n:
        if checkpoint.get("completed_batches"):
            print("Input file or row count changed since last checkpoint -- resetting progress.")
        checkpoint = {"completed_batches": [], "csv_path": CSV_PATH, "n_rows": n}
    completed = set(checkpoint["completed_batches"])

    print(f"Loading model: {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Connecting to ChromaDB at {CHROMA_DB_PATH} ...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    n_batches = (n + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\nTotal rows: {n:,} | Batch size: {BATCH_SIZE} | Total batches: {n_batches}")
    print(f"Already completed: {len(completed)} batches (resuming)\n")

    start_time = time.time()
    rows_done_this_run = 0

    for batch_idx in range(n_batches):
        if batch_idx in completed:
            continue

        start = batch_idx * BATCH_SIZE
        end = min(start + BATCH_SIZE, n)

        batch_texts = texts_all[start:end]
        batch_ids = ids_all[start:end]
        batch_meta = [build_metadata(df.iloc[i]) for i in range(start, end)]

        embeddings = model.encode(batch_texts, normalize_embeddings=True, show_progress_bar=False)

        collection.upsert(
            ids=batch_ids,
            embeddings=embeddings.tolist(),
            documents=batch_texts,
            metadatas=batch_meta,
        )

        completed.add(batch_idx)
        checkpoint["completed_batches"] = list(completed)
        save_checkpoint(checkpoint)

        rows_done_this_run += (end - start)
        elapsed = time.time() - start_time
        rate = rows_done_this_run / elapsed if elapsed > 0 else 0
        remaining_batches = n_batches - len(completed)
        eta_sec = (remaining_batches * BATCH_SIZE) / rate if rate > 0 else float("inf")

        print(f"Batch {batch_idx + 1}/{n_batches} done "
              f"({end:,}/{n:,} rows total) | "
              f"{rate:.1f} rows/sec this run | "
              f"ETA {eta_sec / 60:.1f} min", flush=True)

    print(f"\nDone. Collection '{COLLECTION_NAME}' now has {collection.count():,} vectors.")
    print(f"Stored at: {CHROMA_DB_PATH}")
    print("Delete kcc_index_checkpoint.json if you ever want to force a full re-embed from scratch.")


if __name__ == "__main__":
    main()