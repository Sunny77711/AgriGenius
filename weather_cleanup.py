import pandas as pd
from sowing_time_weather_spotcheck import classify

# Load the dataset
df = pd.read_csv("kcc_index_ready_final.csv")

# Identify the relevant category
is_sowing_weather = df["QueryType"] == "Sowing Time and Weather"

# Apply the classification heuristic only to this subset
classifications = df.loc[is_sowing_weather, "KccAns"].astype(str).apply(classify)

# Create a mask to drop both weather-heavy and mixed rows
drop_mask = is_sowing_weather & (classifications.isin(["weather_heavy", "both"]))

# Filter the dataframe to keep only evergreen data
df_final = df[~drop_mask]

# Overwrite the final file for ChromaDB ingestion
df_final.to_csv("kcc_index_ready_final.csv", index=False)