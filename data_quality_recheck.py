"""
data_quality_recheck.py

Two checks on kcc_index_ready.csv, prompted by the qualitative retrieval run:

1. WEATHER LEAKAGE
   kcc_clean_and_filter.py is supposed to have dropped all Weather QueryType
   rows (161,926 of them, per the original run log). But a random sample of
   the "cleaned" file just surfaced QueryText == "Farmer asked query on
   Weather" in 40% of a 15-row sample -- far too high for that to be residual
   noise. This checks how many such rows remain and what QueryType they
   actually carry, to pin down whether it's a whitespace/casing mismatch
   (same root cause as the earlier QueryType leading-whitespace bug) or
   something else.

2. PII SCAN
   One retrieved candidate in the qualitative check was literally a farmer's
   name, village address, and government registration number sitting inside
   KccAns. This does a lightweight regex/keyword scan to estimate how common
   that is, so you can decide whether to strip specific rows or fields before
   this becomes a public-facing/portfolio artifact.

Usage
-----
python data_quality_recheck.py
"""

import pandas as pd
import re

CSV_PATH = "kcc_index_ready.csv"

# --- PII patterns -----------------------------------------------------------
PII_PATTERNS = {
    "registration_number": re.compile(r"registration\s*(no\.?|number)", re.IGNORECASE),
    "farmer_name_label": re.compile(r"name\s+of\s+farmer", re.IGNORECASE),
    "phone_number": re.compile(r"\b[6-9]\d{9}\b"),  # Indian 10-digit mobile pattern
    "address_label": re.compile(r"\baddress\b", re.IGNORECASE),
}


def main():
    print(f"Loading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows.\n")

    # --- 1. Weather leakage check -------------------------------------------
    print("=" * 100)
    print("WEATHER LEAKAGE CHECK")
    print("=" * 100)

    weather_query_mask = df["QueryText"].astype(str).str.contains("weather", case=False, na=False)
    weather_rows = df[weather_query_mask]
    print(f"Rows where QueryText mentions 'weather' (case-insensitive): {len(weather_rows):,} "
          f"({len(weather_rows) / len(df) * 100:.2f}% of corpus)\n")

    if len(weather_rows):
        print("QueryType breakdown for these rows (this tells you WHY they survived the filter):")
        print(weather_rows["QueryType"].value_counts(dropna=False).to_string())
        print()

        # Specifically check for whitespace/casing variants of "Weather" hiding in QueryType
        all_query_types = df["QueryType"].dropna().unique().tolist()
        weather_like_types = [q for q in all_query_types if "weather" in str(q).lower()]
        print(f"Distinct QueryType values containing 'weather' (repr'd to expose whitespace): "
              f"{[repr(q) for q in weather_like_types]}")
    else:
        print("No weather leakage detected by this check.")

    print()

    # --- 2. PII scan ---------------------------------------------------------
    print("=" * 100)
    print("PII SCAN (on KccAns)")
    print("=" * 100)

    kcc_ans = df["KccAns"].astype(str)
    total_flagged = pd.Series(False, index=df.index)

    for label, pattern in PII_PATTERNS.items():
        mask = kcc_ans.str.contains(pattern, na=False)
        count = mask.sum()
        total_flagged |= mask
        print(f"  {label:22s}: {count:,} rows ({count / len(df) * 100:.3f}%)")

    print(f"\nTotal rows flagged by at least one PII pattern: {total_flagged.sum():,} "
          f"({total_flagged.sum() / len(df) * 100:.3f}%)")

    if total_flagged.sum():
        print("\nSample flagged rows:")
        sample = df[total_flagged].sample(n=min(5, total_flagged.sum()), random_state=1)
        for _, row in sample.iterrows():
            print("-" * 100)
            print(f"KCCCallID: {row.get('KCCCallID', '?')}")
            print(f"KccAns   : {str(row['KccAns'])[:200]}")

    print("\nDone. Use these results to decide: fix the Weather filter logic, and either")
    print("drop PII-flagged rows or strip the offending substrings before re-running")
    print("kcc_clean_and_filter.py and regenerating kcc_index_ready.csv.")


if __name__ == "__main__":
    main()