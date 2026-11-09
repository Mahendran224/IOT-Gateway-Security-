import pandas as pd
import sqlite3

# Load V4 results
df = pd.read_csv("network_anomaly_results_v4.csv")

normal = df[df["anomaly_candidate"] == False]
anomaly = df[df["anomaly_candidate"] == True]

columns = ["total_packets", "total_bytes", "duration_seconds"]

print("\nV4 NORMAL TRAFFIC")
print(normal[columns].describe().round(2))

print("\nV4 ANOMALY CANDIDATES")
print(anomaly[columns].describe().round(2))

print("\nANOMALY CANDIDATES BY CONNECTION STATE")
print(anomaly["connection_state"].value_counts())

print("\nANOMALY CANDIDATES BY SOURCE IP")
print(anomaly["src_ip"].value_counts().head(15))

# Read port information from SQLite without modifying the database
event_ids = anomaly["event_id"].dropna().astype(int).tolist()

conn = sqlite3.connect("file:sensor_data.db?mode=ro", uri=True)

placeholders = ",".join("?" for _ in event_ids)

query = f"""
SELECT id AS event_id, src_port, dest_port
FROM suricata_events
WHERE event_type = 'flow'
AND id IN ({placeholders})
"""

ports = pd.read_sql_query(query, conn, params=event_ids)
conn.close()

merged = anomaly.merge(ports, on="event_id", how="left")

print("\nANOMALY CANDIDATES BY DESTINATION PORT")
print(merged["dest_port"].value_counts(dropna=False).head(15))

print("\nANOMALY CANDIDATES BY SURICATA ALERT STATUS")
print(anomaly["alerted"].value_counts(dropna=False))

print("\nTOP 20 ANOMALY CANDIDATES")
print(
    merged.sort_values("anomaly_score", ascending=False)[
        [
            "event_id", "src_ip", "dest_ip",
            "src_port", "dest_port",
            "protocol", "app_protocol",
            "total_packets", "total_bytes",
            "duration_seconds", "alerted",
            "anomaly_score"
        ]
    ].head(20).to_string(index=False)
)

print("\nPORT INFORMATION MATCHED:", len(ports), "of", len(anomaly))
