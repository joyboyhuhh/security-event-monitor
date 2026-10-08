# Security Event Monitoring Dashboard

A beginner-friendly local project that imports fictional security events into SQLite, applies a few explainable detection rules, and presents the results in a Flask dashboard. It is an educational portfolio project, not a production SIEM.

## Problem and data flow

Security teams review event logs to spot patterns that may need attention. This project demonstrates that workflow using safe, fictional records:

```text
Fictional CSV → validation and cleaning → SQLite events → rule detector → alerts → Flask API → dashboard
```

## Features

- CSV parsing with required-column, timestamp, IP, and required-field validation; rejected rows are reported with line numbers.
- SQLite event and alert tables with indexes, foreign keys, and parameterized queries.
- Repeatable ingestion and alert detection, with duplicate records suppressed.
- Flask JSON endpoints for summary statistics, events, alerts, top source IPs, and daily timeline counts.
- Responsive dark dashboard with alert cards, event table, source IP counts, and a simple timeline.
- Fictional sample data using documentation-only IP ranges.

## Detection rules

- **Brute Force (High):** five or more failed logins for one source IP in a rolling ten-minute window.
- **Repeated Failed Login (Medium):** three or four failed logins for one IP in a rolling ten-minute window.
- **Restricted Resource Access (Medium):** an event references a resource containing `restricted` or `admin`.
- **Privilege Escalation (High):** event type or event text indicates a privilege escalation attempt.
- **Suspicious Request (High):** event text contains one of the fictional patterns `../`, `<script`, or `union select`.

For failed-login bursts, matching events can each produce an alert. Each event/rule pair has a stable fingerprint with a unique database constraint, so rerunning detection does not re-create those alerts. Ingestion also fingerprints event content to avoid importing identical records twice.

## Technology

Python 3, Flask, SQLite, Pandas (CSV handling), HTML, CSS, JavaScript, and pytest.

## Project structure

```text
security-event-monitor/
├── app.py                 # Flask page and JSON API
├── config.py              # Project-relative paths and required CSV columns
├── database.py            # SQLite schema, connection, and transaction helper
├── detector.py            # Explainable alert rules
├── ingest.py              # CSV parsing, validation, and import
├── data/security_logs.csv # Fictional sample events
├── templates/index.html   # Dashboard markup
├── static/style.css       # Dashboard styling
├── static/dashboard.js    # API calls and dashboard rendering
├── tests/                 # Parser, detector, and API tests
├── requirements.txt
└── .gitignore
```

## Install (Windows PowerShell)

From this project directory:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

If PowerShell blocks activation, run the commands with `.venv\Scripts\python.exe` instead.

## Run

The database is created automatically by the importer, detector, and Flask app. Run these in order:

```powershell
py ingest.py
py detector.py
py app.py
```

Open `http://127.0.0.1:5000`. The sample CSV is `data/security_logs.csv`. The generated `security_events.db` is intentionally ignored by Git and can be recreated with the commands above.

API endpoints:

- `GET /api/stats`
- `GET /api/events?limit=100` (limit is capped at 500)
- `GET /api/alerts?severity=High&limit=100`
- `GET /api/top-ips`
- `GET /api/timeline`

## Tests

```powershell
py -m pytest
```

The tests use temporary databases and test CSV files rather than depending on the included sample data.

## Example results

The included CSV contains 178 fictional records spanning ten days. With the current rules and sample data, the dashboard shows 178 events, 6 unique IPs, and 6 alerts (3 High, 3 Medium). These counts describe the included fictional dataset only.

## Limitations

- All records are fictional and local; this does not monitor a live system or network.
- Detection is rule-based and only covers the patterns documented above.
- It is not a real enterprise SIEM, has no real-time ingestion, authentication, cloud deployment, or machine-learning detection.
- The Google Fonts stylesheet is optional presentation polish; the dashboard itself and API work without it.

## Future improvements

Possible extensions include configurable rules, streaming local log ingestion, authentication for a multi-user deployment, PostgreSQL, Docker, notification integrations, and carefully evaluated anomaly detection.
