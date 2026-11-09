
import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import IsolationForest

# 1. Load network-flow dataset
df = pd.read_csv("network_flow_ml.csv")

# 2. Select network-security features
numeric_features = [
    "packets_sent",
    "packets_received",
    "total_packets",
    "bytes_sent",
    "bytes_received",
    "total_bytes",
    "duration_seconds"
]

categorical_features = [
    "protocol",
    "app_protocol",
    "connection_state"
]

tcp_features = [
    "tcp_syn",
    "tcp_ack",
    "tcp_fin",
    "tcp_rst"
]

# 3. Prepare numerical features
numeric_data = df[numeric_features].copy()

for col in numeric_features:
    numeric_data[col] = pd.to_numeric(
        numeric_data[col], errors="coerce"
    )

    # Preserve missing-value information
    numeric_data[col + "_missing"] = (
        numeric_data[col].isna().astype(int)
    )

    numeric_data[col] = numeric_data[col].fillna(
        numeric_data[col].median()
    )

    # Reduce the effect of highly skewed traffic values
    numeric_data[col] = np.log1p(
        numeric_data[col].clip(lower=0)
    )

# 4. Prepare TCP flags
tcp_data = df[tcp_features].copy()

for col in tcp_features:
    tcp_data[col + "_missing"] = (
        tcp_data[col].isna().astype(int)
    )

    tcp_data[col] = tcp_data[col].map({
        True: 1,
        False: 0,
        1: 1,
        0: 0
    })

    tcp_data[col] = tcp_data[col].fillna(-1)

# 5. Prepare categorical features
categorical_data = df[categorical_features].copy()
categorical_data = categorical_data.fillna("UNKNOWN")

categorical_data = pd.get_dummies(
    categorical_data,
    dtype=int
)

# 6. Combine features
X = pd.concat(
    [numeric_data, tcp_data, categorical_data],
    axis=1
)

# 7. Train Isolation Forest
model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42
)

model.fit(X)

# 8. Identify unusual network flows
predictions = model.predict(X)

anomaly_scores = -model.decision_function(X)

# -1 = unusual flow, 1 = normal flow
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

results["anomaly_score"] = anomaly_scores
results["anomaly_candidate"] = (
    predictions == -1
)

# 9. Save results separately
results.to_csv(
    "network_anomaly_results.csv",
    index=False
)

# Save model and feature structure
joblib.dump(
    {
        "model": model,
        "feature_columns": X.columns.tolist()
    },
    "network_anomaly_model.joblib"
)

# 10. Display summary
print("\nISOLATION FOREST MODEL COMPLETED")

print("Total flows:", len(results))
print("Features used:", X.shape[1])

print(
    "Anomaly candidates:",
    int((predictions == -1).sum())
)

print(
    "Normal flows:",
    int((predictions == 1).sum())
)

print("\nTOP 10 ANOMALY CANDIDATES:")

print(
    results.sort_values(
        "anomaly_score",
        ascending=False
    ).head(10).to_string(index=False)
)

print("\nFiles created:")
print("1. network_anomaly_results.csv")
print("2. network_anomaly_model.joblib")

print("\nNote: Anomaly candidates are not confirmed attacks.")
