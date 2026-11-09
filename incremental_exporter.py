import sqlite3
import pandas as pd
import json
import time
import os

DATABASE = "sensor_data.db"
OUTPUT = "continuous_network_dataset.csv"
STATE_FILE = "exporter_state.txt"

print("Incremental network exporter started")

while True:
    with open(STATE_FILE, "r") as file:
        last_id = int(file.read().strip())

    conn = sqlite3.connect(DATABASE)

    query = """
    SELECT id, timestamp, src_ip, dest_ip,
           src_port, dest_port, protocol, raw_json
    FROM suricata_events
    WHERE event_type = 'flow'
      AND id > ?
    ORDER BY id
    """

    df = pd.read_sql_query(query, conn, params=(last_id,))
    conn.close()

    if not df.empty:
        records = []

        for _, row in df.iterrows():
            event = json.loads(row["raw_json"])
            flow = event.get("flow", {})

            records.append({
                "timestamp": row["timestamp"],
                "source_ip": row["src_ip"],
                "destination_ip": row["dest_ip"],
                "source_port": row["src_port"],
                "destination_port": row["dest_port"],
                "protocol": row["protocol"],
                "packets_sent": flow.get("pkts_toserver", 0),
                "packets_received": flow.get("pkts_toclient", 0),
                "bytes_sent": flow.get("bytes_toserver", 0),
                "bytes_received": flow.get("bytes_toclient", 0),
                "duration": flow.get("age", 0),
                "alerted": flow.get("alerted", False)
            })

        output_df = pd.DataFrame(records)

        output_df.to_csv(
            OUTPUT,
            mode="a",
            header=False,
            index=False
        )

        last_id = int(df["id"].max())

        with open(STATE_FILE, "w") as file:
            file.write(str(last_id))

        print("New records exported:", len(df))
        print("Latest database ID:", last_id)

    else:
        print("No new flow records")

    time.sleep(60)
