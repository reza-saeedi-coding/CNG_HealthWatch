"""
This script tests the logic for exporting hourly average temperature
from the `processed_logs` table. Mimics what the real export scripts do.

Useful for debugging temperature summary logic.
"""
import sqlite3
import pandas as pd
from pathlib import Path

# Resolve the path to the database from the tests/ directory
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect to database and load temperature data
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql("SELECT timestamp, temperature FROM processed_logs", conn)

# Parse timestamps and round to the hour
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:00:00")

# Simulate export logic: average temperature per hour
summary = df.groupby("hour")["temperature"].mean().reset_index()

print("Rows in summary:", len(summary))
print(summary.head())
