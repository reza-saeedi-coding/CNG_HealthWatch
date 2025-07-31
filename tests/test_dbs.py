"""
test_dbs.py

This script loads the full `processed_logs` table from the local SQLite database,
sorted by timestamp in ascending order. It prints the first 50,000 rows (if available)
along with the full timestamp range to inspect data continuity and completeness.

Usage:
- Place inside the `tests/` folder of the project.
- Run this manually to visually inspect the database contents.
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Adjust path to reach the data folder from tests/
db_path = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect and read the full processed_logs table
with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query("SELECT * FROM processed_logs ORDER BY timestamp ASC", conn)

# Show some of the data and the timestamp range
print(df.head(50000))
print(df["timestamp"].min(), "to", df["timestamp"].max())
