from flask import Flask, render_template_string
import sqlite3
import json

app = Flask(__name__)
DATABASE = "sensor_data.db"
INFORMATIONAL_SIDS = {2049201, 2049202}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="10">
<title>IoT Security Gateway | SOC Dashboard</title>

<style>
:root {
    --black: #101010;
    --panel: #ffffff;
    --background: #f2f2f2;
    --red: #d71920;
    --red-dark: #a90f16;
    --text: #171717;
    --muted: #777;
    --border: #e5e5e5;
    --green: #16834a;
    --amber: #b87500;
}

* { box-sizing: border-box; }

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: var(--background);
    color: var(--text);
}

header {
    background: var(--black);
    color: white;
    padding: 22px 30px;
    border-bottom: 4px solid var(--red);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.shield {
    background: var(--red);
    color: white;
    width: 46px;
    height: 46px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    font-size: 25px;
    font-weight: bold;
}

header h1 {
    margin: 0;
    font-size: 23px;
    letter-spacing: .5px;
}

header p {
    margin: 5px 0 0;
    color: #c8c8c8;
    font-size: 12px;
}

.system-status {
    color: #d8f5e3;
    background: #173b29;
    border: 1px solid #287348;
    border-radius: 20px;
    padding: 9px 14px;
    font-size: 12px;
    font-weight: bold;
}

.container {
    max-width: 1500px;
    margin: auto;
    padding: 24px;
}

.section-title {
    font-size: 17px;
    margin: 28px 0 14px;
    font-weight: bold;
    border-left: 4px solid var(--red);
    padding-left: 10px;
}

.high-panel {
    background: white;
    border: 1px solid #e6b5b5;
    border-left: 6px solid var(--red);
    border-radius: 9px;
    padding: 18px 20px;
    margin-bottom: 22px;
}

.high-panel.active {
    background: #fff1f1;
    border: 2px solid var(--red);
    border-left: 8px solid var(--red);
}

.high-heading {
    color: var(--red-dark);
    font-weight: bold;
    font-size: 16px;
    margin-bottom: 8px;
}

.high-empty {
    color: #555;
    font-size: 13px;
}

.high-item {
    padding: 10px 0;
    border-top: 1px solid #edcaca;
    font-size: 13px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 14px;
}

.card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 9px;
    padding: 18px;
    box-shadow: 0 2px 5px rgba(0,0,0,.035);
}

.card-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: .5px;
}

.card-value {
    font-size: 29px;
    font-weight: bold;
    margin-top: 12px;
    color: var(--black);
}

.card-value.red { color: var(--red); }

.severity-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
}

.severity-card {
    background: white;
    border-radius: 8px;
    padding: 17px;
    border: 1px solid var(--border);
}

.severity-card strong {
    display: block;
    font-size: 25px;
    margin-top: 7px;
}

.low { color: var(--green); }
.medium { color: var(--amber); }
.high { color: var(--red); }

.table-wrap {
    overflow-x: auto;
    background: white;
    border: 1px solid var(--border);
    border-radius: 9px;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 680px;
}

th, td {
    padding: 12px 13px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    font-size: 12px;
    vertical-align: top;
}

th {
    background: #171717;
    color: white;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .4px;
}

tr:last-child td { border-bottom: none; }

.badge {
    display: inline-block;
    padding: 5px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    white-space: nowrap;
}

.badge-high {
    background: #ffe0e0;
    color: #b00000;
}

.badge-medium {
    background: #fff0d1;
    color: #865000;
}

.badge-low {
    background: #e0f4e8;
    color: #176b3b;
}

.badge-info {
    background: #e9e9e9;
    color: #444;
}

.badge-simulation {
    background: #f0e8ff;
    color: #6233a0;
}

.note {
    color: var(--muted);
    font-size: 12px;
    margin: 8px 0 12px;
    line-height: 1.5;
}

.empty {
    padding: 18px;
    color: #777;
    font-size: 13px;
}

footer {
    text-align: center;
    padding: 22px;
    margin-top: 30px;
    background: var(--black);
    color: #c9c9c9;
    font-size: 11px;
}

@media (max-width: 600px) {
    header { padding: 18px; }
    header h1 { font-size: 19px; }
    .container { padding: 14px; }
    .severity-grid { grid-template-columns: 1fr; }
}
</style>
</head>

<body>
<header>
    <div class="brand">
        <div class="shield">S</div>
        <div>
            <h1>IoT SECURITY GATEWAY</h1>
            <p>AI-Enabled Edge Gateway for Intelligent IoT Network Security</p>
        </div>
    </div>
    <div class="system-status">● GATEWAY DASHBOARD ONLINE</div>
</header>

