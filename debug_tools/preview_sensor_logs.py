"""
preview_sensor_logs.py

This debug script connects to the local SQLite database and retrieves
the 5 most recent entries from the `sensor_logs` table.

Useful for verifying that raw sensor data is being collected and logged correctly.
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Define the path to the SQLite database
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect to the DB and fetch the latest raw sensor logs
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM sensor_logs ORDER BY id DESC LIMIT 5", conn)
conn.close()

# Print results for quick inspection
print("Last 5 entries from sensor_logs:")
print(df)
