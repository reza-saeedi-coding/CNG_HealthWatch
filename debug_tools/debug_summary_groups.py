# ===========================================================
# DEBUG SUMMARY GROUPS
#
# This script helps verify the number of log entries grouped
# by hour of the day and by date. Useful for debugging time-based
# aggregations and checking data completeness.
# ===========================================================

import sqlite3
import pandas as pd
from pathlib import Path

# Adjust path relative to debug_tools directory
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Load timestamps from processed logs table
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query("SELECT timestamp FROM processed_logs", conn)

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Group and display record counts per hour (0–23)
print("\nRecords per HOUR:")
print(df["timestamp"].dt.hour.value_counts().sort_index())

# Group and display record counts per date
print("\nRecords per DAY:")
print(df["timestamp"].dt.date.value_counts().sort_index())
