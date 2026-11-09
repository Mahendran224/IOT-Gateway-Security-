import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

df = pd.read_csv("network_flow_ml.csv")

# Behaviour-based features
features = pd.DataFrame(index=df.index)

features["log_packets"] = np.log1p(df["total_packets"])
features["log_bytes"] = np.log1p(df["total_bytes"])
features["log_duration"] = np.log1p(df["duration_seconds"])

features["log_average_packet_size"] = np.log1p(
    df["total_bytes"] / df["total_packets"].clip(lower=1)
)

features["packet_direction_balance"] = np.log(
    (df["packets_sent"] + 1) /
    (df["packets_received"] + 1)
)

features["byte_direction_balance"] = np.log(
    (df["bytes_sent"] + 1) /
    (df["bytes_received"] + 1)
)

features = features.replace([np.inf, -np.inf], np.nan)
features = features.fillna(features.median())

# Isolation Forest
model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)

predictions = model.fit_predict(features)

df["anomaly_candidate"] = predictions == -1
df["anomaly_score"] = -model.decision_function(features)

df.to_csv("network_anomaly_results_v4.csv", index=False)

print("\nISOLATION FOREST VERSION 4")
print("Total flows:", len(df))
print("Features:", len(features.columns))
print("Anomaly candidates:", df["anomaly_candidate"].sum())
print("Normal outputs:", (~df["anomaly_candidate"]).sum())

print("\nAPPLICATION PROTOCOL DISTRIBUTION")
print(pd.crosstab(
    df["app_protocol"].fillna("UNKNOWN"),
    df["anomaly_candidate"]
))

print("\nPROTOCOL DISTRIBUTION")
print(pd.crosstab(
    df["protocol"],
    df["anomaly_candidate"]
))

print("\nTOP 15 ANOMALY CANDIDATES")
print(
    df.nlargest(15, "anomaly_score")[[
        "event_id", "protocol", "app_protocol",
        "total_packets", "total_bytes",
        "duration_seconds", "anomaly_score"
    ]].to_string(index=False)
)

print("\nSaved: network_anomaly_results_v4.csv")
