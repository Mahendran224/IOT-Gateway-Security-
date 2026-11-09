
import pandas as pd

df = pd.read_csv("network_features.csv")

df["total_packets"] = (
    df["packets_sent"] + df["packets_received"]
)

df["total_bytes"] = (
    df["bytes_sent"] + df["bytes_received"]
)

features = [
    "total_packets",
    "total_bytes",
    "duration"
]

print("\nNETWORK TRAFFIC BASELINE")
print("========================")

print("\nStatistical distribution:")
print(df[features].describe(
    percentiles=[0.50, 0.90, 0.95, 0.99]
).round(2))

print("\nAlerted versus non-alerted flows:")
print(
    df.groupby("alerted")[features]
    .agg(["count", "mean", "median", "max"])
    .round(2)
)

print("\nBaseline analysis completed.")
