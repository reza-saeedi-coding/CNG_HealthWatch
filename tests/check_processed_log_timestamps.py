"""
check_processed_log_timestamps.py

This test script connects to the SQLite database and retrieves all timestamps
from the `processed_logs` table. It then groups and displays how many log entries
exist for each individual date. Useful for verifying data consistency and frequency
over time.

Intended for testing and inspection purposes only. Keep it in the `tests/` directory.
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Use correct path to the database (relative to this file)
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect to the database and retrieve timestamps
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query("SELECT timestamp FROM processed_logs", conn)

# Convert string timestamps to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Count and display number of logs per day
print("Log counts by day:")
print(df["timestamp"].dt.date.value_counts().sort_index())
