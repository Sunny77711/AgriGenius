"""
Multilingual Farming Assistant — Dataset EDA Toolkit
======================================================

Covers the three-dataset architecture:
  1. KCC            -> primary retrieval corpus (real content lives in KccAns, NOT QueryText)
  2. FarmerChat      -> supplementary KB / English-side QC layer
  3. AgriSci-QA      -> held-out evaluation benchmark (LIGHT TOUCH ONLY — never tune on it)

Usage:
    python farming_assistant_dataset_eda.py

Edit the CONFIG section below to point at your actual file paths, then run.
Each function prints a report to stdout and returns a dict/DataFrame you can
inspect further in a notebook.

Dependencies: pandas, numpy (both standard). No internet / no heavy ML libs
required for the core script — language ID here is done via Unicode script
ranges, which is fast and dependency-free. A note on upgrading this to true
language ID (script != language) is at the bottom.
"""

import re
import os
from collections import Counter

import numpy as np
import pandas as pd

pd.set_option("display.max_colwidth", 80)

# ============================== CONFIG ===================================

KCC_PATH = "kcc_pooled.csv"               # KCC export
FARMERCHAT_PATH = "farmerchat.csv"   # DigiGreen/farmerchat-queries export
AGRISCI_QA_PATH = "agrisci_qa.csv"   # AgriSci-QA export

# Adjust these if your loaded columns differ (e.g. after HF dataset -> csv export)
KCC_TEXT_COL = "KccAns"          # substantive content column
KCC_LABEL_COL = "QueryText"      # short English category label, NOT verbatim speech

FARMERCHAT_QUERY_COL = "query"     # adjust to actual column name
FARMERCHAT_ANSWER_COL = "answer"   # adjust to actual column name

AGRISCI_Q_COL = "question"
AGRISCI_A_COL = "answer"

SAMPLE_N = 50_000  # for expensive per-row ops on large KCC exports; set None to use all rows

# =========================== SCRIPT DETECTION =============================
# Unicode block ranges for major Indian scripts relevant to KCC's coverage.
# NOTE: script != language. Devanagari covers Hindi, Marathi, Nepali, Konkani,
# Sanskrit, etc. This layer tells you WHICH SCRIPT text is written in, which
# is enough to decide "is this native-script, Romanized, or English" — the
# key question for embedding-model choice. For script-to-language disambiguation
# see the note at the bottom of this file.

SCRIPT_RANGES = {
    "Devanagari": (0x0900, 0x097F),   # Hindi, Marathi, etc.
    "Bengali":    (0x0980, 0x09FF),
    "Gurmukhi":   (0x0A00, 0x0A7F),   # Punjabi
    "Gujarati":   (0x0A80, 0x0AFF),
    "Oriya":      (0x0B00, 0x0B7F),
    "Tamil":      (0x0B80, 0x0BFF),
    "Telugu":     (0x0C00, 0x0C7F),
    "Kannada":    (0x0C80, 0x0CFF),
    "Malayalam":  (0x0D00, 0x0D7F),
}

# Rough state -> primary language mapping, for the cross-check step.
# Not exhaustive — extend as needed for states present in your KCC export.
STATE_LANGUAGE_MAP = {
    "UTTAR PRADESH": "Devanagari", "MADHYA PRADESH": "Devanagari",
    "BIHAR": "Devanagari", "RAJASTHAN": "Devanagari", "HARYANA": "Devanagari",
    "MAHARASHTRA": "Devanagari", "CHHATTISGARH": "Devanagari",
    "WEST BENGAL": "Bengali",
    "PUNJAB": "Gurmukhi",
    "GUJARAT": "Gujarati",
    "ODISHA": "Oriya",
    "TAMIL NADU": "Tamil",
    "TELANGANA": "Telugu", "ANDHRA PRADESH": "Telugu",
    "KARNATAKA": "Kannada",
    "KERALA": "Malayalam",
}


def script_of_text(text: str) -> str:
    """Return the dominant script label for a piece of text."""
    if not isinstance(text, str) or not text.strip():
        return "EMPTY"
    counts = Counter()
    for ch in text:
        cp = ord(ch)
        if cp < 128 and ch.isalpha():
            counts["Latin"] += 1
            continue
        for script, (lo, hi) in SCRIPT_RANGES.items():
            if lo <= cp <= hi:
                counts[script] += 1
                break
    if not counts:
        return "OTHER/NUMERIC"
    # code-mixed if more than one script has meaningful presence
    total = sum(counts.values())
    dominant, dom_count = counts.most_common(1)[0]
    if len(counts) > 1 and (dom_count / total) < 0.85:
        return f"CODE-MIXED (dominant={dominant})"
    return dominant


# =============================== HELPERS ===================================

