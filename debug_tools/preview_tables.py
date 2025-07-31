"""
create_processed_logs_table.py

Creates the 'processed_logs' table in the sensor_data.db SQLite database
if it doesn't already exist.

This is useful during debugging or the initial setup of the database.
"""

import sqlite3
from pathlib import Path

# Define the database path
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create the processed_logs table with extra derived fields
cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_logs(
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

# Save changes and close the connection
conn.commit()
print("Table 'processed_logs' created successfully.")
conn.close()
