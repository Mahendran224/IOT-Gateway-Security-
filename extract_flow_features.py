import sqlite3
import json
import pandas as pd

DB_NAME = "sensor_data.db"
OUTPUT_FILE = "network_flow_features.csv"

conn = sqlite3.connect(DB_NAME)
conn.execute("PRAGMA query_only=ON")

rows = conn.execute("""
    SELECT id, timestamp, src_ip, dest_ip, raw_json
    FROM suricata_events
    WHERE event_type = 'flow'
    ORDER BY id
""").fetchall()

features = []

for event_id, timestamp, src_ip, dest_ip, raw in rows:

    data = json.loads(raw)

    flow = data.get("flow", {})
    tcp = data.get("tcp", {})

    packets_sent = flow.get("pkts_toserver", 0)
    packets_received = flow.get("pkts_toclient", 0)

    bytes_sent = flow.get("bytes_toserver", 0)
    bytes_received = flow.get("bytes_toclient", 0)

    features.append({

        "event_id": event_id,
        "timestamp": timestamp,
        "flow_id": data.get("flow_id"),

        "src_ip": src_ip,
        "dest_ip": dest_ip,

        "protocol": data.get("proto"),
        "app_protocol": data.get("app_proto"),

        "packets_sent": packets_sent,
        "packets_received": packets_received,
        "total_packets": packets_sent + packets_received,

        "bytes_sent": bytes_sent,
        "bytes_received": bytes_received,
        "total_bytes": bytes_sent + bytes_received,

        "duration_seconds": flow.get("age", 0),

        "connection_state": flow.get("state"),
        "flow_reason": flow.get("reason"),

        "tcp_syn": tcp.get("syn"),
        "tcp_ack": tcp.get("ack"),
        "tcp_fin": tcp.get("fin"),
        "tcp_rst": tcp.get("rst"),

        "alerted": flow.get("alerted")

    })

conn.close()

df = pd.DataFrame(features)

df.to_csv(OUTPUT_FILE, index=False)

print("NETWORK FLOW FEATURE EXTRACTION COMPLETED")
print("------------------------------------------")
print("Total flow records:", len(df))
print("Total extracted features:", len(df.columns))
print("Output file:", OUTPUT_FILE)

print("\nFirst five records:")
print(df.head().to_string(index=False))

print("\nMissing values:")
print(df.isnull().sum())
