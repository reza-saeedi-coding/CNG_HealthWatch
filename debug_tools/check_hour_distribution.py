# ===========================================================
# FLOW RATE DISTRIBUTION BY HOUR
#
# This quick script loads flow rate data from the processed_logs table,
# converts timestamps, extracts the hour of each reading, and prints
# the number of records per hour. Useful for checking uneven sampling,
# gaps, or load distribution across the day.
# ===========================================================

import sqlite3
import pandas as pd
from pathlib import Path

# Define path to the SQLite database
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect to the database and load timestamp + flow_rate
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query("SELECT timestamp, flow_rate FROM processed_logs", conn)

# Convert timestamp column to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Extract hour for each record
df["hour"] = df["timestamp"].dt.hour

# Group by hour and count entries
hourly_counts = df.groupby("hour").size()

# Print results
print("\nRecords per hour:\n")
print(hourly_counts)
