"""
setup_database.py

Initializes the main SQLite database (sensor_data.db) and creates core tables:
1. sensor_logs   → raw incoming sensor data
2. anomalies     → z-score-based detected anomalies

This script should be run once before launching the system.
"""

import sqlite3
from pathlib import Path

# Define the path to the database
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"
DB_PATH.parent.mkdir(exist_ok=True)  # Ensure the /data directory exists

# Connect to the database (creates it if not found)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# --- Table: sensor_logs ---
cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        pressure REAL,
        temperature REAL,
        flow_rate REAL,
        vibration REAL,
        humidity REAL,
        compressor_status INTEGER
    )
""")

# --- Table: anomalies ---
cur.execute("""
    CREATE TABLE IF NOT EXISTS anomalies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        sensor TEXT,
        value REAL,
        z_score REAL
    )
""")

conn.commit()
conn.close()

print(f"Database created and tables are ready at: {DB_PATH}")
