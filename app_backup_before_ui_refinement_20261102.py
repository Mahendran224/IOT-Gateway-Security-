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
<title>IoT Sentinel | Security Operations Center</title>
<style>
:root {
    --bg:#0b0e14;
    --sidebar:#10151e;
    --panel:#151b26;
    --panel2:#1a2230;
    --border:#273142;
    --text:#e8edf5;
    --muted:#8995a8;
    --red:#ed4354;
    --green:#32c48d;
    --amber:#e9aa43;
    --blue:#58a6ff;
}
* {box-sizing:border-box}
body {
    margin:0;background:var(--bg);color:var(--text);
    font-family:Inter,Segoe UI,Arial,sans-serif;font-size:13px;
}
.layout {display:flex;min-height:100vh}
.sidebar {
    width:235px;flex-shrink:0;background:var(--sidebar);
    border-right:1px solid var(--border);padding:25px 15px;
    position:fixed;top:0;bottom:0;left:0;
}
.logo {display:flex;align-items:center;gap:12px;padding:0 10px 28px;
       border-bottom:1px solid var(--border)}
.logo-icon {
    width:39px;height:39px;border-radius:10px;background:#401c28;
    color:#ff596b;display:grid;place-items:center;font-size:21px;font-weight:800;
}
.logo strong {font-size:15px;letter-spacing:1px}
.logo small {display:block;color:var(--muted);font-size:10px;margin-top:4px}
.nav-title {color:#657287;font-size:10px;font-weight:700;
            letter-spacing:1.5px;padding:25px 12px 10px}
