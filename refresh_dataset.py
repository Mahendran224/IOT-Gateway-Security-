import sqlite3
import pandas as pd
import subprocess
import sys
import os

DATABASE = "sensor_data.db"
CSV_FILE = "network_flow_features.csv"
EXTRACTION_SCRIPT = "extract_flow_features.py"


def get_database_count():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA query_only=ON")

    count = conn.execute("""
        SELECT COUNT(*)
        FROM suricata_events
        WHERE event_type = 'flow'
    """).fetchone()[0]

    conn.close()
    return count


print("\nNETWORK DATASET REFRESH")
print("-----------------------")

before_count = get_database_count()
print("Database records before extraction:", before_count)

print("\nRunning feature extraction...")

result = subprocess.run(
    [sys.executable, EXTRACTION_SCRIPT],
    capture_output=True,
    text=True
)

print(result.stdout)

if result.returncode != 0:
    print("Feature extraction failed:")
    print(result.stderr)
    sys.exit(1)

if not os.path.exists(CSV_FILE):
    print("CSV file was not created.")
    sys.exit(1)

df = pd.read_csv(CSV_FILE)

after_count = get_database_count()
csv_count = len(df)

print("\nDATASET VERIFICATION")
print("--------------------")
print("Database before:", before_count)
print("Database after:", after_count)
print("CSV records:", csv_count)
print("New database records:", after_count - before_count)
print("CSV duplicate event IDs:", df["event_id"].duplicated().sum())
print("CSV duplicate flow IDs:", df["flow_id"].duplicated().sum())

if after_count == csv_count:
    print("\nSTATUS: DATASET SYNCHRONIZED")
else:
    print("\nSTATUS: DATABASE CHANGED OR EXTRACTION SNAPSHOT IS OUTDATED")
    print("Run the refresh again when traffic is relatively stable.")
