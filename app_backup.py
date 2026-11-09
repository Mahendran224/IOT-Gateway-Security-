
from flask import Flask, render_template_string, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "sensor_data.db"

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

        .container {
            padding: 25px;
        }

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

        table {
            width: 100%;
            border-collapse: collapse;
            background: #1d2c42;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #34445a;
            font-size: 13px;
        }

        th { color: #42d9c8; }

        .footer {
            text-align: center;
            padding: 20px;
            color: #a9bdd4;
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
            <h3>Suricata Alerts</h3>
            <div class="value">{{ alert_count }}</div>
        </div>

    </div>

    <h2>Recent Hall Sensor Readings</h2>

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
        {% endfor %}
    </table>

    <h2>Recent Network Events</h2>

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
        {% endfor %}
    </table>

    <h2>Security Alerts</h2>

    <table>
        <tr>
            <th>Timestamp</th>
            <th>Source IP</th>
            <th>Alert Signature</th>
        </tr>

        {% for row in alert_rows %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] or '-' }}</td>
            <td>{{ row[2] or '-' }}</td>
        </tr>
        {% endfor %}
    </table>

</div>

<div class="footer">
    Raspberry Pi 4 Edge Gateway | Suricata IDS | MQTT | SQLite
</div>

</body>
</html>
"""


def get_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

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

    alert_rows = cursor.execute("""
        SELECT timestamp, src_ip, alert_signature
        FROM suricata_events
        WHERE event_type='alert'
        ORDER BY id DESC LIMIT 10
    """).fetchall()

    conn.close()

    return (hall_count, latest_hall, event_count,
            alert_count, hall_rows, event_rows, alert_rows)


@app.route("/")
def dashboard():
    data = get_data()
    return render_template_string(
        HTML,
        hall_count=data[0],
        latest_hall=data[1],
        event_count=data[2],
        alert_count=data[3],
        hall_rows=data[4],
        event_rows=data[5],
        alert_rows=data[6]
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
