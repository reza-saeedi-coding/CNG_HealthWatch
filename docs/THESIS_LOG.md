## 2025-09-11 — System Architecture documented
- Wrote Section 3 in `docs/THESIS_OUTLINE.md` (data flow, components, schemas, runbook).
- Purpose: make the pipeline explainable for thesis + internship handover.
- Proof: the new section includes tables for `sensor_logs`, `processed_logs`, `anomalies` and a run sequence.

## 2025-09-11 — Dashboard uses central config
- `dashboard.py`: import DB_PATH, LOCAL_TZ from `core/config.py`; replaced hardcoded "Europe/Rome".
- Reason: single source of truth for paths/timezone, DST-safe UI.
- Proof: `streamlit run dashboard.py` loads; “Last Update (Local)” correct; charts render.

## 2025-09-13 — Pipeline hardening + package setup
- Made packages explicit: added empty `__init__.py` to `core/`, `scripts/`, `debug_tools/`, `tests/`.
- Standardized how scripts run: switched to `python -m ...` (fixes `ModuleNotFoundError: core`).
- Simulator CSV path fixed to use central `DATA_DIR`; DB path centralized via `DB_PATH`.
- Export loop now calls exporter as a module with `sys.executable -m scripts.export_summary_csvs` (OS-portable).
- `export_summary_csvs.py` uses `LOCAL_TZ` (DST-safe); anomalies also exported in local time.
- Dashboard now uses central `DB_PATH` and `LOCAL_TZ`.
- `manual_insert_test.py` timestamps set to UTC; replaced deprecated `utcnow()` with `datetime.now(timezone.utc)`.
- Verified end-to-end:
  - `python -m core.simulate_sensors` → CSV/DB updating
  - `python -m core.transform_logs` → rows flowing into `processed_logs`
  - `python -m tests.test_anomaly_pipeline` → anomalies detected & logged
  - `python -m scripts.export_summary_csvs` → 8 summary CSVs + anomalies.csv in `data/exports/`
## 2025-09-15 — Full pipeline supervisor verified
- Ran `python -m scripts.run_full_pipeline` (one-command bring-up).
- Supervisor launched 4 processes: simulator, transformer, analyzer loop, export loop.
- Observed initial backlog processed (“2467 new rows added to processed_logs”).
- Analyzer executed (z-scores printed) and logged anomalies; exports wrote 8 CSVs + anomalies.csv.
- Clean stop with Ctrl+C; child processes terminated by supervisor.
Verified MQTT path: subscribed to cng/dell-demo/telemetry on test.mosquitto.org; published test JSON; row inserted into sensor_logs and processed into processed_logs.

## 2025-09-23 — MQTT ingest verified (public broker)
- Started subscriber: `python -m ingest.mqtt_subscriber` with MQTT_HOST=test.mosquitto.org, topic `cng/dell-demo/telemetry`.
- Published sample JSON via PowerShell one-liner using paho.mqtt.publish.
- Subscriber printed `Row Inserted`; verified new row in `sensor_logs`.
- Ran transformer; saw “1 new rows added to processed_logs.” Verified in preview.
- Outcome: end-to-end MQTT → DB → processed pipeline confirmed.

## 2025-09-21 to 2025-09-22 — No study
- Note: two days paused due to other work. Resumed on 2025-09-23.

## 2025-09-25 — Added rotating file logging to MQTT subscriber.
- Log file: data/logs/mqtt_subscriber.log (1 MB rotation, 3 backups) + console handler.
- Replaced prints with log.info/warning/exception in connect, subscribe, insert, and error paths.
- Verified by publishing valid and malformed MQTT messages; observed “row inserted” and “skip message: missing keys …” in logs.

## 2025-10-01 TODO — DB Adapter rollout (5–10 mins per file)
- core/db.py added (adapter; SQLite now, MS-SQL later)
- config: DB_URL default to sqlite:///… added
- ingest/mqtt_subscriber now uses get_connection()
Next pass (when time allows):
- swap get_connection() into: core/transform_logs.py, scripts/export_summary_csvs.py,
  tests/* that touch DB, analyzer/loggers.
SAFE cutover:
- install pyodbc + ODBC Driver 17
- set DB_URL in .env to mssql+pyodbc://USER:PASS@SERVER:1433/DBNAME?driver=ODBC+Driver+17+for+SQL+Server
