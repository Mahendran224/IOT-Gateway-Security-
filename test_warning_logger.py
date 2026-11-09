import sqlite3
from datetime import datetime

conn = sqlite3.connect("sensor_data.db")

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

conn.execute("""
INSERT INTO security_warnings
(timestamp, category, severity, description,
 status, related_flows, related_packets, related_bytes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    timestamp,
    "SYSTEM_TEST",
    "INFO",
    "Testing security warning database integration",
    "TEST",
    7,
    126,
    65812
))

conn.commit()

print("Test warning inserted successfully.")

rows = conn.execute("""
SELECT id, timestamp, category, severity, description, status
FROM security_warnings
ORDER BY id DESC
LIMIT 3
""").fetchall()

print("\nRecent security warnings:")

for row in rows:
    print(row)

conn.close()
