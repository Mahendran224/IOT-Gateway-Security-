import sqlite3
import json

event_ids = [1705, 8899, 1706, 1668, 1721, 9276, 6862, 1716, 16]

conn = sqlite3.connect("sensor_data.db")
conn.row_factory = sqlite3.Row

for event_id in event_ids:

    row = conn.execute("""
        SELECT id, timestamp, event_type, raw_json
        FROM suricata_events
        WHERE id = ?
    """, (event_id,)).fetchone()

    if not row:
        print(f"\nEvent {event_id}: NOT FOUND")
        continue

    data = json.loads(row["raw_json"])

    print("\n" + "=" * 65)
    print("EVENT:", row["id"])
    print("TIMESTAMP:", row["timestamp"])
    print("TYPE:", row["event_type"])

    print("SOURCE:", data.get("src_ip"), data.get("src_port"))
    print("DESTINATION:", data.get("dest_ip"), data.get("dest_port"))
    print("PROTOCOL:", data.get("proto"))
    print("APP PROTOCOL:", data.get("app_proto"))

    print("FLOW:", data.get("flow"))
    print("ALERT:", data.get("alert"))
    print("DNS:", data.get("dns"))
    print("TLS:", data.get("tls"))
    print("HTTP:", data.get("http"))

conn.close()
