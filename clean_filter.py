"""
KCC Cleaning & Filtering Script
=================================
Takes the pooled KCC dataset (output of kcc_pool_datasets.py) and applies
the filtering decisions from the EDA pass:

  - Fixes whitespace bugs in categorical columns (e.g. "  Plant Protection")
  - Drops the Season column (100% missing in this export)
  - Drops empty/near-empty KccAns rows
  - Flags and drops rows with corrupted-looking Sector values (numeric
    codes where a category name should be — likely a parsing/column-shift
    artifact, not real sector data)
  - Excludes time-decaying QueryTypes (Weather) from the retrieval corpus
  - Applies a recency cutoff to Government Schemes queries specifically,
    since scheme details (installment numbers, KYC deadlines, etc.) go
    stale much faster than general agronomic advice
  - Collapses exact-duplicate KccAns text into one representative entry
    per unique answer (keeping the most recent occurrence), so the index
    doesn't carry hundreds of copies of the same PM-KISAN boilerplate

Run this AFTER kcc_pool_datasets.py and the EDA pass. Adjust the CONFIG
block below based on what your own EDA output shows.
"""

import re
import pandas as pd

# ============================== CONFIG ===================================

INPUT_PATH = "kcc_pooled.csv"
OUTPUT_PATH = "kcc_index_ready.csv"

MIN_ANSWER_WORDS = 3                     # drop KccAns shorter than this
EXCLUDE_QUERY_TYPES = ["Weather"]        # time-decaying — excluded outright
REVIEW_QUERY_TYPES = ["Sowing Time and Weather"]  # mixed content — flagged, not auto-dropped
SCHEME_QUERY_TYPES = ["Government Schemes"]        # gets a recency cutoff, not exclusion
NUMERIC_SECTOR_PATTERN = re.compile(r"^\d+$")


# =============================== STEPS ===================================

def load(path):
    df = pd.read_csv(path, low_memory=False)
    print(f"Loaded {len(df):,} rows, {len(df.columns)} columns.")
    return df


def strip_whitespace(df):
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip().replace({"nan": pd.NA})
    print(f"Stripped whitespace on {len(str_cols)} text columns.")
    return df


def drop_empty_season(df):
    if "Season" in df.columns:
        missing_pct = df["Season"].isna().mean() * 100
        if missing_pct > 95:
            df = df.drop(columns=["Season"])
            print(f"Dropped 'Season' column ({missing_pct:.1f}% missing — unusable).")
    return df


def filter_empty_answers(df):
    before = len(df)
    word_count = df["KccAns"].fillna("").str.split().str.len()
    df = df[word_count >= MIN_ANSWER_WORDS].copy()
    print(f"Dropped {before - len(df):,} rows with KccAns under {MIN_ANSWER_WORDS} words "
          f"({before:,} -> {len(df):,}).")
    return df


def filter_corrupted_sector(df):
    if "Sector" not in df.columns:
        return df
    is_numeric = df["Sector"].astype(str).str.match(NUMERIC_SECTOR_PATTERN, na=False)
    n_bad = int(is_numeric.sum())
    if n_bad:
        print(f"Found {n_bad:,} rows with numeric-looking Sector values "
              f"(likely corrupted/shifted columns) — sample below, inspect before trusting this filter:")
        cols = [c for c in ["Sector", "QueryType", "Category", "KccAns"] if c in df.columns]
        print(df.loc[is_numeric, cols].head(3).to_string())
        df = df[~is_numeric].copy()
        print(f"Dropped {n_bad:,} rows with corrupted Sector values.")
    return df


def exclude_query_types(df):
    before = len(df)
    df = df[~df["QueryType"].isin(EXCLUDE_QUERY_TYPES)].copy()
    print(f"Excluded QueryTypes {EXCLUDE_QUERY_TYPES}: {before - len(df):,} rows dropped "
          f"({before:,} -> {len(df):,}).")
    present_types = df["QueryType"].dropna().unique().tolist()
    present_review = [q for q in REVIEW_QUERY_TYPES if q in present_types]
    if present_review:
        print(f"[review] These QueryTypes mix evergreen + time-sensitive content — "
              f"decide manually whether to keep, split, or drop: {present_review}")
    return df


def apply_scheme_recency_cutoff(df):
    if "year" not in df.columns:
        return df
    latest_year = df["year"].max()
    is_scheme = df["QueryType"].isin(SCHEME_QUERY_TYPES)
    before = int(is_scheme.sum())
    drop_mask = is_scheme & (df["year"] < latest_year)
    n_dropped = int(drop_mask.sum())
    df = df[~drop_mask].copy()
    print(f"Government-Schemes recency cutoff: kept only year={latest_year} for scheme queries "
          f"— dropped {n_dropped:,} of {before:,} scheme rows from earlier years "
          f"(scheme details like installment numbers and KYC deadlines go stale fast).")
    return df


def collapse_duplicate_answers(df):
    before = len(df)

    if "CreatedOn" in df.columns:
        df["_sort_dt"] = pd.to_datetime(df["CreatedOn"], errors="coerce")
    elif {"year", "month", "day"}.issubset(df.columns):
        date_str = (
            df["year"].astype("Int64").astype(str) + "-" +
            df["month"].astype("Int64").astype(str) + "-" +
            df["day"].astype("Int64").astype(str)
        )
        df["_sort_dt"] = pd.to_datetime(date_str, errors="coerce")
    else:
        df["_sort_dt"] = pd.NaT

    df = df.sort_values("_sort_dt", ascending=False, na_position="last")
    dup_counts = df.groupby("KccAns")["KccAns"].transform("count")
    df["duplicate_call_count"] = dup_counts
    df = df.drop_duplicates(subset="KccAns", keep="first").drop(columns=["_sort_dt"]).copy()

    print(f"Collapsed exact-duplicate KccAns text (kept most recent occurrence of each): "
          f"{before:,} -> {len(df):,} rows.")
    return df


# ================================= MAIN =====================================

if __name__ == "__main__":
    df = load(INPUT_PATH)
    df = strip_whitespace(df)
    df = drop_empty_season(df)
    df = filter_empty_answers(df)
    df = filter_corrupted_sector(df)
    df = exclude_query_types(df)
    df = apply_scheme_recency_cutoff(df)
    df = collapse_duplicate_answers(df)

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved retrieval-ready corpus to '{OUTPUT_PATH}' ({len(df):,} rows).")
    print("Next: build embeddings over KccAns and index into FAISS/Chroma.")