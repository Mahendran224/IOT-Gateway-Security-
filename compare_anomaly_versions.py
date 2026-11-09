import pandas as pd

v1 = pd.read_csv("network_anomaly_results.csv")
v2 = pd.read_csv("network_anomaly_results_v2.csv")
v3 = pd.read_csv("network_anomaly_results_v3.csv")

print("\nANOMALY VERSION COMPARISON")

for name, df in [("V1", v1), ("V2", v2), ("V3", v3)]:
    count = df["anomaly_candidate"].sum()
    print(f"{name}: {count} candidates")

sets = {}

for name, df in [("V1", v1), ("V2", v2), ("V3", v3)]:
    sets[name] = set(
        df.loc[df["anomaly_candidate"], "event_id"]
    )

print("\nOVERLAPPING CANDIDATES")

print("V1 and V2:", len(sets["V1"] & sets["V2"]))
print("V1 and V3:", len(sets["V1"] & sets["V3"]))
print("V2 and V3:", len(sets["V2"] & sets["V3"]))
print("All three:", len(sets["V1"] & sets["V2"] & sets["V3"]))

print("\nCANDIDATES COMMON TO ALL THREE")

common = sets["V1"] & sets["V2"] & sets["V3"]
print(sorted(common))
