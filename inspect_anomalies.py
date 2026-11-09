import pandas as pd

df = pd.read_csv("protocol_anomaly_results.csv")

anomalies = df[df["potential_anomaly"] == True]

print("\n========== POTENTIAL ANOMALIES ==========")

print("Total:", len(anomalies))

print("\n========== ANOMALY REASONS ==========")
print(anomalies["anomaly_reason"].value_counts())

print("\n========== DESTINATION PORTS ==========")
print(anomalies["destination_port"].value_counts())

print("\n========== PROTOCOL DISTRIBUTION ==========")
print(anomalies["protocol"].value_counts())

print("\n========== FLAGGED FLOW DETAILS ==========")

columns = [
    "timestamp",
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

print(anomalies[columns].to_string(index=False))

print("\n========== INVESTIGATION COMPLETED ==========")