<div class="container">

    <div class="section-title">Critical Security Status</div>

    <div class="high-panel {% if high_count > 0 %}active{% endif %}">
        <div class="high-heading">HIGH-SEVERITY SECURITY WARNINGS</div>

        {% if high_count > 0 %}
            <p><strong>{{ high_count }}</strong> HIGH-severity warning(s) recorded.</p>
            {% for w in high_warning_rows %}
                <div class="high-item">
                    <strong>{{ w[0] }}</strong> — {{ w[1] }}<br>
                    {{ w[2] }}
                </div>
            {% endfor %}
        {% else %}
            <div class="high-empty">
                No HIGH-severity warnings currently recorded.
                The system will display HIGH warnings here when generated.
            </div>
        {% endif %}
    </div>

    <div class="section-title">Gateway Overview</div>

    <div class="cards">
        <div class="card">
            <div class="card-label">Hall Sensor Readings</div>
            <div class="card-value">{{ hall_count }}</div>
        </div>
        <div class="card">
            <div class="card-label">Latest Hall Value</div>
            <div class="card-value">{{ latest_hall }}</div>
        </div>
        <div class="card">
            <div class="card-label">Network Events</div>
            <div class="card-value">{{ event_count }}</div>
        </div>
        <div class="card">
            <div class="card-label">Suricata Alerts</div>
            <div class="card-value">{{ alert_count }}</div>
        </div>
        <div class="card">
            <div class="card-label">Total Warnings</div>
            <div class="card-value">{{ warning_count }}</div>
        </div>
        <div class="card">
            <div class="card-label">Open Warnings</div>
            <div class="card-value">{{ open_warning_count }}</div>
        </div>
    </div>

    <div class="section-title">Warning Severity Distribution</div>

    <div class="severity-grid">
        <div class="severity-card">
            <span class="low">LOW SEVERITY</span>
            <strong class="low">{{ low_count }}</strong>
        </div>
        <div class="severity-card">
            <span class="medium">MEDIUM SEVERITY</span>
            <strong class="medium">{{ medium_count }}</strong>
        </div>
        <div class="severity-card">
            <span class="high">HIGH SEVERITY</span>
            <strong class="high">{{ high_count }}</strong>
        </div>
    </div>

    <div class="section-title">Recent Network Activity</div>
    <div class="table-wrap">
        <table>
            <tr>
                <th>Time</th><th>Event</th><th>Source IP</th>
                <th>Destination IP</th><th>Protocol</th><th>MQTT Topic</th>
            </tr>
            {% for e in event_rows %}
            <tr>
                <td>{{ e[0] }}</td>
                <td>{{ e[1] }}</td>
                <td>{{ e[2] or '-' }}</td>
                <td>{{ e[3] or '-' }}</td>
                <td>{{ e[4] or '-' }}</td>
                <td>{{ e[5] or '-' }}</td>
            </tr>
            {% else %}
            <tr><td colspan="6">No network events available.</td></tr>
            {% endfor %}
        </table>
    </div>

    <div class="section-title">Suricata Security Alerts</div>
    <p class="note">
        Informational alerts and alerts requiring review are shown separately.
        An alert requiring review is not, by itself, proof of an attack.
    </p>
    <div class="table-wrap">
        <table>
            <tr>
                <th>Time</th><th>Source IP</th><th>Signature ID</th>
                <th>Alert Description</th><th>Classification</th>
            </tr>
            {% for a in alert_rows %}
            <tr>
                <td>{{ a[0] }}</td>
                <td>{{ a[1] or '-' }}</td>
                <td>{{ a[2] if a[2] is not none else '-' }}</td>
                <td>{{ a[3] }}</td>
                <td>
                    {% if a[4] == 'INFORMATIONAL' %}
                        <span class="badge badge-info">INFORMATIONAL</span>
                    {% else %}
                        <span class="badge badge-medium">REQUIRES REVIEW</span>
                    {% endif %}
                </td>
            </tr>
            {% else %}
            <tr><td colspan="5">No Suricata alerts available.</td></tr>
            {% endfor %}
        </table>
    </div>

    <div class="section-title">Security Warnings</div>
    <p class="note">
        These are monitoring indicators. Their classification does not automatically
        establish that a cyberattack has occurred. Classroom simulations are labelled.
    </p>
    <div class="table-wrap">
        <table>
            <tr>
                <th>Time</th><th>Category</th><th>Severity</th>
                <th>Description</th><th>Status</th>
            </tr>
            {% for w in warning_rows %}
            <tr>
                <td>{{ w[0] }}</td>
                <td>
                    {% if w[1] == 'MQTT_SECURITY_ANOMALY' %}
                        <span class="badge badge-simulation">CLASSROOM SIMULATION</span>
                    {% else %}
                        {{ w[1] }}
                    {% endif %}
                </td>
                <td>
                    {% if w[2]|upper == 'HIGH' %}
                        <span class="badge badge-high">HIGH</span>
                    {% elif w[2]|upper == 'MEDIUM' %}
                        <span class="badge badge-medium">MEDIUM</span>
                    {% else %}
                        <span class="badge badge-low">LOW</span>
                    {% endif %}
                </td>
                <td>{{ w[3] }}</td>
                <td>{{ w[4] }}</td>
            </tr>
            {% else %}
            <tr><td colspan="5">No security warnings available.</td></tr>
            {% endfor %}
        </table>
    </div>

    <div class="section-title">Recent Hall Sensor Readings</div>
    <div class="table-wrap">
        <table>
            <tr><th>Timestamp</th><th>Hall Sensor Value</th></tr>
            {% for h in hall_rows %}
            <tr><td>{{ h[0] }}</td><td>{{ h[1] }}</td></tr>
            {% else %}
            <tr><td colspan="2">No sensor readings available.</td></tr>
            {% endfor %}
        </table>
    </div>

</div>

<footer>
    RASPBERRY PI 4 EDGE GATEWAY | SURICATA IDS | MQTT | SQLITE
    <br>Dashboard refresh interval: 10 seconds
</footer>
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

                try:
                    sid_number = int(sid)
                except (TypeError, ValueError):
                    sid_number = None

                if sid_number in INFORMATIONAL_SIDS:
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
                timestamp, src_ip, sid, signature, classification
            ))

        warning_count = 0
        open_warning_count = 0
        low_count = 0
        medium_count = 0
        high_count = 0
        warning_rows = []
        high_warning_rows = []

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

            high_warning_rows = cursor.execute("""
                SELECT timestamp, category, description
                FROM security_warnings
                WHERE UPPER(severity) = 'HIGH'
                ORDER BY id DESC LIMIT 5
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
            "warning_rows": warning_rows,
            "high_warning_rows": high_warning_rows
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
