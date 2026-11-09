
import json
import sqlite3
import subprocess

DATABASE = "sensor_data.db"
EVE_LOG = "/var/log/suricata/eve.json"

# Connect to the existing database
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Create a separate table for Suricata events
cursor.execute("""
CREATE TABLE IF NOT EXISTS suricata_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    event_type TEXT,
    src_ip TEXT,
    dest_ip TEXT,
    src_port INTEGER,
    dest_port INTEGER,
    protocol TEXT,
    mqtt_topic TEXT,
    mqtt_message TEXT,
    alert_signature TEXT,
    raw_json TEXT
)
""")

conn.commit()

print("Suricata event collector started")
print("Monitoring:", EVE_LOG)
print("Saving events to:", DATABASE)
print("----------------------------------")

# Follow only new log entries
process = subprocess.Popen(
    ["tail", "-n", "0", "-F", EVE_LOG],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

try:
    for line in process.stdout:
        try:
            event = json.loads(line)

            event_type = event.get("event_type")

            mqtt = event.get("mqtt", {})
            publish = mqtt.get("publish", {})

            alert = event.get("alert", {})

            cursor.execute("""
                INSERT INTO suricata_events (
                    timestamp, event_type,
                    src_ip, dest_ip,
                    src_port, dest_port,
                    protocol, mqtt_topic,
                    mqtt_message, alert_signature,
                    raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.get("timestamp"),
                event_type,
                event.get("src_ip"),
                event.get("dest_ip"),
                event.get("src_port"),
                event.get("dest_port"),
                event.get("proto"),
                publish.get("topic"),
                publish.get("message"),
                alert.get("signature"),
                json.dumps(event)
            ))

            conn.commit()

            print("Event:", event_type)
            print("Source:", event.get("src_ip"))
            print("Destination:", event.get("dest_ip"))

            if publish:
                print("MQTT Topic:", publish.get("topic"))
                print("MQTT Message:", publish.get("message"))

            if alert:
                print("Alert:", alert.get("signature"))

            print("Saved to SQLite")
            print("----------------------------------")

        except json.JSONDecodeError:
            continue

except KeyboardInterrupt:
    print("\nStopping Suricata event collector...")

finally:
    process.terminate()
    conn.close()
    print("Database connection closed.")
