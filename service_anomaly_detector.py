
import pandas as pd

df = pd.read_csv("network_features.csv")

# Calculate total packets and bytes
df["total_packets"] = (
    df["packets_sent"] + df["packets_received"]
)

df["total_bytes"] = (
    df["bytes_sent"] + df["bytes_received"]
)

features = ["total_packets", "total_bytes", "duration"]

MIN_SERVICE_FLOWS = 10

# Calculate protocol-level thresholds
protocol_thresholds = {}

for protocol in df["protocol"].dropna().unique():

    data = df[df["protocol"] == protocol]

    protocol_thresholds[protocol] = {
        feature: data[feature].quantile(0.95)
        for feature in features
    }

# Calculate service-level thresholds
service_thresholds = {}

for (protocol, port), data in df.groupby(
    ["protocol", "destination_port"]
):

    if len(data) >= MIN_SERVICE_FLOWS:

        service_thresholds[(protocol, port)] = {
            feature: data[feature].quantile(0.95)
            for feature in features
        }

# Detect potential anomalies
def detect_anomaly(row):

    protocol = row["protocol"]
    port = row["destination_port"]

    service = (protocol, port)

    if service in service_thresholds:
        limits = service_thresholds[service]
        method = "Service-level"
    else:
        limits = protocol_thresholds.get(protocol)

        if limits is None:
            return pd.Series([False, "No threshold"])

        method = "Protocol-level fallback"

    flagged = any(
        row[feature] > limits[feature]
        for feature in features
    )

    return pd.Series([flagged, method])


df[["potential_anomaly", "detection_method"]] = df.apply(
    detect_anomaly,
    axis=1
)

# Display results
anomalies = df[df["potential_anomaly"]]

print("\nSERVICE-AWARE ANOMALY DETECTION")
print("================================")

print("Total flows:", len(df))
print("Potential anomalies:", len(anomalies))

print("\nDetection methods:")

print(df["detection_method"].value_counts())

print("\nPotential anomaly details:")

columns = [
    "source_ip",
    "destination_ip",
    "destination_port",
    "protocol",
    "total_packets",
    "total_bytes",
    "duration",
    "alerted",
    "detection_method"
]

print(anomalies[columns].to_string(index=False))

# Save results
df.to_csv("service_anomaly_results.csv", index=False)

print("\nSaved: service_anomaly_results.csv")
print("Analysis completed.")
