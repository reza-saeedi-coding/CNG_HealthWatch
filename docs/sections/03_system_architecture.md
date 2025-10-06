## 3. System Architecture

### 3.1 Purpose

This architecture documents how the CNG HealthWatch system ingests sensor data, transforms it, detects anomalies, exports summary reports, and serves a live dashboard. It is small, reproducible, and easy to industrialize (swap simulator → EWON/MQTT; SQLite → MS-SQL).

### 3.2 High-level data flow

```
[ Sensors / EWON (planned MQTT) ]    ──>  Ingest
             │
             └── (now) simulate_sensors.py  ──>  SQLite: sensor_logs
                                                │
                                                └─ transform_logs.py (10 s loop)
                                                       │
                                                       └─ SQLite: processed_logs
                                                             │
                                           detect_anomalies.py (z-score, ~60 s)
                                           log_anomalies.py ─┬─> SQLite: anomalies
                                                             └─> data/anomalies.csv
                                                             │
                               export_summary_csvs.py ───────┴─> data/exports/*.csv
                                                             │
                                                  dashboard.py (Streamlit UI)
```

### 3.3 Components & responsibilities

* **Ingest**

  * `simulate_sensors.py`: generates realistic readings every \~5 s; inserts into `sensor_logs` and appends to `data/sensor_log.csv`.
  * *(Planned)* `ingest/mqtt_subscriber.py`: subscribe to EWON/MQTT topics and insert rows into `sensor_logs`.
* **Transform**

  * `transform_logs.py`: reads new `sensor_logs`, converts timestamps (UTC), adds `pressure_status`, `flow_ok`, `hour`, and appends to `processed_logs` (loop \~10 s).
* **Analyze**

  * `detect_anomalies.py`: computes rolling z-scores on the latest window; returns an anomalies dict.
  * `log_anomalies.py`: persists anomalies to DB table `anomalies` and to `data/anomalies.csv`.
* **Export**

  * `export_summary_csvs.py`: aggregates hourly/daily/weekday summaries and compressor transitions; converts UTC → local `LOCAL_TZ`; writes to `data/exports/`.
* **Visualize**

  * `dashboard.py`: Streamlit app with live metrics, trends, and anomaly views (auto-refresh).
* **Ops / Orchestration**

  * `scripts/run_analyzer_loop.py`, `scripts/run_export_loop.py`, `scripts/run_full_pipeline.py`, `scripts/run_export_wrapper.py` (periodic jobs).
* **Config**

  * `core/config.py`: single source for `DB_PATH`, `DATA_DIR`, `LOCAL_TZ` (DST-safe exports, portable paths).

### 3.4 Data model (schemas)

**Table: `sensor_logs`** (raw ingest)

| Column             | Type    | Notes            |
| ------------------ | ------- | ---------------- |
| id                 | INTEGER | PK AUTOINCREMENT |
| timestamp          | TEXT    | ISO-8601 UTC     |
| pressure           | REAL    |                  |
| temperature        | REAL    |                  |
| flow\_rate         | REAL    |                  |
| vibration          | REAL    |                  |
| humidity           | REAL    |                  |
| compressor\_status | INTEGER | 0=OFF, 1=ON      |

**Table: `processed_logs`** (derived)

| Column             | Type    | Notes               |
| ------------------ | ------- | ------------------- |
| id                 | INTEGER | PK AUTOINCREMENT    |
| timestamp          | TEXT    | ISO-8601 UTC        |
| pressure           | REAL    |                     |
| temperature        | REAL    |                     |
| flow\_rate         | REAL    |                     |
| vibration          | REAL    |                     |
| humidity           | REAL    |                     |
| compressor\_status | INTEGER |                     |
| pressure\_status   | TEXT    | LOW / NORMAL / HIGH |
| flow\_ok           | INTEGER | 0/1                 |
| hour               | INTEGER | 0–23                |

**Table: `anomalies`**

| Column    | Type    | Notes                                  |
| --------- | ------- | -------------------------------------- |
| id        | INTEGER | PK AUTOINCREMENT                       |
| timestamp | TEXT    | ISO-8601 UTC (log time)                |
| sensor    | TEXT    | e.g., pressure, temperature            |
| value     | REAL    | observed value                         |
| z\_score  | REAL    | anomaly score (distance from baseline) |

### 3.5 Runtime & refresh cadence (defaults)

* Ingest: \~5 s (simulator) / near-real-time with MQTT (planned)
* Transform loop: \~10 s
* Analyzer loop: \~60 s
* Dashboard: auto-refresh (per tab, e.g., 10–30 s)
* Exports: on demand or periodic (loop script)

### 3.6 How to run (developer runbook)

1. Initialize DB/tables
   `python core/setup_database.py`
2. Start ingest (choose one)
   `python core/simulate_sensors.py` **or** `python debug_tools/manual_insert_test.py`
3. Start loops
   `python core/transform_logs.py`
   `python scripts/run_analyzer_loop.py`
4. Export summaries
   `python scripts/export_summary_csvs.py`
5. Open dashboard
   `streamlit run dashboard.py`

### 3.7 Industrialization path (internship targets)

* Replace simulator with EWON/MQTT subscriber.
* Optional: swap SQLite → MS-SQL via ODBC/SQLAlchemy.
* Dockerize services; add email/Teams alert hooks; integrate Grafana/Power BI.
