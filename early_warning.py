
import sqlite3
import json
import time
from datetime import datetime, timedelta

DATABASE = "sensor_data.db"

CHECK_INTERVAL = 60
CURRENT_WINDOW = 1
SHORT_BASELINE = 5
LONG_BASELINE = 30

# Informational signatures observed during project testing.
INFORMATIONAL_SIDS = {2049201, 2049202}


def get_network_data(conn, start_time, end_time):

    rows = conn.execute("""
        SELECT src_ip, dest_ip, raw_json
        FROM suricata_events
        WHERE event_type = 'flow'
          AND substr(timestamp, 1, 19) >= ?
          AND substr(timestamp, 1, 19) < ?
        ORDER BY id
    """, (start_time, end_time)).fetchall()

    data = {
        "flows": 0,
        "packets": 0,
        "bytes": 0,
        "source_ips": set(),
        "destination_ips": set(),
        "alerted_flows": 0
    }

    for src_ip, dest_ip, raw_json in rows:

        try:
            event = json.loads(raw_json)
            flow = event.get("flow", {})

            if not isinstance(flow, dict):
                continue

            data["flows"] += 1

            data["packets"] += (
                flow.get("pkts_toserver", 0)
                + flow.get("pkts_toclient", 0)
            )

            data["bytes"] += (
                flow.get("bytes_toserver", 0)
                + flow.get("bytes_toclient", 0)
            )

            if src_ip:
                data["source_ips"].add(src_ip)

            if dest_ip:
                data["destination_ips"].add(dest_ip)

            if flow.get("alerted", False):
                data["alerted_flows"] += 1

        except (json.JSONDecodeError, TypeError, ValueError):
            continue

    data["source_ips"] = len(data["source_ips"])
    data["destination_ips"] = len(data["destination_ips"])

    return data


def get_event_counts(conn, start_time, end_time):

    result = {
        "alert": 0,
        "dns": 0,
        "mqtt": 0,
        "review_alerts": []
    }

    for event_type in ["alert", "dns", "mqtt"]:

        rows = conn.execute("""
            SELECT raw_json
            FROM suricata_events
            WHERE event_type = ?
              AND substr(timestamp, 1, 19) >= ?
              AND substr(timestamp, 1, 19) < ?
        """, (event_type, start_time, end_time)).fetchall()

        result[event_type] = len(rows)

        if event_type == "alert":

            for row in rows:

                try:
                    event = json.loads(row[0])
                    alert = event.get("alert", {})

                    if not isinstance(alert, dict):
                        alert = {}

                    sid = alert.get("signature_id")
                    signature = alert.get(
                        "signature", "Unknown signature"
                    )

                    if sid not in INFORMATIONAL_SIDS:

                        result["review_alerts"].append({
                            "sid": sid,
                            "signature": signature
                        })

                except (json.JSONDecodeError, TypeError):
                    result["review_alerts"].append({
                        "sid": None,
                        "signature": "Unable to parse alert"
                    })

    return result


def save_warning(conn, timestamp, category, severity,
                 description, current):

    cutoff_time = (
        datetime.now() - timedelta(minutes=5)
    ).strftime("%Y-%m-%d %H:%M:%S")

    existing = conn.execute("""
        SELECT id
        FROM security_warnings
        WHERE category = ?
          AND status = 'OPEN'
          AND datetime(replace(timestamp, 'T', ' ')) >= datetime(?)
        LIMIT 1
    """, (category, cutoff_time)).fetchone()

    if existing:
        print("Duplicate warning skipped:", category)
        return

    conn.execute("""
        INSERT INTO security_warnings
        (timestamp, category, severity, description,
         status, related_flows, related_packets, related_bytes)
        VALUES (?, ?, ?, ?, 'OPEN', ?, ?, ?)
    """, (
        timestamp,
        category,
        severity,
        description,
        current["flows"],
        current["packets"],
        current["bytes"]
    ))

    conn.commit()

    print("Warning saved to database:", category)


def process_warnings(conn, warnings, timestamp, current):

    if warnings["traffic"]:

        description = (
            "TRAFFIC BEHAVIOUR ANOMALY: "
            + "; ".join(warnings["traffic"])
        )

        save_warning(
            conn,
            timestamp,
            "TRAFFIC_BEHAVIOUR_ANOMALY",
            "LOW",
            description,
            current
        )

    if warnings["suricata"]:

        descriptions = []

        for alert in warnings["suricata"]:

            descriptions.append(
                "SID: "
                + str(alert["sid"])
                + " | "
                + alert["signature"]
            )

        description = (
            "SURICATA ALERTS REQUIRING REVIEW: "
            + "; ".join(descriptions)
        )

        save_warning(
            conn,
            timestamp,
            "SURICATA_ALERT",
            "MEDIUM",
            description,
            current
        )


