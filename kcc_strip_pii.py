"""
kcc_strip_pii.py

Drops the ~1,691 rows flagged by data_quality_recheck.py's PII scan
(registration numbers, "Name of Farmer" labels, phone numbers, address
labels in KccAns) and writes the final corpus ready for embedding.

No "weather leakage" fix is included here -- that check turned out to be a
false alarm (see analysis): QueryType=="Weather" rows were already correctly
excluded upstream; the wide 'weather' substring hits in QueryText are just
noisy free-text labeling that doesn't touch KccAns content, so nothing to
strip on that front.

Usage
-----
python kcc_strip_pii.py
"""

import pandas as pd
import re

INPUT_PATH = "kcc_index_ready.csv"
OUTPUT_PATH = "kcc_index_ready_final.csv"

PII_PATTERNS = {
    "registration_number": re.compile(r"registration\s*(no\.?|number)", re.IGNORECASE),
    "farmer_name_label": re.compile(r"name\s+of\s+farmer", re.IGNORECASE),
    "phone_number": re.compile(r"\b[6-9]\d{9}\b"),
    "address_label": re.compile(r"\baddress\b", re.IGNORECASE),
}


def main():
    print(f"Loading {INPUT_PATH} ...")
    df = pd.read_csv(INPUT_PATH)
    n_before = len(df)
    print(f"Loaded {n_before:,} rows.")

    kcc_ans = df["KccAns"].astype(str)
    flagged = pd.Series(False, index=df.index)
    for label, pattern in PII_PATTERNS.items():
        mask = kcc_ans.str.contains(pattern, na=False, regex=True)
        print(f"  {label:22s}: {mask.sum():,} rows flagged")
        flagged |= mask

    print(f"\nTotal flagged: {flagged.sum():,} ({flagged.sum() / n_before * 100:.3f}% of corpus)")

    df_clean = df[~flagged].reset_index(drop=True)
    n_after = len(df_clean)
    print(f"Dropping flagged rows: {n_before:,} -> {n_after:,} rows "
          f"({n_before - n_after:,} removed)")

    df_clean.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved final corpus to {OUTPUT_PATH}")
    print("This is the file to use for the full embedding + ChromaDB indexing step.")


if __name__ == "__main__":
    main()