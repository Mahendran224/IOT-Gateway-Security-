
import pandas as pd

df = pd.read_csv("service_anomaly_results.csv")

def classify(row):

    if not row["potential_anomaly"]:
        return "NORMAL_BASELINE"

    protocol = row["protocol"]
    port = row["destination_port"]

    # Use the same threshold selection as Version 3
    group = df[
        (df["protocol"] == protocol) &
        (df["destination_port"] == port)
    ]

    if (
        row["detection_method"] == "Service-level"
        and len(group) >= 10
    ):
        reference = group
    else:
        reference = df[df["protocol"] == protocol]

    reasons = []

    for feature, label in [
        ("total_packets", "HIGH_PACKET_COUNT"),
        ("total_bytes", "HIGH_BYTE_COUNT"),
        ("duration", "LONG_DURATION")
    ]:

        threshold = reference[feature].quantile(0.95)

        if row[feature] > threshold:
            reasons.append(label)

    if len(reasons) > 1:
        return "MULTIPLE_FEATURES: " + ", ".join(reasons)

    if reasons:
        return reasons[0]

    return "REQUIRES_REVIEW"


df["anomaly_reason"] = df.apply(classify, axis=1)

print("\nANOMALY CLASSIFICATION REPORT")
print("==============================")

print("\nClassification counts:")
print(df["anomaly_reason"].value_counts().to_string())

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
    "anomaly_reason"
]

print(
    df[df["potential_anomaly"]][columns].to_string(index=False)
)

df.to_csv("classified_anomalies.csv", index=False)

print("\nSaved: classified_anomalies.csv")
print("Classification completed.")
