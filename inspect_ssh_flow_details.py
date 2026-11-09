import sqlite3
import json

event_ids = [16, 8899, 1721, 9276, 1716, 6862]

conn = sqlite3.connect("sensor_data.db")
conn.row_factory = sqlite3.Row

for event_id in event_ids:

    row = conn.execute("""
        SELECT id, timestamp, raw_json
        FROM suricata_events
        WHERE id = ?
    """, (event_id,)).fetchone()

    if not row:
        continue

    data = json.loads(row["raw_json"])
    flow = data.get("flow", {})

    print("\n" + "=" * 55)
    print("EVENT:", event_id)
    print("TIME:", row["timestamp"])
    print("SOURCE:", data.get("src_ip"), data.get("src_port"))
    print("DESTINATION:", data.get("dest_ip"), data.get("dest_port"))
    print("TCP FLAGS:", data.get("tcp"))
    print("FLOW STATE:", flow.get("state"))
    print("FLOW REASON:", flow.get("reason"))
    print("PACKETS TO SERVER:", flow.get("pkts_toserver"))
    print("PACKETS TO CLIENT:", flow.get("pkts_toclient"))
    print("ALERT:", data.get("alert"))

conn.close()
