
from flask import Flask, render_template_string
import sqlite3
import json

app = Flask(__name__)

DATABASE = "sensor_data.db"

INFORMATIONAL_SIDS = {2049201, 2049202}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>IoT Security Gateway Dashboard</title>
    <meta http-equiv="refresh" content="10">

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #101827;
            color: white;
        }

        header {
            background: #172438;
            padding: 22px;
            text-align: center;
        }

        h1 { margin: 0; color: #42d9c8; }

        .container { padding: 25px; }

        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px;
        }

        .card {
            background: #1d2c42;
            padding: 22px;
            border-radius: 10px;
        }

        .card h3 {
            color: #a9bdd4;
            font-size: 15px;
        }

        .value {
            font-size: 30px;
            color: #42d9c8;
            font-weight: bold;
        }

        h2 {
            color: #42d9c8;
            margin-top: 35px;
        }

        .table-wrap {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: #1d2c42;
            min-width: 650px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #34445a;
            font-size: 13px;
        }

        th { color: #42d9c8; }

        .severity-high { color: #ff7777; font-weight: bold; }
        .severity-medium { color: #ffc66d; font-weight: bold; }
        .severity-low { color: #42d9c8; font-weight: bold; }

        .informational {
            color: #42d9c8;
            font-weight: bold;
        }

        .review {
            color: #ffc66d;
            font-weight: bold;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #a9bdd4;
        }

        .note {
            color: #a9bdd4;
            font-size: 13px;
            margin-top: 10px;
        }
    </style>
</head>

<body>

<header>
    <h1>IoT Security Gateway</h1>
    <p>AI-Enabled Edge Gateway for Intelligent IoT Network Security</p>
</header>

<div class="container">

    <div class="cards">

        <div class="card">
            <h3>Total Hall Readings</h3>
            <div class="value">{{ hall_count }}</div>
        </div>

        <div class="card">
            <h3>Latest Hall Sensor Value</h3>
            <div class="value">{{ latest_hall }}</div>
        </div>

        <div class="card">
            <h3>Total Network Events</h3>
            <div class="value">{{ event_count }}</div>
        </div>

        <div class="card">
            <h3>Total Suricata Alerts</h3>
            <div class="value">{{ alert_count }}</div>
        </div>

        <div class="card">
            <h3>Informational Alerts</h3>
            <div class="value">{{ informational_count }}</div>
        </div>

        <div class="card">
            <h3>Alerts Requiring Review</h3>
            <div class="value">{{ review_count }}</div>
        </div>

        <div class="card">
            <h3>Total Early Warnings</h3>
            <div class="value">{{ warning_count }}</div>
        </div>

        <div class="card">
            <h3>Open Warnings</h3>
            <div class="value">{{ open_warning_count }}</div>
        </div>

        <div class="card">
            <h3>Low Severity</h3>
            <div class="value">{{ low_count }}</div>
        </div>

        <div class="card">
            <h3>Medium Severity</h3>
            <div class="value">{{ medium_count }}</div>
        </div>

        <div class="card">
            <h3>High Severity</h3>
            <div class="value">{{ high_count }}</div>
        </div>

    </div>

    <h2>Recent Hall Sensor Readings</h2>

    <div class="table-wrap">
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Hall Value</th>
        </tr>

        {% for row in hall_rows %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
        </tr>
        {% else %}
        <tr>
            <td colspan="2">No sensor readings available.</td>
        </tr>
        {% endfor %}
    </table>
    </div>

    <h2>Recent Network Events</h2>

    <div class="table-wrap">
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Event Type</th>
            <th>Source IP</th>
            <th>Destination IP</th>
            <th>Protocol</th>
            <th>MQTT Topic</th>
        </tr>

        {% for row in event_rows %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] or '-' }}</td>
            <td>{{ row[3] or '-' }}</td>
            <td>{{ row[4] or '-' }}</td>
            <td>{{ row[5] or '-' }}</td>
        </tr>
        {% else %}
        <tr>
            <td colspan="6">No network events available.</td>
        </tr>
        {% endfor %}
    </table>
    </div>

    <h2>Suricata Alert Classification</h2>

    <p class="note">
        Informational signatures are separated from alerts requiring
        investigation. A review classification does not confirm an attack.
    </p>

    <div class="table-wrap">
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Source IP</th>
            <th>Signature ID</th>
            <th>Alert Signature</th>
            <th>Classification</th>
        </tr>

        {% for row in alert_rows %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] or '-' }}</td>
            <td>{{ row[2] if row[2] is not none else '-' }}</td>
            <td>{{ row[3] }}</td>
            <td class="{{ 'informational' if row[4] == 'INFORMATIONAL' else 'review' }}">
                {{ row[4] }}
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="5">No Suricata alerts recorded.</td>
        </tr>
        {% endfor %}
    </table>
    </div>

    <h2>Early Warning Monitor</h2>

    <p class="note">
        Preliminary network indicators for investigation.
        A warning is not, by itself, confirmation of an attack.
    </p>

    <div class="table-wrap">
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Category</th>
            <th>Severity</th>
            <th>Description</th>
            <th>Status</th>
            <th>Flows</th>
            <th>Packets</th>
            <th>Bytes</th>
        </tr>

        {% for row in warning_rows %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td class="severity-{{ row[2]|lower }}">
                {{ row[2] }}
            </td>
            <td>{{ row[3] }}</td>
            <td>{{ row[4] }}</td>
            <td>{{ row[5] }}</td>
            <td>{{ row[6] }}</td>
            <td>{{ row[7] }}</td>
        </tr>
        {% else %}
        <tr>
            <td colspan="8">No early warnings recorded.</td>
        </tr>
        {% endfor %}
    </table>
    </div>

</div>

<div class="footer">
    Raspberry Pi 4 Edge Gateway | Suricata IDS | MQTT | SQLite
</div>

</body>
</html>
"""


def get_data():

    conn = sqlite3.connect(DATABASE, timeout=20)
    cursor = conn.cursor()

    try:

        cursor.execute("PRAGMA busy_timeout = 20000")

        hall_count = cursor.execute(
            "SELECT COUNT(*) FROM hall_readings"
        ).fetchone()[0]

        latest = cursor.execute(
            "SELECT hall_value FROM hall_readings ORDER BY id DESC LIMIT 1"
        ).fetchone()

        latest_hall = latest[0] if latest else "No Data"

        event_count = cursor.execute(
            "SELECT COUNT(*) FROM suricata_events"
        ).fetchone()[0]

        alert_count = cursor.execute(
            "SELECT COUNT(*) FROM suricata_events WHERE event_type='alert'"
        ).fetchone()[0]

        hall_rows = cursor.execute("""
            SELECT timestamp, hall_value
            FROM hall_readings
            ORDER BY id DESC LIMIT 10
        """).fetchall()

        event_rows = cursor.execute("""
            SELECT timestamp, event_type, src_ip,
                   dest_ip, protocol, mqtt_topic
            FROM suricata_events
            ORDER BY id DESC LIMIT 15
        """).fetchall()

        # Classify recent Suricata alerts
        alert_rows = cursor.execute("""
            SELECT timestamp, src_ip, alert_signature, raw_json
            FROM suricata_events
            WHERE event_type = 'alert'
            ORDER BY id DESC LIMIT 10
        """).fetchall()

        classified_alerts = []
        informational_count = 0
        review_count = 0

        for timestamp, src_ip, signature, raw_json in alert_rows:

            try:
                event = json.loads(raw_json)
                alert = event.get("alert", {})

                if not isinstance(alert, dict):
                    alert = {}

                sid = alert.get("signature_id")
                signature = alert.get(
                    "signature", signature or "Unknown signature"
                )

                if sid in INFORMATIONAL_SIDS:
                    classification = "INFORMATIONAL"
                    informational_count += 1
                else:
                    classification = "REQUIRES REVIEW"
                    review_count += 1

            except (json.JSONDecodeError, TypeError):
                sid = None
                classification = "REQUIRES REVIEW"
                review_count += 1
                signature = signature or "Unable to parse alert"

            classified_alerts.append((
                timestamp,
                src_ip,
                sid,
                signature,
                classification
            ))

        # Early-warning data
        warning_count = 0
        open_warning_count = 0
        low_count = 0
        medium_count = 0
        high_count = 0
        warning_rows = []

        try:

            warning_count = cursor.execute(
                "SELECT COUNT(*) FROM security_warnings"
            ).fetchone()[0]

            open_warning_count = cursor.execute("""
                SELECT COUNT(*) FROM security_warnings
                WHERE UPPER(status) = 'OPEN'
            """).fetchone()[0]

            low_count, medium_count, high_count = cursor.execute("""
                SELECT
                    SUM(CASE WHEN UPPER(severity)='LOW' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN UPPER(severity)='MEDIUM' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN UPPER(severity)='HIGH' THEN 1 ELSE 0 END)
                FROM security_warnings
            """).fetchone()

            low_count = low_count or 0
            medium_count = medium_count or 0
            high_count = high_count or 0

            warning_rows = cursor.execute("""
                SELECT timestamp, category, severity, description,
                       status, related_flows, related_packets, related_bytes
                FROM security_warnings
                ORDER BY id DESC LIMIT 10
            """).fetchall()

        except sqlite3.OperationalError as error:
            print("Warning table temporarily unavailable:", error)

        return {
            "hall_count": hall_count,
            "latest_hall": latest_hall,
            "event_count": event_count,
            "alert_count": alert_count,
            "informational_count": informational_count,
            "review_count": review_count,
            "hall_rows": hall_rows,
            "event_rows": event_rows,
            "alert_rows": classified_alerts,
            "warning_count": warning_count,
            "open_warning_count": open_warning_count,
            "low_count": low_count,
            "medium_count": medium_count,
            "high_count": high_count,
            "warning_rows": warning_rows
        }

    finally:
        conn.close()


@app.route("/")
def dashboard():

    data = get_data()
    return render_template_string(HTML, **data)


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