def main():

    conn = sqlite3.connect(DATABASE, timeout=20)
    conn.execute("PRAGMA busy_timeout = 20000")

    print("======================================")
    print(" ADVANCED IOT GATEWAY EARLY WARNING")
    print("======================================")
    print("Current window:", CURRENT_WINDOW, "minute")
    print("Short baseline:", SHORT_BASELINE, "minutes")
    print("Long baseline:", LONG_BASELINE, "minutes")
    print("--------------------------------------")

    try:

        while True:

            now = datetime.now()

            end_time = now.strftime("%Y-%m-%dT%H:%M:%S")

            current_start = (
                now - timedelta(minutes=CURRENT_WINDOW)
            ).strftime("%Y-%m-%dT%H:%M:%S")

            short_start = (
                now - timedelta(
                    minutes=SHORT_BASELINE + CURRENT_WINDOW
                )
            ).strftime("%Y-%m-%dT%H:%M:%S")

            long_start = (
                now - timedelta(
                    minutes=LONG_BASELINE + CURRENT_WINDOW
                )
            ).strftime("%Y-%m-%dT%H:%M:%S")

            current = get_network_data(
                conn, current_start, end_time
            )

            short_data = get_network_data(
                conn, short_start, current_start
            )

            long_data = get_network_data(
                conn, long_start, current_start
            )

            current_events = get_event_counts(
                conn, current_start, end_time
            )

            print("\nTime:", end_time)

            print("\nCURRENT ONE-MINUTE TRAFFIC:")
            print(current)

            print("\nPREVIOUS FIVE-MINUTE BASELINE:")
            print(short_data)

            print("\nPREVIOUS THIRTY-MINUTE BASELINE:")
            print(long_data)

            print("\nCURRENT SECURITY EVENTS:")
            print(current_events)

            warnings = {
                "traffic": [],
                "suricata": []
            }

            # Flow count comparison
            for name, baseline, minutes in [
                ("SHORT", short_data, SHORT_BASELINE),
                ("LONG", long_data, LONG_BASELINE)
            ]:

                if baseline["flows"] >= 3:

                    average = baseline["flows"] / minutes

                    if current["flows"] > max(10, average * 3):

                        warnings["traffic"].append(
                            name + " baseline: unusual flow count"
                        )

            # Packet volume comparison
            for name, baseline, minutes in [
                ("SHORT", short_data, SHORT_BASELINE),
                ("LONG", long_data, LONG_BASELINE)
            ]:

                if baseline["packets"] > 0:

                    average = baseline["packets"] / minutes

                    if current["packets"] > max(100, average * 3):

                        warnings["traffic"].append(
                            name + " baseline: unusual packet volume"
                        )

            # Data volume comparison
            for name, baseline, minutes in [
                ("SHORT", short_data, SHORT_BASELINE),
                ("LONG", long_data, LONG_BASELINE)
            ]:

                if baseline["bytes"] > 0:

                    average = baseline["bytes"] / minutes

                    if current["bytes"] > max(10000, average * 3):

                        warnings["traffic"].append(
                            name + " baseline: unusual data volume"
                        )

            # Independent Suricata alert classification
            warnings["suricata"] = current_events["review_alerts"]

            print("\nDNS events:", current_events["dns"])
            print("MQTT events:", current_events["mqtt"])

            if warnings["traffic"] or warnings["suricata"]:

                print("\n*** SECURITY REVIEW REQUIRED ***")

                for reason in warnings["traffic"]:
                    print("- Traffic indicator:", reason)

                for alert in warnings["suricata"]:
                    print(
                        "- Suricata alert requiring review:",
                        "SID:", alert["sid"],
                        "| Signature:", alert["signature"]
                    )

                print(
                    "These are indicators, not confirmed attacks."
                )

                process_warnings(
                    conn,
                    warnings,
                    end_time,
                    current
                )

            else:
                print(
                    "\nStatus: No configured warning condition detected."
                )

            if short_data["flows"] == 0:
                print("NOTE: Short baseline has no flow records.")

            if long_data["flows"] == 0:
                print("NOTE: Long baseline has no flow records.")

            print("--------------------------------------")

            time.sleep(CHECK_INTERVAL)

    finally:

        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\nEarly-warning monitor stopped.")

