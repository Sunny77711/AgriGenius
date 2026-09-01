import pandas as pd
from sowing_time_weather_spotcheck import classify

def verify_data():
    print("Loading updated kcc_index_ready_final.csv...")
    df = pd.read_csv("kcc_index_ready_final.csv")
    
    subset = df[df["QueryType"] == "Sowing Time and Weather"].copy()
    total_remaining = len(subset)
    
    print("=" * 60)
    print(f"Total 'Sowing Time and Weather' rows remaining: {total_remaining:,}")
    print("=" * 60)
    
    if total_remaining == 0:
        print("❌ ERROR: 0 rows found. You may have accidentally dropped the entire category.")
        return

    # Re-classify the remaining rows
    subset["bucket"] = subset["KccAns"].astype(str).apply(classify)
    
    print("Current Bucket Distribution:")
    counts = subset["bucket"].value_counts()
    for bucket, count in counts.items():
        print(f"  {bucket:15s}: {count:,}")
        
    # Verification check
    has_weather = "weather_heavy" in counts.index and counts["weather_heavy"] > 0
    has_both = "both" in counts.index and counts["both"] > 0
    
    print("-" * 60)
    if not has_weather and not has_both:
        print("✅ SUCCESS: 'weather_heavy' and 'both' buckets were successfully completely removed!")
        print("You are ready to run kcc_build_index.py.")
    else:
        print("❌ ERROR: Some 'weather_heavy' or 'both' rows are still present. The filter did not apply correctly.")

if __name__ == "__main__":
    verify_data()