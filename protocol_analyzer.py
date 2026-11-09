
import pandas as pd

df = pd.read_csv("network_features.csv")

# Calculate total traffic per flow
df["total_packets"] = (
    df["packets_sent"] + df["packets_received"]
)

df["total_bytes"] = (
    df["bytes_sent"] + df["bytes_received"]
)

features = ["total_packets", "total_bytes", "duration"]

print("\nPROTOCOL-AWARE NETWORK ANALYSIS")
print("================================")

# Calculate separate thresholds for each protocol
thresholds = {}

for protocol in df["protocol"].dropna().unique():

    protocol_data = df[df["protocol"] == protocol]

    thresholds[protocol] = {}

    for feature in features:
        thresholds[protocol][feature] = (
            protocol_data[feature].quantile(0.95)
        )

    print("\nProtocol:", protocol)
    print("Number of flows:", len(protocol_data))

    for feature in features:
        print(
            feature,
            "95th percentile:",
            round(thresholds[protocol][feature], 2)
        )

# Flag flows exceeding their own protocol thresholds
def detect_anomaly(row):

    protocol = row["protocol"]

    if protocol not in thresholds:
        return False

    limits = thresholds[protocol]

    return any(
        row[feature] > limits[feature]
        for feature in features
    )

df["protocol_anomaly"] = df.apply(
    detect_anomaly, axis=1
)

anomalies = df[df["protocol_anomaly"]]

print("\nPROTOCOL-AWARE DETECTION RESULTS")
print("================================")
print("Total flows:", len(df))
print("Potential anomalies:", len(anomalies))

print("\nDetected flows:")

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

df.to_csv("protocol_anomaly_results.csv", index=False)

print("\nSaved: protocol_anomaly_results.csv")
print("Analysis completed.")