.nav a {
    display:block;padding:12px;border-radius:7px;color:#9aa7b9;
    text-decoration:none;margin:3px 0;font-size:12px;
}
.nav a:hover,.nav a.active {
    color:white;background:#242b39;border-left:3px solid var(--red);
}
.sidebar-bottom {
    position:absolute;bottom:22px;left:22px;right:22px;
    border-top:1px solid var(--border);padding-top:15px;
    color:var(--muted);font-size:10px;line-height:1.8;
}
.main {margin-left:235px;width:calc(100% - 235px);min-width:0}
.topbar {
    height:75px;background:#10151e;border-bottom:1px solid var(--border);
    display:flex;align-items:center;justify-content:space-between;
    padding:0 30px;position:sticky;top:0;z-index:5;
}
.topbar h1 {font-size:17px;margin:0;font-weight:650;letter-spacing:.3px}
.topbar p {font-size:11px;color:var(--muted);margin:5px 0 0}
.status {
    border:1px solid #225d48;background:#122c25;color:var(--green);
    padding:8px 13px;border-radius:6px;font-size:10px;font-weight:700;
    letter-spacing:.5px;
}
.content {padding:25px 30px 35px;max-width:1600px;margin:auto}
.section-title {
    font-size:13px;font-weight:700;letter-spacing:.5px;
    margin:25px 0 13px;color:#dce4ef;
    display:flex;align-items:center;gap:9px;
}
.section-title:before {
    content:"";width:3px;height:16px;background:var(--red);border-radius:3px;
}
.cards {
    display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;
}
.card {
    background:var(--panel);border:1px solid var(--border);
    border-radius:9px;padding:18px;min-height:105px;
}
.card-label {
    color:var(--muted);font-size:10px;font-weight:700;
    letter-spacing:.8px;text-transform:uppercase;
}
.card-value {font-size:28px;font-weight:700;margin-top:13px;color:#f2f5fa}
.card-value.red {color:var(--red)}
.card-value.green {color:var(--green)}
.card-value.amber {color:var(--amber)}
.status-panel {
    background:var(--panel);border:1px solid var(--border);
    border-radius:9px;padding:17px 20px;display:flex;
    justify-content:space-between;align-items:center;gap:15px;
}
.status-panel.active {border-left:4px solid var(--red)}
.status-panel.normal {border-left:4px solid var(--green)}
.status-heading {font-size:13px;font-weight:700}
.status-detail {font-size:11px;color:var(--muted);margin-top:6px}
.status-count {font-size:26px;font-weight:750;color:var(--red)}
.severity-grid {display:grid;grid-template-columns:repeat(3,1fr);gap:13px}
.severity-card {
    background:var(--panel);border:1px solid var(--border);
    padding:16px;border-radius:8px;
}
.severity-card span {font-size:10px;font-weight:700;letter-spacing:.7px}
.severity-card strong {display:block;font-size:25px;margin-top:8px}
.low {color:var(--green)} .medium {color:var(--amber)} .high {color:var(--red)}
.table-wrap {
    overflow-x:auto;background:var(--panel);
    border:1px solid var(--border);border-radius:9px;
}
table {width:100%;border-collapse:collapse;min-width:650px}
th {
    background:#1b2331;color:#8f9db1;font-size:10px;
    letter-spacing:.7px;text-transform:uppercase;font-weight:700;
}
th,td {
    padding:12px 14px;text-align:left;border-bottom:1px solid var(--border);
    font-size:11px;vertical-align:top;
}
td {color:#cbd4e1}
tr:last-child td {border-bottom:0}
tr:hover td {background:#1b2432}
.badge {
    display:inline-block;padding:5px 8px;border-radius:4px;
    font-size:9px;font-weight:750;white-space:nowrap;
}
.badge-high {background:#48202a;color:#ff7885}
.badge-medium {background:#46351d;color:#f0bd66}
.badge-low {background:#173c32;color:#58d6a8}
.badge-info {background:#263449;color:#8ebcff}
.badge-simulation {background:#33254a;color:#c5a3ff}
.empty {padding:18px;color:var(--muted);font-size:11px}
footer {
    border-top:1px solid var(--border);padding:18px 0;
    margin-top:30px;color:#69778a;font-size:10px;
}
@media(max-width:1050px) {
    .cards {grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:700px) {
    .sidebar {width:62px;padding:18px 7px}
    .logo {padding:0 3px 20px}
    .logo div:last-child,.nav-title,.nav a span,.sidebar-bottom {display:none}
    .logo-icon {width:42px}
    .nav a {font-size:0;text-align:center;padding:13px 2px}
    .nav a:before {content:"•";font-size:19px}
    .main {margin-left:62px;width:calc(100% - 62px)}
    .content {padding:17px 12px}
    .topbar {padding:0 13px}
    .topbar h1 {font-size:13px}
    .status {font-size:9px;padding:7px}
    .cards {grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
    .card {padding:13px}
    .card-value {font-size:23px}
    .severity-grid {gap:7px}
    .severity-card {padding:10px}
}
</style>
</head>
<body>
<div class="layout">
<aside class="sidebar">
    <div class="logo">
        <div class="logo-icon">S</div>
        <div><strong>IOT SENTINEL</strong><small>SECURITY OPERATIONS</small></div>
    </div>
    <div class="nav-title">MONITORING</div>
    <nav class="nav">
        <a class="active" href="#overview"><span>◈ &nbsp; Overview</span></a>
        <a href="#network"><span>⌁ &nbsp; Network Activity</span></a>
        <a href="#ids"><span>◉ &nbsp; IDS Alerts</span></a>
        <a href="#warnings"><span>⚑ &nbsp; Security Events</span></a>
        <a href="#mqtt"><span>▣ &nbsp; MQTT Traffic</span></a>
        <a href="#sensors"><span>⌁ &nbsp; Sensor Data</span></a>
    </nav>
    <div class="sidebar-bottom">
        EDGE GATEWAY<br>
        RASPBERRY PI 4<br>
        <span style="color:var(--green)">● MONITORING ACTIVE</span>
    </div>
</aside>

<main class="main">
<header class="topbar">
    <div>
        <h1>Security Overview</h1>
        <p>IoT Network Monitoring &amp; Threat Visibility</p>
    </div>
    <div class="status">● GATEWAY ONLINE</div>
</header>

<div class="content">
<section id="overview">
    <div class="section-title">GATEWAY OVERVIEW</div>
    <div class="cards">
        <div class="card"><div class="card-label">Sensor Readings</div>
            <div class="card-value">{{ hall_count }}</div></div>
        <div class="card"><div class="card-label">Latest Hall Value</div>
            <div class="card-value">{{ latest_hall }}</div></div>
        <div class="card"><div class="card-label">Network Events</div>
            <div class="card-value">{{ event_count }}</div></div>
        <div class="card"><div class="card-label">Suricata IDS Alerts</div>
            <div class="card-value red">{{ alert_count }}</div></div>
        <div class="card"><div class="card-label">Total Warnings</div>
            <div class="card-value">{{ warning_count }}</div></div>
        <div class="card"><div class="card-label">Open Warnings</div>
            <div class="card-value amber">{{ open_warning_count }}</div></div>
        <div class="card"><div class="card-label">Unexpected MQTT</div>
            <div class="card-value red">{{ unexpected_mqtt_count }}</div></div>
    </div>

    <div class="section-title">SECURITY STATUS</div>
    <div class="status-panel {% if high_count > 0 %}active{% else %}normal{% endif %}">
        <div>
            <div class="status-heading">
                {% if high_count > 0 %}HIGH-SEVERITY WARNINGS{% else %}NO HIGH-SEVERITY WARNINGS{% endif %}
            </div>
            <div class="status-detail">
                {% if high_count > 0 %}
                    {% for w in high_warning_rows %}
                        {{ w[0] }} &nbsp; | &nbsp; {{ w[1] }}<br>
                    {% endfor %}
                {% else %}
                    Gateway monitoring operational
                {% endif %}
            </div>
        </div>
        <div class="status-count">{{ high_count }}</div>
    </div>

    <div class="section-title">WARNING SEVERITY</div>
    <div class="severity-grid">
        <div class="severity-card"><span class="low">LOW</span>
            <strong class="low">{{ low_count }}</strong></div>
        <div class="severity-card"><span class="medium">MEDIUM</span>
            <strong class="medium">{{ medium_count }}</strong></div>
        <div class="severity-card"><span class="high">HIGH</span>
            <strong class="high">{{ high_count }}</strong></div>
    </div>
</section>

<section id="network">
    <div class="section-title">RECENT NETWORK ACTIVITY</div>
    <div class="table-wrap"><table>
        <tr><th>Time</th><th>Event</th><th>Source IP</th>
        <th>Destination IP</th><th>Protocol</th><th>MQTT Topic</th></tr>
        {% for e in event_rows %}
        <tr><td>{{ e[0] }}</td><td>{{ e[1] }}</td>
        <td>{{ e[2] or '-' }}</td><td>{{ e[3] or '-' }}</td>
        <td>{{ e[4] or '-' }}</td><td>{{ e[5] or '-' }}</td></tr>
        {% else %}<tr><td colspan="6" class="empty">No network events</td></tr>
        {% endfor %}
    </table></div>
</section>

<section id="ids">
    <div class="section-title">SURICATA IDS ALERTS</div>
    <div class="table-wrap"><table>
        <tr><th>Time</th><th>Source IP</th><th>Signature ID</th>
        <th>Alert Signature</th><th>Classification</th></tr>
        {% for a in alert_rows %}
        <tr><td>{{ a[0] }}</td><td>{{ a[1] or '-' }}</td>
        <td>{{ a[2] if a[2] is not none else '-' }}</td><td>{{ a[3] }}</td>
        <td>{% if a[4] == 'INFORMATIONAL' %}
            <span class="badge badge-info">INFORMATIONAL</span>
            {% else %}<span class="badge badge-medium">REQUIRES REVIEW</span>{% endif %}
        </td></tr>
        {% else %}<tr><td colspan="5" class="empty">No IDS alerts</td></tr>
        {% endfor %}
    </table></div>
</section>

<section id="warnings">
    <div class="section-title">SECURITY EVENTS</div>
    <div class="table-wrap"><table>
        <tr><th>Time</th><th>Category</th><th>Severity</th>
        <th>Event</th><th>Status</th></tr>
        {% for w in warning_rows %}
        <tr><td>{{ w[0] }}</td><td>
            {% if w[1] == 'MQTT_SECURITY_ANOMALY' %}
                <span class="badge badge-simulation">SIMULATION</span>
            {% else %}{{ w[1] }}{% endif %}
        </td><td>
            {% if w[2]|upper == 'HIGH' %}
                <span class="badge badge-high">HIGH</span>
            {% elif w[2]|upper == 'MEDIUM' %}
                <span class="badge badge-medium">MEDIUM</span>
            {% else %}<span class="badge badge-low">LOW</span>{% endif %}
        </td><td>{{ w[3] }}</td><td>{{ w[4] }}</td></tr>
        {% else %}<tr><td colspan="5" class="empty">No security events</td></tr>
        {% endfor %}
    </table></div>
</section>

<section id="mqtt">
    <div class="section-title">UNEXPECTED MQTT TRAFFIC</div>
    <div class="table-wrap"><table>
        <tr><th>Time</th><th>Source IP</th><th>Destination IP</th>
        <th>Topic</th><th>Message</th><th>Classification</th></tr>
        {% for m in unexpected_mqtt_rows %}
        <tr><td>{{ m[0] }}</td><td>{{ m[1] or '-' }}</td>
        <td>{{ m[2] or '-' }}</td><td>{{ m[3] or 'Unknown' }}</td>
        <td>{{ m[4] or '-' }}</td>
        <td><span class="badge badge-medium">UNEXPECTED</span></td></tr>
        {% else %}<tr><td colspan="6" class="empty">No unexpected MQTT messages</td></tr>
        {% endfor %}
    </table></div>
</section>

<section id="sensors">
    <div class="section-title">HALL SENSOR READINGS</div>
    <div class="table-wrap"><table>
        <tr><th>Timestamp</th><th>Hall Sensor Value</th></tr>
        {% for h in hall_rows %}
        <tr><td>{{ h[0] }}</td><td>{{ h[1] }}</td></tr>
        {% else %}<tr><td colspan="2" class="empty">No sensor readings</td></tr>
        {% endfor %}
    </table></div>
</section>

<footer>RASPBERRY PI 4 &nbsp; | &nbsp; SURICATA IDS &nbsp; | &nbsp; MQTT &nbsp; | &nbsp; SQLITE
&nbsp; | &nbsp; AUTO REFRESH: 10 SEC</footer>
</div>
</main>
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

        unexpected_mqtt_count = cursor.execute("""
            SELECT COUNT(*) FROM suricata_events
            WHERE event_type = 'mqtt'
            AND (mqtt_topic IS NULL OR mqtt_topic != 'iot/sensor')
        """).fetchone()[0]

        unexpected_mqtt_rows = cursor.execute("""
            SELECT timestamp, src_ip, dest_ip, mqtt_topic, mqtt_message
            FROM suricata_events
            WHERE event_type = 'mqtt'
            AND (mqtt_topic IS NULL OR mqtt_topic != 'iot/sensor')
            ORDER BY id DESC LIMIT 20
        """).fetchall()

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
            "unexpected_mqtt_count": unexpected_mqtt_count,
            "unexpected_mqtt_rows": unexpected_mqtt_rows,
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