def basic_profile(df: pd.DataFrame, name: str) -> dict:
    print(f"\n{'='*70}\n{name} — basic profile\n{'='*70}")
    print(f"Rows: {len(df):,}  |  Columns: {len(df.columns)}")
    missing = (df.isna().mean() * 100).round(1).sort_values(ascending=False)
    print("\nMissing % by column:")
    print(missing[missing > 0].to_string() if (missing > 0).any() else "  none")
    dupes = df.duplicated().sum()
    print(f"\nExact duplicate rows: {dupes:,} ({dupes/len(df)*100:.1f}%)")
    return {"rows": len(df), "missing_pct": missing.to_dict(), "duplicates": dupes}


def categorical_summary(df: pd.DataFrame, cols: list, top_n: int = 10):
    for col in cols:
        if col not in df.columns:
            continue
        print(f"\n--- {col}: top {top_n} values (of {df[col].nunique()} unique) ---")
        vc = df[col].value_counts(dropna=False).head(top_n)
        for val, count in vc.items():
            print(f"  {str(val)[:40]:42s} {count:>8,} ({count/len(df)*100:5.1f}%)")


def text_length_stats(series: pd.Series, label: str):
    lengths = series.dropna().astype(str).str.split().str.len()
    print(f"\n--- {label} word-length distribution ---")
    print(lengths.describe(percentiles=[.1, .25, .5, .75, .9, .99]).round(1).to_string())


def duplicate_answer_analysis(series: pd.Series, label: str, top_n: int = 10):
    vc = series.dropna().value_counts()
    total = vc.sum()
    top = vc.head(top_n)
    print(f"\n--- {label}: most repeated exact answers ---")
    for text, count in top.items():
        preview = text[:70].replace("\n", " ")
        print(f"  x{count:<6,} ({count/total*100:4.1f}%)  {preview}...")
    boilerplate_share = top.sum() / total * 100
    print(f"\n  Top {top_n} answers account for {boilerplate_share:.1f}% of all non-null answers.")
    print(f"  Unique answers: {series.nunique():,} vs total non-null rows: {total:,} "
          f"(diversity ratio: {series.nunique()/total:.3f})")


def state_language_crosscheck(df: pd.DataFrame, state_col: str, text_col: str, sample_n=SAMPLE_N):
    sub = df[[state_col, text_col]].dropna()
    if sample_n and len(sub) > sample_n:
        sub = sub.sample(sample_n, random_state=42)
    sub = sub.copy()
    sub["detected_script"] = sub[text_col].astype(str).apply(script_of_text)
    sub["state_upper"] = sub[state_col].astype(str).str.upper().str.strip()
    sub["expected_script"] = sub["state_upper"].map(STATE_LANGUAGE_MAP)

    known = sub.dropna(subset=["expected_script"])
    if known.empty:
        print("\nNo states matched STATE_LANGUAGE_MAP — extend the map for your state coverage.")
        return
    match_mask = known["detected_script"].str.contains(known["expected_script"], na=False) \
        if False else known.apply(
            lambda r: r["expected_script"] in r["detected_script"], axis=1
        )
    match_rate = match_mask.mean() * 100
    print(f"\n--- State ↔ detected-script cross-check (n={len(known):,}) ---")
    print(f"Match rate (detected script contains expected script): {match_rate:.1f}%")
    print("Mismatches are not necessarily errors — could be code-switching, "
          "Romanized/transliterated text, or genuinely multilingual calls. Worth spot-checking.")


def leakage_check(eval_texts: pd.Series, corpus_texts: pd.Series, ngram=8, sample_n=2000):
    """
    Cheap verbatim-overlap check: for a sample of held-out eval texts, look for
    shared n-grams (word sequences) with the retrieval corpus. Any hits deserve
    manual review before you trust RQ1 results — leakage would let 'no-grounding'
    baselines appear artificially close to 'grounding' runs, or vice versa.
    """
    def ngrams(text, n):
        words = re.findall(r"\w+", str(text).lower())
        return set(tuple(words[i:i+n]) for i in range(max(0, len(words) - n + 1)))

    corpus_sample = corpus_texts.dropna().astype(str)
    if len(corpus_sample) > 20000:
        corpus_sample = corpus_sample.sample(20000, random_state=42)
    corpus_ngrams = set()
    for t in corpus_sample:
        corpus_ngrams |= ngrams(t, ngram)

    eval_sample = eval_texts.dropna().astype(str)
    if len(eval_sample) > sample_n:
        eval_sample = eval_sample.sample(sample_n, random_state=42)

    hits = 0
    for t in eval_sample:
        if ngrams(t, ngram) & corpus_ngrams:
            hits += 1

    print(f"\n--- Leakage check: AgriSci-QA vs retrieval corpus ({ngram}-word overlap) ---")
    print(f"Eval texts checked: {len(eval_sample):,}")
    print(f"Texts with a {ngram}-word verbatim overlap in corpus: {hits} "
          f"({hits/len(eval_sample)*100:.2f}%)")
    if hits > 0:
        print("  -> Manually inspect these — could indicate accidental leakage, "
              "or just common boilerplate/agricultural phrasing. Don't assume either way.")


