import sqlite3
import json
import time

DATABASE = "sensor_data.db"
CHECK_INTERVAL = 10


def process_new_alerts():

    conn = sqlite3.connect(DATABASE, timeout=20)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.timestamp, s.raw_json
        FROM suricata_events s
        LEFT JOIN security_context c
        ON s.id = c.suricata_event_id
        WHERE s.event_type = 'alert'
        AND c.suricata_event_id IS NULL
        ORDER BY s.id
    """)

    events = cursor.fetchall()
    saved = 0

    for event_id, timestamp, raw_json in events:

        try:
            event = json.loads(raw_json)

            alert = event.get("alert", {})
            flow = event.get("flow", {})

            cursor.execute("""
                INSERT OR IGNORE INTO security_context (
                    suricata_event_id,
                    timestamp,
                    flow_id,
                    signature_id,
                    signature,
                    severity,
                    category,
                    action,
                    direction,
                    flow_src_ip,
                    flow_src_port,
                    flow_dest_ip,
                    flow_dest_port,
                    protocol,
                    app_proto,
                    pkts_toserver,
                    pkts_toclient,
                    bytes_toserver,
                    bytes_toclient
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                timestamp,
                event.get("flow_id"),
                alert.get("signature_id"),
                alert.get("signature"),
                alert.get("severity"),
                alert.get("category"),
                alert.get("action"),
                event.get("direction"),
                flow.get("src_ip"),
                flow.get("src_port"),
                flow.get("dest_ip"),
                flow.get("dest_port"),
                event.get("proto"),
                event.get("app_proto"),
                flow.get("pkts_toserver"),
                flow.get("pkts_toclient"),
                flow.get("bytes_toserver"),
                flow.get("bytes_toclient")
            ))

            if cursor.rowcount == 1:
                saved += 1

        except (json.JSONDecodeError, TypeError) as error:
            print("Skipped event:", event_id, error)

    conn.commit()
    conn.close()

    if saved > 0:
        print("New security-context records:", saved)

    return saved


print("Automatic security-context extractor started")
print("Checking for new alerts every", CHECK_INTERVAL, "seconds")

try:
    while True:
        try:
            process_new_alerts()

        except sqlite3.Error as error:
            print("Database error:", error)

        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print("\nSecurity-context extractor stopped.")
