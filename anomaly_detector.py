
import pandas as pd

df = pd.read_csv("network_features.csv")

df["total_packets"] = (
    df["packets_sent"] + df["packets_received"]
)

df["total_bytes"] = (
    df["bytes_sent"] + df["bytes_received"]
)

# Calculate preliminary 95th percentile thresholds
packet_limit = df["total_packets"].quantile(0.95)
byte_limit = df["total_bytes"].quantile(0.95)
duration_limit = df["duration"].quantile(0.95)

print("\nNETWORK ANOMALY DETECTOR")
print("========================")

print("\nThresholds:")
print("Packet threshold:", packet_limit)
print("Byte threshold:", byte_limit)
print("Duration threshold:", duration_limit)

# Flag flows exceeding any threshold
df["anomaly"] = (
    (df["total_packets"] > packet_limit) |
    (df["total_bytes"] > byte_limit) |
    (df["duration"] > duration_limit)
)

anomalies = df[df["anomaly"]]

print("\nTotal flows:", len(df))
print("Potential anomalies:", len(anomalies))

print("\nPotential anomalous flows:")

print(
    anomalies[
        [
            "source_ip",
            "destination_ip",
            "destination_port",
            "protocol",
            "total_packets",
            "total_bytes",
            "duration",
            "alerted"
        ]
    ].to_string(index=False)
)

df.to_csv("network_anomaly_results.csv", index=False)

print("\nResults saved to network_anomaly_results.csv")
