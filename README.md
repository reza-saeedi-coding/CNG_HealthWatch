````md
# SAFE IoT Monitoring System

A robust end-to-end IoT data monitoring pipeline built with Python and Streamlit. This system simulates sensor data, processes and stores it in a SQLite database, detects anomalies, and visualizes insights in real-time using a web dashboard.

![GitHub last commit](https://img.shields.io/github/last-commit/reza-saeedi-coding/SAFE_IoT_Monitoring)

---

## Features

- Simulated IoT Data: Emulates multiple sensors (temperature, pressure, humidity, etc.).
- SQLite Database: Efficient local storage of structured sensor data.
- Data Pipeline: Modular ETL-style scripts for ingesting, transforming, and logging data.
- Anomaly Detection: Z-score based statistical detection on real-time values.
- Live Dashboard: Streamlit app displaying metrics, charts, and anomalies.
- Export System: Automatic CSV generation of summarized and anomaly data for analysis.

---

## Project Structure

```plaintext
SAFE_IoT_Monitoring/
│
├── core/                   # Core processing and data logic
│   ├── analyze_data.py
│   ├── detect_anomalies.py
│   ├── log_anomalies.py
│   ├── migrate_csv_to_sqlite.py
│   ├── processed_table.py
│   ├── setup_database.py
│   ├── simulate_sensors.py
│   └── transform_logs.py
│
├── scripts/                # Loops and wrappers for automation
│   ├── export_summary_csvs.py
│   ├── run_analyzer_loop.py
│   ├── run_export_loop.py
│   ├── run_export_wrapper.py
│   └── run_full_pipeline.py
│
├── debug_tools/            # Debug scripts for sanity checks
│   ├── debug_processed_log.py
│   ├── debug_summary_groups.py
│   ├── preview_anomalies.py
│   ├── preview_processed_logs.py
│   ├── preview_sensor_logs.py
│   ├── preview_tables.py
│   ├── check_hour_distribution.py
│   └── manual_insert_test.py
│
├── tests/                  # Test and validation scripts
│   ├── check_csv_export.py
│   ├── check_processed_log.py
│   ├── check_processed_log_timestamps.py
│   ├── check_temperature_distribution.py
│   ├── test_anomaly_pipeline.py
│   ├── test_dbs.py
│   ├── test_humidity_export.py
│   └── test_temp_export.py
│
├── data/                   # Local databases and raw data
│   ├── anomalies.csv
│   ├── iot_data.db
│   ├── sensor_data.db
│   └── sensor_log.csv
│
├── exports/                # Auto-generated CSV summaries
│   └── *.csv
│
├── charts/                 # Legacy PNG charts
│
├── dashboard.py            # Streamlit dashboard app
├── requirements.txt        # Python dependencies
└── README.md               # This file
````

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/reza-saeedi-coding/SAFE_IoT_Monitoring.git
cd SAFE_IoT_Monitoring
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # On Linux/macOS
.venv\Scripts\activate         # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the database

```bash
python core/setup_database.py
```

### 5. Run the full pipeline

```bash
python scripts/run_full_pipeline.py
```

### 6. Start the dashboard

```bash
streamlit run dashboard.py
```

---

## Dashboard Preview

<!-- Add a screenshot if you want -->

<!-- Example: ![Dashboard Preview](https://github.com/reza-saeedi-coding/SAFE_IoT_Monitoring/blob/main/images/dashboard_preview.png) -->

---

## Use Cases

* Industrial sensor monitoring (compressors, HVAC, etc.)
* Prototyping real-time data pipelines
* Teaching IoT + Data Engineering concepts
* Offline diagnostics and anomaly visualization

---

## Highlights

* Works fully offline with local DB (SQLite)
* Minimal dependencies, fast setup
* Modular scripts for easy customization
* Export-ready CSVs for further reporting or Power BI

---

## TODO (Planned Features)

* REST API endpoint for data access
* Live Kafka integration
* Real-time alert system
* Docker containerization

---

## Author

**Reza Saeedi Sorkheh Rizi**
Email: [reza.saeedisorkheh@studio.unibo.it](mailto:reza.saeedisorkheh@studio.unibo.it)
GitHub: [@reza-saeedi-coding](https://github.com/reza-saeedi-coding)

---

