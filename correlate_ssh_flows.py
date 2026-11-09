import sqlite3
import json

flow_ids = [
    2236272382193394,
    159591765984636,
    658340052348658,
    1492732463124286,
    718189959798680
]

conn = sqlite3.connect("file:sensor_data.db?mode=ro", uri=True)

for flow_id in flow_ids:

    rows = conn.execute(
        """
        SELECT id, timestamp, event_type, src_ip, dest_ip,
               src_port, dest_port, protocol, alert_signature, raw_json
        FROM suricata_events
        WHERE raw_json LIKE ?
        ORDER BY timestamp
        """,
        (f'%"flow_id": {flow_id}%',)
    ).fetchall()

    print("\n" + "=" * 65)
    print("FLOW ID:", flow_id)
    print("MATCHING EVENTS:", len(rows))

    for row in rows:
        print(
            "ID:", row[0],
            "| TYPE:", row[2],
            "| SRC:", row[3], row[5],
            "| DEST:", row[4], row[6],
            "| PROTOCOL:", row[7],
            "| ALERT:", row[8]
        )

        try:
            data = json.loads(row[9])
            print("APP PROTOCOL:", data.get("app_proto"))
            print("EVENT TYPE:", data.get("event_type"))
        except (TypeError, json.JSONDecodeError):
            pass

conn.close()
