"""
This script connects to the database and loads humidity data
from the `processed_logs` table. It calculates and prints
the average humidity per day.

Mainly used for testing the logic behind daily humidity export,
before using it in a production pipeline.
"""
import sqlite3
import pandas as pd
from pathlib import Path

# Define correct path to DB from inside tests/ directory
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect to the database and read humidity data
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql("SELECT timestamp, humidity FROM processed_logs", conn)

# Parse timestamps and extract day
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["day"] = df["timestamp"].dt.date

# Display basic summary
print("Total rows:", len(df))
print("Unique days:", df["day"].nunique())

# Group by day and calculate average humidity
daily_avg = df.groupby("day")["humidity"].mean().reset_index()
print("\nAverage humidity per day:")
print(daily_avg)
