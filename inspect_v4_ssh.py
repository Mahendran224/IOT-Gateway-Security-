import pandas as pd
import sqlite3

df = pd.read_csv("network_anomaly_results_v4.csv")
anomaly = df[df["anomaly_candidate"] == True]

conn = sqlite3.connect("file:sensor_data.db?mode=ro", uri=True)

query = """
SELECT
    id,
    timestamp,
    src_ip,
    dest_ip,
    src_port,
    dest_port,
    protocol,
    raw_json
FROM suricata_events
WHERE event_type = 'flow'
AND (
    src_port = 22 OR dest_port = 22
)
ORDER BY timestamp
"""

ssh = pd.read_sql_query(query, conn)
conn.close()

result = anomaly.merge(
    ssh,
    left_on="event_id",
    right_on="id",
    how="inner"
)

print("\nV4 SSH ANOMALY CANDIDATES")
print("Total:", len(result))

print(
    result[
        [
            "event_id",
            "timestamp_x",
            "src_ip_x",
            "dest_ip_x",
            "src_port",
            "dest_port",
            "total_packets",
            "total_bytes",
            "duration_seconds",
            "connection_state",
            "anomaly_score"
        ]
    ].to_string(index=False)
)
