
import pandas as pd

df = pd.read_csv("network_features.csv")

print("\nNETWORK TRAFFIC STATISTICS")
print("============================")

print("\nTotal flows:", len(df))

print("\nProtocol distribution:")
print(df["protocol"].value_counts())

print("\nAverage packets per flow:")
print(
    (df["packets_sent"] + df["packets_received"]).mean()
)

print("\nAverage bytes per flow:")
print(
    (df["bytes_sent"] + df["bytes_received"]).mean()
)

print("\nAverage flow duration:")
print(df["duration"].mean(), "seconds")

print("\nSuricata alerted flows:")
print(df["alerted"].value_counts())

print("\nMost frequently used destination ports:")
print(df["destination_port"].value_counts().head(10))

print("\nAnalysis completed.")
