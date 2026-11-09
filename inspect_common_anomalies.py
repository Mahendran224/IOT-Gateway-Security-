import pandas as pd

df = pd.read_csv("network_flow_ml.csv")

v1 = pd.read_csv("network_anomaly_results.csv")
v2 = pd.read_csv("network_anomaly_results_v2.csv")
v3 = pd.read_csv("network_anomaly_results_v3.csv")

sets = []

for data in [v1, v2, v3]:
    ids = set(
        data.loc[data["anomaly_candidate"], "event_id"]
    )
    sets.append(ids)

common = sets[0] & sets[1] & sets[2]

result = df[df["event_id"].isin(common)].copy()

print("\nCOMMON ANOMALY CANDIDATES:", len(result))

print("\nAPPLICATION PROTOCOLS")
print(result["app_protocol"].value_counts(dropna=False))

print("\nNETWORK PROTOCOLS")
print(result["protocol"].value_counts(dropna=False))

print("\nCONNECTION STATES")
print(result["connection_state"].value_counts(dropna=False))

print("\nTOP SOURCE IP ADDRESSES")
print(result["src_ip"].value_counts().head(10))

print("\nTOP DESTINATION IP ADDRESSES")
print(result["dest_ip"].value_counts().head(10))

print("\nTRAFFIC SUMMARY")
print(result[
    ["total_packets", "total_bytes", "duration_seconds"]
].describe().round(2))

print("\nTOP 20 COMMON CANDIDATES")
print(
    result.sort_values(
        "total_bytes", ascending=False
    )[[
        "event_id", "src_ip", "dest_ip",
        "protocol", "app_protocol",
        "total_packets", "total_bytes",
        "duration_seconds", "alerted"
    ]].head(20).to_string(index=False)
)

result.to_csv("common_anomaly_candidates.csv", index=False)

print("\nSaved: common_anomaly_candidates.csv")

