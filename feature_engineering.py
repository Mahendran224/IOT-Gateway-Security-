import pandas as pd

INPUT_FILE = "continuous_network_dataset.csv"
OUTPUT_FILE = "engineered_network_dataset.csv"

df = pd.read_csv(INPUT_FILE)

# Total packets
df["total_packets"] = (
    df["packets_sent"] + df["packets_received"]
)

# Total bytes
df["total_bytes"] = (
    df["bytes_sent"] + df["bytes_received"]
)

# Average packet size
df["average_packet_size"] = (
    df["total_bytes"] /
    df["total_packets"].replace(0, 1)
)

# Packets per second
df["packets_per_second"] = (
    df["total_packets"] /
    df["duration"].replace(0, 1)
)

# Bytes per second
df["bytes_per_second"] = (
    df["total_bytes"] /
    df["duration"].replace(0, 1)
)

df.to_csv(OUTPUT_FILE, index=False)

print("Feature engineering completed")
print("Total records:", len(df))
print("Total features:", len(df.columns))
print("\nNew features:")
print([
    "total_packets",
    "total_bytes",
    "average_packet_size",
    "packets_per_second",
    "bytes_per_second"
])

print("\nFeature preview:")
print(df[[
    "total_packets",
    "total_bytes",
    "average_packet_size",
    "packets_per_second",
    "bytes_per_second"
]].head())

print("\nSaved to:", OUTPUT_FILE)
