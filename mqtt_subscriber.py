
import json
import sqlite3
import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/sensor"

# Create or open the database
conn = sqlite3.connect("sensor_data.db")
cursor = conn.cursor()

# Create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS hall_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    hall_value INTEGER
)
""")
conn.commit()

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT broker")
        client.subscribe(TOPIC)
        print("Subscribed to:", TOPIC)
    else:
        print("MQTT connection failed:", reason_code)

def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        data = json.loads(payload)

        hall_value = data.get("hall_value")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if hall_value is not None:
            cursor.execute(
                "INSERT INTO hall_readings (timestamp, hall_value) VALUES (?, ?)",
                (timestamp, hall_value)
            )
            conn.commit()

            print("Time:", timestamp)
            print("Hall Sensor Value:", hall_value)
            print("Saved to SQLite database")
            print("-----------------------------")

    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        print("Invalid message:", error)

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="RaspberryPi_Hall_Database"
)

client.on_connect = on_connect
client.on_message = on_message

print("Connecting to MQTT broker...")
client.connect(BROKER, PORT, 60)
client.loop_forever()

