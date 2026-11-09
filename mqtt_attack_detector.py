import sqlite3
from datetime import datetime

import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "lab/test"

DATABASE = "sensor_data.db"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to Raspberry Pi MQTT broker")
        client.subscribe(TOPIC)
        print("Monitoring topic:", TOPIC)
    else:
        print("Connection failed:", reason_code)


def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
    except UnicodeDecodeError:
        payload = "[Non-text MQTT payload]"

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    description = (
        "CLASSROOM SIMULATION: Unexpected MQTT message received "
        "on the monitored test topic. Not a confirmed cyberattack. "
        f"Message: {payload[:200]}"
    )

    conn = sqlite3.connect(DATABASE, timeout=20)

    try:
        conn.execute("PRAGMA busy_timeout = 20000")

        conn.execute("""
            INSERT INTO security_warnings
            (timestamp, category, severity, description,
             status, related_flows, related_packets, related_bytes)
            VALUES (?, ?, ?, ?, 'OPEN', 0, 0, 0)
        """, (
            timestamp,
            "MQTT_SECURITY_ANOMALY",
            "LOW",
            description
        ))

        conn.commit()

        print("\nLOW-SEVERITY MQTT WARNING SAVED")
        print("Topic:", message.topic)
        print("Payload:", payload)
        print("Classification: Controlled classroom simulation")
        print("Dashboard warning saved successfully")

    except sqlite3.Error as error:
        print("Database error:", error)

    finally:
        conn.close()


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="MQTT_Classroom_Detector"
)

client.on_connect = on_connect
client.on_message = on_message

print("IoT Security Gateway - MQTT Warning Monitor")
print("Monitoring:", TOPIC)
print("Severity: LOW")
print("Classification: Controlled classroom simulation")

client.connect(BROKER, PORT, 60)
client.loop_forever()
