"""
This script loads timestamps from the `processed_logs` table and prints summary
information such as date range, number of unique days, weekdays, and hours.

It is useful for validating time coverage and data completeness.
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Use relative path from tests/ to access the database
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Load timestamps from DB
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql("SELECT timestamp FROM processed_logs", conn)

# Convert to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Summary stats
print("Total rows:", len(df))
print("Time range:")
print("  Start:", df["timestamp"].min())
print("  End:  ", df["timestamp"].max())
print("Unique days:", df["timestamp"].dt.date.nunique())
print("Unique weekdays:", df["timestamp"].dt.day_name().nunique())
print("Unique hours:", df["timestamp"].dt.hour.nunique())
