import pandas as pd

# original big file
df = pd.read_csv("grocer_ai_data.csv", parse_dates=["date_time"])
print("Original rows:", len(df))

# keep only 10,000 rows from the last 1 year
df = df[df["date_time"] >= str(pd.Timestamp.now() - pd.Timedelta(days=365))]
df = df.sample(n=min(10000, len(df)), random_state=42)

# save smaller dataset
df.to_csv("grocer_ai_data_sample.csv", index=False)
print("Saved sample file with rows:", len(df))
