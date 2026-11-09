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
    --bg:#090f1c;
    --sidebar:#0d1627;
    --panel:#131f32;
    --panel2:#1b2a40;
    --border:#293b55;
    --text:#edf3fc;
    --muted:#94a6bd;
    --red:#ff5368;
    --green:#42d6a0;
    --amber:#ffbd59;
    --blue:#55b5ff;
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

/* Refined SOC visual treatment */
body {
    background:
      radial-gradient(ellipse at 80% 0%, #14243b 0%, transparent 38%),
      var(--bg);
    color:var(--text);
}
.sidebar {
    background:linear-gradient(180deg,#101d31 0%,#0b1423 100%);
    border-right:1px solid #263b57;
}
.logo-icon {
    background:linear-gradient(135deg,#193e63,#174d69);
    color:#7ed0ff;
    box-shadow:0 0 18px #278ac533;
}
.topbar {
    background:rgba(13,22,39,.96);
    border-bottom:1px solid #293d59;
    backdrop-filter:blur(12px);
}
.card,.severity-card,.table-wrap,.status-panel {
    background:linear-gradient(145deg,#17263b,#111c2e);
    border:1px solid #2a405d;
    box-shadow:0 5px 18px #02081744;
}
.card {
    transition:border-color .2s ease,transform .2s ease;
}
.card:hover {
    border-color:#4d83b2;
    transform:translateY(-2px);
}
.card-label {
    color:#9eb1c9;
}
.card-value {
    letter-spacing:-.5px;
}
.section-title {
    color:#e9f2ff;
    letter-spacing:1px;
}
.section-title:before {
    background:linear-gradient(180deg,#62c8ff,#387dff);
    box-shadow:0 0 9px #55b5ff66;
}
th {
    background:#1c2d45;
    color:#a9c2df;
}
td {
    color:#d4deeb;
}
tr:hover td {
    background:#20334b;
}
.event-message {
    font-size:10px;
    line-height:1.5;
    color:#b9c8da;
    max-width:380px;
    overflow-wrap:anywhere;
}
.badge-low {
    background:#123d35;
    color:#58e3b1;
}
.badge-medium {
    background:#47351c;
    color:#ffd080;
}
.badge-high {
    background:#49202c;
    color:#ff8293;
}
.badge-simulation {
    background:#30264d;
    color:#c9b3ff;
}
.nav a:hover,.nav a.active {
    background:#1b304a;
    border-left-color:#55b5ff;
}
.status {
    border-color:#28634f;
    background:#102f29;
    box-shadow:0 0 14px #32c48d12;
}
.status-panel.normal {
    border-left-color:var(--green);
}
.status-panel.active {
    border-left-color:var(--red);
}
footer {
    color:#8498b2;
    border-color:#293d59;
}


/* IOT SENTINEL PREMIUM BLUE GRADIENT THEME */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg:#02040b;
    --sidebar:rgba(5,10,24,.82);
    --panel:rgba(8,17,39,.72);
    --panel2:rgba(13,30,62,.78);
    --border:rgba(115,164,255,.19);
    --text:#f4f7ff;
    --muted:#a2b2ce;
    --red:#ff647d;
    --green:#50e0b0;
    --amber:#ffd078;
    --blue:#65baff;
}

html {
    scroll-behavior:smooth;
    scroll-padding-top:95px;
}

body {
    min-height:100vh;
    background:
        linear-gradient(
            180deg,
            #020204 0%,
            #030611 22%,
            #06112b 47%,
            #071b50 72%,
            #073fc0 100%
        );
    background-attachment:fixed;
    color:#f4f7ff;
    font-family:'DM Sans','Inter',Arial,sans-serif;
    font-size:13px;
    letter-spacing:.05px;
}

body::before {
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    z-index:-1;
    background:
        radial-gradient(ellipse at 50% 100%,rgba(20,91,255,.22),transparent 48%),
        radial-gradient(ellipse at 90% 55%,rgba(34,91,210,.10),transparent 42%);
}

.layout {
    position:relative;
}

.sidebar {
    background:rgba(3,7,18,.84);
    border-right:1px solid rgba(130,170,255,.16);
    backdrop-filter:blur(22px);
    -webkit-backdrop-filter:blur(22px);
    box-shadow:12px 0 45px rgba(0,0,0,.16);
    z-index:10;
}

.logo {
    border-color:rgba(130,170,255,.16);
    padding-bottom:25px;
}

.logo-icon {
    width:42px;
    height:42px;
    border-radius:13px;
    background:linear-gradient(145deg,#164d9d,#087ce9);
    color:#fff;
    font-family:'Space Grotesk',sans-serif;
    box-shadow:0 0 25px rgba(36,126,255,.32);
}

.logo strong {
    font-family:'Space Grotesk',sans-serif;
    font-size:16px;
    letter-spacing:1.2px;
    color:#f5f8ff;
}

.logo small {
    color:#8ea9d2;
    letter-spacing:1.5px;
    font-size:9px;
}

.nav-title {
    color:#7188ad;
    letter-spacing:2px;
    font-size:9px;
}

.nav a {
    color:#a6b6d0;
    border:1px solid transparent;
    border-left:3px solid transparent;
    border-radius:9px;
    padding:12px 11px;
    transition:all .22s ease;
}

.nav a:hover {
    color:#fff;
    background:rgba(39,103,207,.15);
    border-color:rgba(92,155,255,.12);
    border-left-color:#5eaeff;
    transform:translateX(3px);
}

.nav a.active {
    color:#fff;
    background:linear-gradient(100deg,rgba(31,105,220,.28),rgba(24,66,130,.10));
    border:1px solid rgba(91,159,255,.19);
    border-left:3px solid #55aaff;
    box-shadow:inset 0 0 20px rgba(42,117,235,.07);
}

.sidebar-bottom {
    border-color:rgba(130,170,255,.16);
    color:#8299bc;
    letter-spacing:.7px;
}

.main {
    min-height:100vh;
}

.topbar {
    height:82px;
    background:rgba(3,7,17,.76);
    border-bottom:1px solid rgba(130,170,255,.17);
    backdrop-filter:blur(22px);
    -webkit-backdrop-filter:blur(22px);
    padding:0 34px;
}

.topbar h1 {
    font-family:'Space Grotesk','DM Sans',sans-serif;
    font-size:21px;
    font-weight:600;
    letter-spacing:-.55px;
    color:#f5f8ff;
}

.topbar p {
    color:#9aafd0;
    font-size:11px;
    letter-spacing:.2px;
}

.status {
    background:rgba(20,111,81,.17);
    border:1px solid rgba(69,224,169,.35);
    color:#6aebbd;
    border-radius:30px;
    padding:9px 15px;
    font-size:9px;
    letter-spacing:1px;
    box-shadow:0 0 22px rgba(44,210,151,.08);
}

.content {
    padding:30px 34px 42px;
}

.section-title {
    font-family:'Space Grotesk','DM Sans',sans-serif;
    font-size:12px;
    font-weight:600;
    letter-spacing:1.5px;
    color:#e8f1ff;
    margin-top:32px;
    margin-bottom:16px;
}

.section-title:before {
    width:3px;
    height:17px;
    background:linear-gradient(180deg,#65c7ff,#3475ff);
    box-shadow:0 0 13px rgba(74,160,255,.7);
}

.cards {
    gap:15px;
}

.card,.severity-card,.status-panel,.table-wrap {
    background:linear-gradient(
        145deg,
        rgba(12,27,57,.84),
        rgba(5,14,34,.76)
    );
    border:1px solid rgba(124,169,255,.19);
    border-radius:13px;
    box-shadow:
        0 12px 32px rgba(0,0,0,.18),
        inset 0 1px 0 rgba(255,255,255,.035);
    backdrop-filter:blur(16px);
    -webkit-backdrop-filter:blur(16px);
}

.card {
    min-height:116px;
    padding:20px;
    position:relative;
    overflow:hidden;
    transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease;
}

.card::after {
    content:"";
    position:absolute;
    width:110px;
    height:110px;
    right:-48px;
    bottom:-65px;
    border-radius:50%;
    background:rgba(42,120,255,.12);
    filter:blur(22px);
    pointer-events:none;
}

.card:hover {
    transform:translateY(-4px);
    border-color:rgba(91,170,255,.48);
    box-shadow:0 17px 38px rgba(0,0,0,.25),0 0 24px rgba(43,119,255,.08);
}

.card-label {
    color:#9fb4d5;
    font-size:10px;
    letter-spacing:1px;
    font-weight:600;
}

.card-value {
    font-family:'Space Grotesk','DM Sans',sans-serif;
    font-size:31px;
    font-weight:600;
    letter-spacing:-1.1px;
    color:#f4f8ff;
    margin-top:15px;
    font-variant-numeric:tabular-nums;
}

.card-value.red {color:#ff7187}
.card-value.green {color:#55e3b4}
.card-value.amber {color:#ffd078}

.status-panel {
    padding:20px 23px;
}

.status-panel.normal {
    border-left:3px solid #50e0b0;
}

.status-panel.active {
    border-left:3px solid #ff647d;
}

.status-heading {
    font-family:'Space Grotesk',sans-serif;
    font-size:14px;
    font-weight:600;
}

.status-detail {
    color:#a4b7d6;
    line-height:1.8;
}

.status-count {
    font-family:'Space Grotesk',sans-serif;
    font-size:31px;
}

.severity-grid {
    gap:15px;
}

.severity-card {
    padding:19px;
    transition:transform .2s ease,border-color .2s ease;
}

.severity-card:hover {
    transform:translateY(-3px);
    border-color:rgba(112,167,255,.43);
}

.severity-card span {
    letter-spacing:1.4px;
}

.severity-card strong {
    font-family:'Space Grotesk',sans-serif;
    font-size:29px;
    font-variant-numeric:tabular-nums;
}

.table-wrap {
    overflow:hidden;
}

table {
    min-width:650px;
}

th {
    background:rgba(22,48,91,.76);
    color:#a9c5ed;
    font-size:9px;
    letter-spacing:1px;
    padding:15px 15px;
}

th,td {
    border-bottom:1px solid rgba(126,165,226,.12);
    padding:14px 15px;
    font-size:11px;
}

td {
    color:#d4e0f3;
    line-height:1.5;
}

tr:hover td {
    background:rgba(44,104,194,.13);
}

.event-message {
    color:#c1d0e8;
    line-height:1.65;
}

.badge {
    border-radius:20px;
    padding:5px 10px;
    letter-spacing:.5px;
}

.badge-low {
    background:rgba(30,169,123,.16);
    color:#65e8bc;
    border:1px solid rgba(75,220,170,.2);
}

.badge-medium {
    background:rgba(211,147,44,.15);
    color:#ffd17e;
    border:1px solid rgba(255,190,82,.2);
}

.badge-high {
    background:rgba(224,67,92,.16);
    color:#ff8799;
    border:1px solid rgba(255,100,125,.2);
}

.badge-simulation {
    background:rgba(139,94,220,.16);
    color:#d0b7ff;
    border:1px solid rgba(170,130,255,.2);
}

.badge-info {
    background:rgba(67,139,231,.16);
    color:#9bcaff;
}

.empty {
    color:#91a8cb;
    padding:22px;
}

footer {
    border-color:rgba(130,170,255,.17);
    color:#9aafd0;
    letter-spacing:.8px;
    line-height:1.8;
}

@media(max-width:1050px) {
    .content {padding:24px 20px 35px}
    .topbar {padding:0 22px}
}

@media(max-width:700px) {
    .sidebar {
        background:rgba(3,7,18,.94);
    }
    .topbar {
        height:70px;
        padding:0 13px;
    }
    .topbar h1 {font-size:15px}
    .content {padding:16px 12px 28px}
    .card {min-height:100px}
    .card-value {font-size:24px}
    .section-title {font-size:11px}
}

@media(prefers-reduced-motion:reduce) {
    *,*::before,*::after {
        scroll-behavior:auto !important;
        transition:none !important;
    }
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
        <th>Alert Signature</th></tr>
        {% for a in alert_rows %}
        <tr><td>{{ a[0] }}</td><td>{{ a[1] or '-' }}</td>
        <td>{{ a[2] if a[2] is not none else '-' }}</td>
        <td class="event-message" title="{{ a[3] }}">{{ a[3] }}</td></tr>
        {% else %}<tr><td colspan="4" class="empty">No IDS alerts</td></tr>
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
        </td><td class="event-message" title="{{ w[3] }}">{{ w[3] }}</td><td>{{ w[4] }}</td></tr>
        {% else %}<tr><td colspan="5" class="empty">No security events</td></tr>
        {% endfor %}
    </table></div>
</section>

<section id="mqtt">
    <div class="section-title">UNEXPECTED MQTT TRAFFIC</div>
    <div class="table-wrap"><table>
        <tr><th>Time</th><th>Source IP</th><th>Destination IP</th>
        <th>Topic</th><th>Message</th></tr>
        {% for m in unexpected_mqtt_rows %}
        <tr><td>{{ m[0] }}</td><td>{{ m[1] or '-' }}</td>
        <td>{{ m[2] or '-' }}</td><td>{{ m[3] or 'Unknown' }}</td>
        <td class="event-message" title="{{ m[4] }}">{{ m[4] or '-' }}</td></tr>
        {% else %}<tr><td colspan="5" class="empty">No unexpected MQTT messages</td></tr>
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
