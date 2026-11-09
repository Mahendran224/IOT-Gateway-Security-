import pandas as pd

INPUT_FILE = "engineered_network_dataset.csv"
OUTPUT_FILE = "protocol_anomaly_results.csv"

df = pd.read_csv(INPUT_FILE)

features = [
    "total_packets",
    "total_bytes",
    "duration"
]

df["potential_anomaly"] = False
df["anomaly_reason"] = ""

print("Protocol-aware anomaly detection started")

for protocol in df["protocol"].unique():

    protocol_data = df[df["protocol"] == protocol]

    thresholds = {}

    print("\nProtocol:", protocol)
    print("Number of flows:", len(protocol_data))

    for feature in features:
        threshold = protocol_data[feature].quantile(0.95)
        thresholds[feature] = threshold
        print(f"{feature} 95th percentile:", threshold)

    for index in protocol_data.index:

        reasons = []

        for feature in features:
            if df.loc[index, feature] > thresholds[feature]:
                reasons.append("HIGH_" + feature.upper())

        if reasons:
            df.loc[index, "potential_anomaly"] = True
            df.loc[index, "anomaly_reason"] = ", ".join(reasons)

print("\n========== DETECTION SUMMARY ==========")

print("Total flows:", len(df))
print("Potential anomalies:", df["potential_anomaly"].sum())
print("Other flows:", (~df["potential_anomaly"]).sum())

df.to_csv(OUTPUT_FILE, index=False)

print("\nResults saved to:", OUTPUT_FILE)
