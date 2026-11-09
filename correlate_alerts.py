import pandas as pd

df = pd.read_csv("protocol_anomaly_results.csv")

anomalies = df[df["potential_anomaly"] == True]

print("\n========== ANOMALY AND ALERT CORRELATION ==========")

print("Total potential anomalies:", len(anomalies))

print("\nSuricata alert status:")

print(anomalies["alerted"].value_counts())

print("\n========== ALERTED FLOWS ==========")

alerted = anomalies[anomalies["alerted"] == True]

columns = [
    "timestamp",
    "source_ip",
    "destination_ip",
    "destination_port",
    "protocol",
    "total_packets",
    "total_bytes",
    "duration",
    "anomaly_reason"
]

print(alerted[columns].to_string(index=False))

print("\n========== NON-ALERTED ANOMALIES ==========")

print("Count:", len(anomalies[anomalies["alerted"] == False]))

print("\n========== CORRELATION COMPLETED ==========")
