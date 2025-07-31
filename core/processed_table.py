"""
processed_table.py

Creates the required tables for the monitoring system:
1. processed_logs: contains enriched sensor data with pressure status, flow flags, etc.
2. anomalies: stores detected anomalies with z-score values.

Run this script once during initial setup or reset of the database.
"""

import sqlite3
from pathlib import Path

# Define the database path (adjust if structure changes)
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# --- Create processed_logs table ---
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pressure REAL,
            temperature REAL,
            flow_rate REAL,
            vibration REAL,
            humidity REAL,
            compressor_status INTEGER,
            pressure_status TEXT,
            flow_ok INTEGER,
            hour INTEGER
        )
    """)
    conn.commit()

print("Table 'processed_logs' created or already exists.")

# --- Create anomalies table ---
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            sensor TEXT,
            value REAL,
            z_score REAL
        )
    """)
    conn.commit()

print("Table 'anomalies' created or already exists.")
