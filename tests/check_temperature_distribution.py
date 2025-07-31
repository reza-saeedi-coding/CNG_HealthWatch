"""
check_temperature_distribution.py

This script performs a quick exploratory check on the temperature values from the
'processed_logs' table in the SQLite database. It:
1. Loads timestamp and temperature data.
2. Groups the temperature data by hour.
3. Prints basic statistics like total count, unique values, and hourly distribution.

Used for sanity-checking data quality and distribution during development/debugging.
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Define DB path (relative to project root)
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect and fetch timestamp + temperature columns
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql("SELECT timestamp, temperature FROM processed_logs", conn)

# Convert timestamp to datetime object
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Group into hourly intervals
df["hour"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:00:00")

# Display basic stats
print("Total rows with temperature:", df["temperature"].count())
print("Unique temperature values:", df["temperature"].nunique())
print("Unique hourly groups:", df["hour"].nunique())

# Display average temperature for a few hours
print("\nAverage temperature by hour (first few rows):")
print(df.groupby("hour")["temperature"].mean().head())
