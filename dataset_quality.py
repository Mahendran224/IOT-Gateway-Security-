import pandas as pd

FILE = "continuous_network_dataset.csv"

df = pd.read_csv(FILE)

print("\n========== DATASET OVERVIEW ==========")
print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("\nColumns:")
print(df.columns.tolist())

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATE RECORDS ==========")
print("Duplicates:", df.duplicated().sum())

print("\n========== PROTOCOL DISTRIBUTION ==========")
print(df["protocol"].value_counts())

print("\n========== ALERT DISTRIBUTION ==========")
print(df["alerted"].value_counts())

print("\n========== NUMERICAL STATISTICS ==========")
print(df[
    [
        "packets_sent",
        "packets_received",
        "bytes_sent",
        "bytes_received",
        "duration"
    ]
].describe())

print("\n========== DATASET QUALITY CHECK COMPLETED ==========")
