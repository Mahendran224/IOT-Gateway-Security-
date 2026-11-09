
import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import IsolationForest

# 1. Load dataset
df = pd.read_csv("network_flow_ml.csv")

# 2. Engineer network features
X = pd.DataFrame(index=df.index)

X["log_total_packets"] = np.log1p(
    df["total_packets"].clip(lower=0)
)

X["log_duration"] = np.log1p(
    df["duration_seconds"].clip(lower=0)
)

X["log_average_packet_size"] = np.log1p(
    df["total_bytes"] /
    df["total_packets"].clip(lower=1)
)

# Signed log ratios preserve direction information
X["packet_direction_balance"] = np.log(
    (df["packets_sent"] + 1) /
    (df["packets_received"] + 1)
)

X["byte_direction_balance"] = np.log(
    (df["bytes_sent"] + 1) /
    (df["bytes_received"] + 1)
)

# 3. Handle invalid values
X = X.replace([np.inf, -np.inf], np.nan)
X = X.fillna(X.median())

# 4. Train Isolation Forest
model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42
)

model.fit(X)

# 5. Generate anomaly assessments
predictions = model.predict(X)
scores = -model.decision_function(X)

# 6. Prepare results
results = df[
    [
        "event_id",
        "timestamp",
        "flow_id",
        "src_ip",
        "dest_ip",
        "protocol",
        "app_protocol",
        "total_packets",
        "total_bytes",
        "duration_seconds"
    ]
].copy()

results["anomaly_score"] = scores
results["anomaly_candidate"] = predictions == -1

# 7. Save results separately
results.to_csv(
    "network_anomaly_results_v3.csv",
    index=False
)

joblib.dump(
    {
        "model": model,
        "feature_columns": X.columns.tolist()
    },
    "network_anomaly_model_v3.joblib"
)

# 8. Display model results
print("\nISOLATION FOREST VERSION 3")

print("Total flows:", len(results))
print("Features used:", X.shape[1])

print(
    "Anomaly candidates:",
    int((predictions == -1).sum())
)

print(
    "Normal outputs:",
    int((predictions == 1).sum())
)

print("\nAPPLICATION PROTOCOL DISTRIBUTION")

print(
    pd.crosstab(
        results["app_protocol"].fillna("UNKNOWN"),
        results["anomaly_candidate"]
    )
)

print("\nPROTOCOL DISTRIBUTION")

print(
    pd.crosstab(
        results["protocol"],
        results["anomaly_candidate"]
    )
)

print("\nTOP 10 ANOMALY CANDIDATES")

print(
    results.nlargest(10, "anomaly_score")[
        [
            "event_id",
            "protocol",
            "app_protocol",
            "total_packets",
            "total_bytes",
            "duration_seconds",
            "anomaly_score"
        ]
    ].to_string(index=False)
)

print("\nSaved:")
print("network_anomaly_results_v3.csv")
print("network_anomaly_model_v3.joblib")

print("\nAnomaly candidates are not confirmed attacks.")

