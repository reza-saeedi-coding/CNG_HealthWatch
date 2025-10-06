# CNG HealthWatch — RUNBOOK

This guide explains how to install, run, and verify the CNG HealthWatch monitoring pipeline.

---

## Table of Contents
- [Quick start](#quick-start)
- [Run the full pipeline (MQTT mode)](#run-the-full-pipeline-mqtt-mode)
- [Publish a test message (manual check)](#publish-a-test-message-manual-check)
- [Health check (smoke test)](#health-check-smoke-test)
- [Logs](#logs)
- [Exports](#exports)
- [Dashboard (Streamlit)](#dashboard-streamlit)
- [Common pitfalls](#common-pitfalls)
- [Config files](#config-files)
- [DB adapter (SQLite now, MSSQL later)](#db-adapter-sqlite-now-mssql-later)

---

## Quick start

Set up Python environment and install dependencies (first time only):

```powershell
git clone <repo-url>
cd CNG_HealthWatch
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# one-time: create .env from the template
Copy-Item .env.example .env -Force
````

---

## Run the full pipeline (MQTT mode)

Start everything (subscriber, transformer, analyzer, exporter):

```powershell
cd C:\Users\Dell\PycharmProjects\CNG_HealthWatch
.\.venv\Scripts\activate
python -m scripts.run_full_pipeline
```

What starts:

* MQTT subscriber → writes to `sensor_logs`
* Transformer → fills `processed_logs`
* Analyzer (every 60s) → writes to `anomalies`
* Export loop (every 5 min) → CSVs in `data\exports\`

---

## Publish a test message (manual check)

Send one telemetry record to MQTT and confirm it appears in the DB:

```powershell
.\.venv\Scripts\python.exe -m tests.publish_once
```

Expected:

* Console prints `published...` and ✅ insert detected
* Subscriber log shows `row inserted`

---

## Health check (smoke test)

Verify DB tables have fresh rows and pipeline is healthy:

```powershell
.\.venv\Scripts\python.exe -m tests.smoke_test
```

Output shows row counts and latest timestamps:

* Exit code `0` = healthy
* Exit code `1` = problem (empty or stale tables, missing DB)

---

## Logs

Logs are written to `data/logs/`. Key files:

* `mqtt_subscriber.log` → raw ingest from MQTT
* `transform_logs.log` → processing and enrichment
* `analyzer.log` → anomaly detection
* `export.log` → CSV export jobs

Tail a log in PowerShell:

```powershell
Get-Content .\data\logs\mqtt_subscriber.log -Tail 50 -Wait
```

---

## Exports

Summary CSV files are saved under `data/exports/`.
They include:

* `avg_pressure_by_hour.csv`
* `avg_temperature_by_hour.csv`
* `compressor_transitions_by_day.csv`
* `anomalies.csv` (detected anomalies)

These can be opened in Excel, Power BI, or Grafana for visualization.

---

## Dashboard (Streamlit)

To view the live dashboard:

```powershell
streamlit run dashboard.py
```

This shows:

* Current sensor metrics
* Summary charts
* Anomalies

---

## Common pitfalls

* **No “row inserted” after publish:**

  * Subscriber not running, or topic mismatch with publisher
  * Broker unreachable (network / firewall)
* **Smoke test says “stale”:**

  * Only subscriber running; start full pipeline so transformer/analyzer loops update tables
* **Where are logs?**

  * MQTT subscriber: `data\logs\mqtt_subscriber.log` (tail with PowerShell)

---

## Config files

* `.env` → created from `.env.example`, stores MQTT host, topic, DB_URL, etc.
* `requirements.txt` → Python dependencies (`pip install -r requirements.txt`)
* (optional later) `docker-compose.yml` → to run the pipeline in containers

---

## DB adapter (SQLite now, MSSQL later)

The code uses `core.db.get_connection()` so the DB backend is chosen by `DB_URL`.

* **Local dev (default):**

  ```
  DB_URL=sqlite:///./data/sensor_data.db
  ```

* **MS-SQL (later, on SAFE server):**

  1. Install `pyodbc` and the SQL Server ODBC driver (e.g., “ODBC Driver 17 for SQL Server”).
  2. Set in `.env`:

     ```
     DB_URL=mssql+pyodbc://USER:PASS@SERVER:1433/DBNAME?driver=ODBC+Driver+17+for+SQL+Server
     ```
  3. Restart the pipeline. No code changes needed.

---
# 5-minute demo
1) Activate venv: .\.venv\Scripts\activate
2) Start pipeline: python -m scripts.run_full_pipeline
3) Publish once:   python -m tests.publish_once
4) Health check:   python -m tests.smoke_test
5) Dashboard:      streamlit run dashboard.py
Beautiful — that’s **exactly** what we wanted to see ✅

Let’s break down what this proves, so you know *what each step validated*:

---

### 🧩 What just happened

1. `python -m tests.publish_once`
   → Published **one MQTT message** to `test.mosquitto.org`.
   → The subscriber (which runs inside `scripts.run_full_pipeline`) immediately **inserted** that into `sensor_logs`.
   → The “✅ Insert detected…” message confirms the row arrived safely.

2. `python -m tests.smoke_test`
   → Checked all three tables:

   * `sensor_logs` got the new data
   * `processed_logs` transformed it
   * `anomalies` loop ran and detected/updated anomalies
     → Everything in sync → full pipeline is healthy.

---



````markdown
## Refresh / Health Check

If smoke test shows stale data:
1. Start the full pipeline:
   ```powershell
   .\.venv\Scripts\activate
   python -m scripts.run_full_pipeline
````

2. In another terminal, publish one test message:

   ```powershell
   python -m tests.publish_once
   ```
3. Verify freshness:

   ```powershell
   python -m tests.smoke_test
   ```

✅ All three tables should show recent timestamps.


