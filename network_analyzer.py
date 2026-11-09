
import sqlite3
import json
import pandas as pd

DATABASE = "sensor_data.db"

conn = sqlite3.connect(DATABASE)

query = """
SELECT timestamp, raw_json
FROM suricata_events
WHERE event_type = 'flow'
ORDER BY id DESC
"""

records = pd.read_sql_query(query, conn)
conn.close()

features = []

for _, row in records.iterrows():
    event = json.loads(row["raw_json"])
    flow = event.get("flow", {})

    features.append({
        "timestamp": row["timestamp"],
        "source_ip": event.get("src_ip"),
        "destination_ip": event.get("dest_ip"),
        "source_port": event.get("src_port"),
        "destination_port": event.get("dest_port"),
        "protocol": event.get("proto"),
        "packets_sent": flow.get("pkts_toserver", 0),
        "packets_received": flow.get("pkts_toclient", 0),
        "bytes_sent": flow.get("bytes_toserver", 0),
        "bytes_received": flow.get("bytes_toclient", 0),
        "duration": flow.get("age", 0),
        "alerted": flow.get("alerted", False)
    })

df = pd.DataFrame(features)

print("\nNETWORK TRAFFIC FEATURE EXTRACTION")
print("-----------------------------------")

print("Total flow records:", len(df))

if not df.empty:
    print("\nExtracted features:")
    print(df.head(10).to_string(index=False))

    df.to_csv("network_features.csv", index=False)
    print("\nDataset saved as network_features.csv")
else:
    print("No flow records found.")
