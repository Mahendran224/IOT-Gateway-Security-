
import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import IsolationForest

# 1. Load dataset
df = pd.read_csv("network_flow_ml.csv")

# 2. Use numerical network traffic features only
features = [
    "packets_sent",
    "packets_received",
    "total_packets",
    "bytes_sent",
    "bytes_received",
    "total_bytes",
    "duration_seconds"
]

X = df[features].copy()

# 3. Handle missing numerical values
for col in features:
    X[col] = pd.to_numeric(X[col], errors="coerce")
    X[col] = X[col].fillna(X[col].median())

# 4. Apply logarithmic transformation
X = np.log1p(X.clip(lower=0))

# 5. Train Isolation Forest
model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42
)

model.fit(X)

# 6. Predict unusual flows
predictions = model.predict(X)
scores = -model.decision_function(X)

# 7. Prepare separate results
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

# 8. Save results
results.to_csv(
    "network_anomaly_results_v2.csv",
    index=False
)

joblib.dump(
    {
        "model": model,
        "feature_columns": features
    },
    "network_anomaly_model_v2.joblib"
)

# 9. Display summary
print("\nISOLATION FOREST VERSION 2")

print("Total flows:", len(results))
print("Numerical features:", len(features))

print(
    "Anomaly candidates:",
    int((predictions == -1).sum())
)

print(
    "Normal flows:",
    int((predictions == 1).sum())
)

print("\nAPPLICATION PROTOCOL DISTRIBUTION")

print(
    pd.crosstab(
        results["app_protocol"].fillna("UNKNOWN"),
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
print("network_anomaly_results_v2.csv")
print("network_anomaly_model_v2.joblib")

print("\nAnomaly candidates are not confirmed attacks.")
