"""
KCC Multi-File Ingestion & Pooling Script
==========================================
Consolidates separately-downloaded KCC exports (one file per state/year,
or per state/year/month depending on how AIKosh lets you filter) into a
single, schema-validated master dataset.

Usage:
    1. Download your filtered KCC exports from AIKosh/data.gov.in and drop
       ALL of them (any state, any year) into RAW_DATA_DIR below — no need
       to sort them into subfolders first.
    2. Update RAW_DATA_DIR and OUTPUT_PATH below.
    3. Run: python kcc_pool_datasets.py

What it does:
    - Reads every .csv (and .json, if present) file in RAW_DATA_DIR
    - Standardizes column names (case/whitespace-insensitive matching)
    - Backfills StateName/year from the filename if a file is missing
      those columns (common when a filtered export drops the filter
      field itself — check your actual files; this is a safety net,
      not a guaranteed fix, so watch the [warn] lines below)
    - Concatenates everything into one DataFrame
    - Drops exact duplicate rows (common if you accidentally re-download
      overlapping ranges)
    - Reports row counts per state/year so you can sanity-check coverage
      BEFORE moving on to the EDA step
    - Saves the consolidated file to OUTPUT_PATH

Once this runs cleanly, feed OUTPUT_PATH into farming_assistant_dataset_eda.py
(KCC_PATH) from the earlier EDA pass.
"""

import os
import re
import glob
import pandas as pd

# ============================== CONFIG ===================================

RAW_DATA_DIR = "C:/Users/Tejasvi Senka/OneDrive/Documents/College/Projects/Datasets"     # folder containing all your per-state/year files
OUTPUT_PATH = "kcc_pooled.csv"          # consolidated output

EXPECTED_COLUMNS = [
    "BlockName", "Category", "CreatedOn", "Crop", "DistrictName",
    "KCCCallID", "KccAns", "QueryText", "QueryType", "Season",
    "Sector", "StateName", "day", "month", "year",
]

# Handles minor naming differences across export batches (extend this as
# you see your actual downloaded column headers — AIKosh exports aren't
# always perfectly consistent across filter combinations).
COLUMN_ALIASES = {c.lower().strip(): c for c in EXPECTED_COLUMNS}
COLUMN_ALIASES.update({
    "kcc_ans": "KccAns", "kccans": "KccAns", "answer": "KccAns",
    "query_text": "QueryText", "querytext": "QueryText", "query": "QueryText",
    "query_type": "QueryType", "querytype": "QueryType",
    "state_name": "StateName", "statename": "StateName", "state": "StateName",
    "district_name": "DistrictName", "districtname": "DistrictName", "district": "DistrictName",
    "block_name": "BlockName", "blockname": "BlockName", "block": "BlockName",
    "created_on": "CreatedOn", "createdon": "CreatedOn",
    "kcc_call_id": "KCCCallID", "kcccallid": "KCCCallID", "callid": "KCCCallID",
})

# Adjust this regex to match your ACTUAL downloaded filenames once you see
# them, e.g. "UttarPradesh_2023.csv" or "up_2023_jan.csv". Only used as a
# fallback when a file is missing StateName/year columns entirely.
FILENAME_PATTERN = re.compile(r"(?P<state>[A-Za-z]+)[_\-](?P<year>\d{4})", re.IGNORECASE)


# =============================== HELPERS ===================================

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        key = col.lower().strip()
        if key in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[key]
    return df.rename(columns=rename_map)


def backfill_state_year(df: pd.DataFrame, filepath: str) -> pd.DataFrame:
    match = FILENAME_PATTERN.search(os.path.basename(filepath))

    if "StateName" not in df.columns or df["StateName"].isna().all():
        if match:
            df["StateName"] = match.group("state")
        else:
            print(f"  [warn] Could not infer StateName for {os.path.basename(filepath)} "
                  f"— check FILENAME_PATTERN or fix this column manually.")

    if "year" not in df.columns or df["year"].isna().all():
        if match:
            df["year"] = int(match.group("year"))
        else:
            print(f"  [warn] Could not infer year for {os.path.basename(filepath)} "
                  f"— check FILENAME_PATTERN or fix this column manually.")

    return df


def load_one_file(filepath: str) -> pd.DataFrame:
    if filepath.endswith(".json"):
        df = pd.read_json(filepath)
    else:
        df = pd.read_csv(filepath, low_memory=False)

    df = standardize_columns(df)
    df = backfill_state_year(df, filepath)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        print(f"  [warn] {os.path.basename(filepath)} is missing expected columns: {missing}")

    return df


def pool_kcc_files(raw_dir: str) -> pd.DataFrame:
    files = sorted(
        glob.glob(os.path.join(raw_dir, "*.csv")) + glob.glob(os.path.join(raw_dir, "*.json"))
    )
    if not files:
        raise FileNotFoundError(
            f"No .csv or .json files found in '{raw_dir}'. "
            f"Drop your downloaded KCC exports there first, or update RAW_DATA_DIR."
        )

    print(f"Found {len(files)} files to pool.\n")

    frames = []
    for f in files:
        print(f"Loading {os.path.basename(f)} ...")
        try:
            frames.append(load_one_file(f))
        except Exception as e:
            print(f"  [error] Failed to load {f}: {e}")

    if not frames:
        raise RuntimeError("No files loaded successfully — check the [error] lines above.")

    pooled = pd.concat(frames, ignore_index=True, sort=False)

    before = len(pooled)
    pooled = pooled.drop_duplicates()
    after = len(pooled)
    print(f"\nPooled rows: {before:,} -> {after:,} after exact-duplicate removal "
          f"({before - after:,} dropped)")

    return pooled


def summarize(df: pd.DataFrame):
    print("\n--- Rows per state ---")
    if "StateName" in df.columns:
        print(df["StateName"].value_counts(dropna=False).to_string())

    print("\n--- Rows per year ---")
    if "year" in df.columns:
        print(df["year"].value_counts(dropna=False).sort_index().to_string())

    print("\n--- Rows per state x year (sanity-check coverage gaps here) ---")
    if {"StateName", "year"}.issubset(df.columns):
        print(df.groupby(["StateName", "year"]).size().unstack(fill_value=0).to_string())


# ================================= MAIN =====================================

if __name__ == "__main__":
    pooled_df = pool_kcc_files(RAW_DATA_DIR)
    summarize(pooled_df)

    pooled_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved consolidated dataset to '{OUTPUT_PATH}' ({len(pooled_df):,} rows).")
    print("Next: point KCC_PATH in farming_assistant_dataset_eda.py at this file and run the EDA pass.")