# =============================== RUNNERS ===================================

def run_kcc_eda(path):
    if not os.path.exists(path):
        print(f"[skip] KCC file not found at {path} — update KCC_PATH in CONFIG.")
        return None
    df = pd.read_csv(path, low_memory=False)
    basic_profile(df, "KCC")

    categorical_summary(df, ["StateName", "Sector", "Crop", "Season", "QueryType", "Category"])

    text_length_stats(df[KCC_LABEL_COL], "QueryText (agent label — expect short & templated)")
    text_length_stats(df[KCC_TEXT_COL], "KccAns (the real content)")

    sample = df if SAMPLE_N is None else df.sample(min(SAMPLE_N, len(df)), random_state=42)
    script_counts = sample[KCC_TEXT_COL].astype(str).apply(script_of_text).value_counts()
    print("\n--- KccAns script distribution (sampled) ---")
    print(script_counts.to_string())

    duplicate_answer_analysis(df[KCC_TEXT_COL], "KccAns")

    if "StateName" in df.columns:
        state_language_crosscheck(df, "StateName", KCC_TEXT_COL)

    return df


def run_farmerchat_eda(path):
    if not os.path.exists(path):
        print(f"[skip] FarmerChat file not found at {path} — update FARMERCHAT_PATH in CONFIG.")
        return None
    df = pd.read_csv(path, low_memory=False)
    basic_profile(df, "FarmerChat")

    for col in (FARMERCHAT_QUERY_COL, FARMERCHAT_ANSWER_COL):
        if col in df.columns:
            sample = df if SAMPLE_N is None else df.sample(min(SAMPLE_N, len(df)), random_state=42)
            script_counts = sample[col].astype(str).apply(script_of_text).value_counts()
            print(f"\n--- FarmerChat[{col}] script distribution (confirming English-only) ---")
            print(script_counts.to_string())
            text_length_stats(df[col], f"FarmerChat[{col}]")

    return df


def run_agrisci_qa_eda(path, kcc_df=None, farmerchat_df=None):
    """Light structural pass only — do not use this to tune the retrieval index."""
    if not os.path.exists(path):
        print(f"[skip] AgriSci-QA file not found at {path} — update AGRISCI_QA_PATH in CONFIG.")
        return None
    df = pd.read_csv(path, low_memory=False)
    basic_profile(df, "AgriSci-QA (held-out — structure only, no content mining)")

    if AGRISCI_Q_COL in df.columns:
        text_length_stats(df[AGRISCI_Q_COL], "Question length")
    if AGRISCI_A_COL in df.columns:
        text_length_stats(df[AGRISCI_A_COL], "Answer length")

    # Leakage checks against your retrieval corpus + supplementary KB
    if kcc_df is not None and AGRISCI_A_COL in df.columns and KCC_TEXT_COL in kcc_df.columns:
        leakage_check(df[AGRISCI_A_COL], kcc_df[KCC_TEXT_COL])
    if farmerchat_df is not None and AGRISCI_A_COL in df.columns and FARMERCHAT_ANSWER_COL in farmerchat_df.columns:
        leakage_check(df[AGRISCI_A_COL], farmerchat_df[FARMERCHAT_ANSWER_COL])

    return df


# ================================= MAIN =====================================

if __name__ == "__main__":
    kcc_df = run_kcc_eda(KCC_PATH)
    farmerchat_df = run_farmerchat_eda(FARMERCHAT_PATH)
    agrisci_df = run_agrisci_qa_eda(AGRISCI_QA_PATH, kcc_df=kcc_df, farmerchat_df=farmerchat_df)

    print("\n" + "=" * 70)
    print("EDA pass complete. Suggested next steps once you've reviewed output:")
    print("  1. Decide chunking strategy for KccAns (per-answer vs merged-by-topic)")
    print("  2. Pick a multilingual embedding model based on the script distribution")
    print("     found above (e.g. MuRIL / IndicBERT for native-script-heavy corpora,")
    print("     LaBSE or multilingual-e5 if code-mixed/Romanized text dominates)")
    print("  3. Define the exact 'grounding vs no-grounding' protocol for RQ1")
    print("  4. Re-run leakage_check() after any corpus dedup to confirm it's still clean")

# -----------------------------------------------------------------------------
# NOTE on upgrading script detection to true language ID:
# Unicode-range detection tells you the SCRIPT, not the LANGUAGE (e.g. Devanagari
# is shared by Hindi/Marathi/Nepali/Konkani). If you need language-level (not
# script-level) granularity — e.g. to separate Hindi from Marathi — layer in
# AI4Bharat's IndicLID or fastText's lid.176 model on top of this script pass.
# Reserve that for text already flagged Devanagari/etc. here; running a heavy
# language-ID model on the full corpus first is unnecessary cost.
# -----------------------------------------------------------------------------