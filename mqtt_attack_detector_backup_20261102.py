import json
import sqlite3
import time
from datetime import datetime

import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "lab/test"

DATABASE = "sensor_data.db"
ALERT_INTERVAL = 60

last_alert_time = 0


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to Raspberry Pi MQTT broker")
        client.subscribe(TOPIC)
        print("Monitoring topic:", TOPIC)
    else:
        print("Connection failed:", reason_code)


def on_message(client, userdata, message):
    global last_alert_time

    try:
        payload = message.payload.decode("utf-8")
    except UnicodeDecodeError:
        payload = "[Non-text MQTT payload]"

    print("\nMQTT TEST MESSAGE RECEIVED")
    print("Topic:", message.topic)
    print("Payload:", payload)

    # This is a controlled classroom simulation rule.
    # Messages on the dedicated test topic are labelled as simulated events.

    current_time = time.time()

    if current_time - last_alert_time < ALERT_INTERVAL:
        print("Alert cooldown active. Event received but warning not repeated.")
        return

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    description = (
        "CLASSROOM SIMULATION: "
        "MQTT test-topic event detected. "
        "This is a controlled demonstration, "
        "not a confirmed cyberattack."
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
            "MEDIUM",
            description
        ))

        conn.commit()
        last_alert_time = current_time

        print("\n====================================")
        print("MQTT ATTACK SIMULATION DETECTED")
        print("Severity: MEDIUM")
        print("Topic:", message.topic)
        print("Classification: Classroom simulation")
        print("Dashboard warning saved successfully")
        print("====================================\n")

    finally:
        conn.close()


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="MQTT_Classroom_Detector"
)

client.on_connect = on_connect
client.on_message = on_message

print("IoT Security Gateway - MQTT Demo Detector")
print("Monitoring:", TOPIC)
print("Classification: Controlled classroom simulation")

client.connect(BROKER, PORT, 60)
client.loop_forever()
