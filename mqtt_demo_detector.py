import sqlite3
from datetime import datetime

DATABASE = "sensor_data.db"

DEMO_TOPIC = "lab/test"
DEMO_MARKER = "SIMULATE_SECURITY_ALERT"


def record_demo_alert():

    conn = sqlite3.connect(DATABASE, timeout=20)

    try:
        conn.execute("PRAGMA busy_timeout = 20000")

        timestamp = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

        description = (
            "CLASSROOM SIMULATION ONLY: "
            "Recognised designated MQTT demonstration marker. "
            "This is not a confirmed cyberattack."
        )

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

        print("MQTT SECURITY ANOMALY DETECTED")
        print("Classification: Classroom simulation")
        print("Topic:", DEMO_TOPIC)

    finally:
        conn.close()


if __name__ == "__main__":
    print("MQTT Classroom Demonstration Detector")
    print("Marker:", DEMO_MARKER)
    print("This script records only a labelled simulation.")

    record_demo_alert()
