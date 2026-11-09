import sqlite3
import json

event_ids = [16, 1716, 1721, 8899, 6862, 1747, 1802, 2082]

conn = sqlite3.connect("file:sensor_data.db?mode=ro", uri=True)

for event_id in event_ids:

    row = conn.execute(
        """
        SELECT id, timestamp, raw_json
        FROM suricata_events
        WHERE id = ?
        """,
        (event_id,)
    ).fetchone()

    if not row:
        continue

    data = json.loads(row[2])

    print("\n" + "=" * 55)
    print("EVENT ID:", row[0])
    print("TIMESTAMP:", row[1])
    print("FLOW ID:", data.get("flow_id"))
    print("PROTOCOL:", data.get("proto"))

    print("TCP:", data.get("tcp"))

    flow = data.get("flow", {})

    print("FLOW STATE:", flow.get("state"))
    print("FLOW REASON:", flow.get("reason"))
    print("PACKETS:", flow.get("pkts_toserver"),
          flow.get("pkts_toclient"))
    print("BYTES:", flow.get("bytes_toserver"),
          flow.get("bytes_toclient"))

conn.close()
