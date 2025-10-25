## eBoi Web 🐂

Smart cattle monitoring and control platform built with Flask, PostgreSQL, and MQTT. It receives telemetry from ESP32 devices (GPS, motion, temperature, humidity), stores historical data, and provides an admin panel to manage users and devices, plus real‑time dashboards and remote commands.

This repository contains:

- A Flask web application (`app/`) with authentication, admin, MQTT ingestion, and dashboards
- Database SQL scripts (`database/`) for PostgreSQL provisioning and sample data
- Example ESP32 firmwares (`firmwares/`) to publish telemetry over MQTT

## Features

- Authentication (login/logout) and session handling
- Admin-only CRUD for users and device registrations
- Real-time data view powered by MQTT subscriptions
- Remote command page to publish messages to devices (MQTT)
- Historical logs:
  - Sensor warnings (temperature, humidity, motion)
  - Cattle geolocation history

## Architecture at a glance

- ESP32 devices publish telemetry to a public MQTT broker (default: broker.hivemq.com)
- Flask app subscribes to MQTT topics and persists values via SQLAlchemy in PostgreSQL
- Jinja2 templates render admin, profile, and telemetry pages

High level:

ESP32 firmware → MQTT broker ↔ Flask subscriber → PostgreSQL → Web UI

## Tech stack

- Python, Flask, Jinja2
- SQLAlchemy / Flask‑SQLAlchemy
- PostgreSQL (psycopg2)
- MQTT client: paho‑mqtt
- HTML/CSS templates (Bootstrap-like custom styles)

## Repository structure

```
app/
	app.py                # Flask app factory and routes registration
	models.py             # SQLAlchemy models (users, cattle, sensors, logs)
	config/
		db.py               # DB URI and SQLAlchemy config
		mqtt.py             # MQTT topics, subscriber loop, persistence
	admin/ auth/ general/ # Blueprints and routes
	templates/ static/    # Jinja templates and styles
database/
	script.sql            # Create DB and tables (PostgreSQL)
	populate.sql          # Seed sample data (admin user, etc.)
firmwares/
	gps-esp32.py          # GPS publisher (Micropython)
	warning-esp32.py      # Motion + DHT22 publisher (Micropython)
```

## Prerequisites

- Python 3.10+ recommended
- PostgreSQL 13+ (local or hosted)
- Internet access for the MQTT broker (default: public HiveMQ)

## Quick start (Windows PowerShell)

1. Clone and create a virtual environment

```powershell
git clone https://github.com/tuchanski/eboi.git
cd eboi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

If you have a `requirements.txt` (recommended):

```powershell
pip install -r requirements.txt
```

Or install the essentials directly:

```powershell
pip install Flask Flask-SQLAlchemy SQLAlchemy psycopg2-binary paho-mqtt
```

3. Configure PostgreSQL

- Create the database and tables:

```powershell
# Adjust the psql connection parameters as needed
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE \"eBoi\";"
psql -U postgres -h localhost -p 5432 -d eBoi -f .\database\script.sql
psql -U postgres -h localhost -p 5432 -d eBoi -f .\database\populate.sql
```

- Update credentials if needed in `app/config/db.py`:
  - DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

4. Review MQTT settings

- In `app/config/mqtt.py` you’ll find:
  - Broker: `MQTT_BROKER` (default broker.hivemq.com) and `MQTT_PORT`
  - Subscribed topics: `eboi/coordinates`, `eboi/temperature`, `eboi/humidity`, `eboi/motion`

Important: the example firmwares publish to `esp32/...` topics by default. Either:

- Change firmware topics to the `eboi/...` topics, or
- Change the app topics in `app/config/mqtt.py` to match `esp32/...`

Remote commands: the route `/comando-remoto` expects a publish topic constant named `MQTT_TOPIC_COMMAND`. Define it in `app/config/mqtt.py` and make your device subscribe to that same topic, for example:

```python
MQTT_TOPIC_COMMAND = "eboi/command"
```

5. Run the web app

```powershell
python .\app\app.py
```

You should see the server on http://localhost:8080.

## Default accounts (demo)

From `database/populate.sql` you’ll have an admin user:

- Email: `admin`
- Password: `admin`

## Key pages

- `/auth/login` – Login page
- `/` – Home
- `/dados-tempo-real` – Real-time data dashboard (login required)
- `/comando-remoto` – Send commands via MQTT (login required)
- `/historico-alerta` – Sensor warnings history
- `/historico-localizacao` – Cattle GPS history
- `/admin` – Admin area
  - Manage users, sensors, actuators

## Firmware notes (ESP32)

- `firmwares/gps-esp32.py`: publishes GPS coordinates via Micropython (`micropyGPS`, `umqtt.simple`).
- `firmwares/warning-esp32.py`: publishes motion (PIR) and DHT22 temperature/humidity.

Before flashing:

- Fill your Wi‑Fi SSID and password in the scripts
- Align MQTT topics with the app configuration (see “Review MQTT settings”)

## Troubleshooting

- Psycopg2 on Windows: prefer `psycopg2-binary` in development. If build errors appear, install Visual C++ Build Tools or use WSL.
- Cannot connect to DB: verify `app/config/db.py` matches your PostgreSQL credentials, and that the `eBoi` database exists.
- No telemetry showing up: ensure MQTT topics match between firmware and `app/config/mqtt.py`, and the broker is reachable from both sides.
- Remote command errors: make sure `MQTT_TOPIC_COMMAND` is defined in `app/config/mqtt.py` and your device subscribes to it.
- Port already in use: change `host/port` at the bottom of `app/app.py`.

## Security and production notes

- Replace plain-text passwords with hashed passwords (e.g., `werkzeug.security.generate_password_hash`).
- Consider environment variables for DB/MQTT config instead of hardcoding.
- Use a private MQTT broker for production.
- Run behind a production WSGI server (gunicorn/uwsgi) and a reverse proxy (nginx), and disable Flask debug.

## Acknowledgements

- HiveMQ public broker for quick MQTT testing
- Flask, SQLAlchemy, and the Python community
