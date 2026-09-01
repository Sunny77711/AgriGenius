"""
sowing_time_weather_spotcheck.py

Manual review helper for the "Sowing Time and Weather" QueryType (13,174 rows) --
flagged in the original scoping decision as mixing evergreen crop-calendar
advice with time-sensitive weather forecast content. Still unresolved.

This does NOT auto-decide anything. It:
1. Buckets all "Sowing Time and Weather" rows into 4 heuristic categories using
   keyword matching (weather-forecast-like / sowing-calendar-like / both /
   neither), so you can see the overall shape of the category before reading
   any individual rows.
2. Prints a representative sample from each bucket, with crop/district/date
   metadata, so you can judge whether the content is genuinely time-sensitive.

Use the bucket sizes + printed samples to decide: keep the whole QueryType,
drop it entirely, or apply a rule (e.g. drop rows that read like dated
forecasts, keep rows that read like evergreen sowing advice).

Usage
-----
python sowing_time_weather_spotcheck.py
"""

import pandas as pd
import re

CSV_PATH = "kcc_index_ready_final.csv"
SAMPLES_PER_BUCKET = 4

WEATHER_KEYWORDS = [
    "मौसम विभाग", "पूर्वानुमान", "बारिश", "बादल", "तापमान", "आंशिक",
    "बूंदाबांदी", "वर्षा", "weather", "forecast", "rain", "temperature", "cloudy",
]
SOWING_KEYWORDS = [
    "बुवाई", "बोने", "बीज दर", "रोपाई", "बोआई", "sowing", "seed rate",
    "planting", "प्रजाति", "किस्म", "variety",
]

WEATHER_RE = re.compile("|".join(re.escape(k) for k in WEATHER_KEYWORDS), re.IGNORECASE)
SOWING_RE = re.compile("|".join(re.escape(k) for k in SOWING_KEYWORDS), re.IGNORECASE)


def classify(text):
    has_weather = bool(WEATHER_RE.search(text))
    has_sowing = bool(SOWING_RE.search(text))
    if has_weather and has_sowing:
        return "both"
    elif has_weather:
        return "weather_heavy"
    elif has_sowing:
        return "sowing_heavy"
    else:
        return "neither"


def main():
    print(f"Loading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH)
    subset = df[df["QueryType"] == "Sowing Time and Weather"].copy()
    print(f"'Sowing Time and Weather' rows: {len(subset):,} "
          f"({len(subset) / len(df) * 100:.2f}% of corpus)\n")

    if len(subset) == 0:
        print("No rows found -- check that QueryType values match exactly (see earlier repr() check).")
        return

    subset["bucket"] = subset["KccAns"].astype(str).apply(classify)

    print("=" * 100)
    print("BUCKET DISTRIBUTION (keyword heuristic -- read samples below before trusting this)")
    print("=" * 100)
    counts = subset["bucket"].value_counts()
    for bucket, count in counts.items():
        print(f"  {bucket:15s}: {count:,} ({count / len(subset) * 100:.1f}%)")
    print()

    bucket_descriptions = {
        "weather_heavy": "Reads like a dated weather forecast -- likely stale fast. "
                          "Candidate to DROP, or recency-cutoff like Government Schemes.",
        "sowing_heavy":  "Reads like evergreen sowing-time / crop-calendar advice -- likely safe to KEEP.",
        "both":          "Mixes both. Answers are short (median ~46 words), so splitting WITHIN a row "
                          "probably isn't practical -- this is a per-row keep-or-drop call.",
        "neither":       "Neither keyword set matched -- could be miscategorized, or phrased without "
                          "these specific keywords. Worth a closer look.",
    }

    for bucket in ["weather_heavy", "sowing_heavy", "both", "neither"]:
        bucket_rows = subset[subset["bucket"] == bucket]
        if len(bucket_rows) == 0:
            continue
        print("=" * 100)
        print(f"BUCKET: {bucket}  ({len(bucket_rows):,} rows)")
        print(bucket_descriptions[bucket])
        print("=" * 100)
        sample = bucket_rows.sample(n=min(SAMPLES_PER_BUCKET, len(bucket_rows)), random_state=1)
        for _, row in sample.iterrows():
            print("-" * 100)
            print(f"QueryText : {row['QueryText']}")
            print(f"Crop      : {row.get('Crop', '?')}  |  District: {row.get('DistrictName', '?')}  |  "
                  f"Date: {row.get('day', '?')}/{row.get('month', '?')}/{row.get('year', '?')}")
            print(f"KccAns    : {row['KccAns']}")
        print()

    print("=" * 100)
    print("DECISION GUIDE")
    print("=" * 100)
    print("- weather_heavy dominates and reads like dated forecasts -> drop the whole QueryType,")
    print("  same reasoning you already applied to the Weather category.")
    print("- sowing_heavy dominates and reads like generic crop-calendar advice -> keep as-is.")
    print("- genuine mix -> simplest defensible rule given short atomic answers is bucket-level")
    print("  keep/drop (e.g. drop weather_heavy + both, keep sowing_heavy), or a recency cutoff")
    print("  on weather_heavy rows only, mirroring what you did for Government Schemes.")
    print()
    print("Once decided, apply it as a filter on kcc_index_ready_final.csv, e.g.:")
    print('    drop_mask = (df["QueryType"] == "Sowing Time and Weather") & \\')
    print('                (df["KccAns"].astype(str).apply(classify) == "weather_heavy")')
    print('    df_final = df[~drop_mask]')
    print("before running the full-corpus embedding step.")


if __name__ == "__main__":
    main()