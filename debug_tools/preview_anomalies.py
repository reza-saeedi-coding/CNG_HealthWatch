"""
preview_anomalies.py

This script connects to the local SQLite database and retrieves the
10 most recent anomaly records from the `anomalies` table.

Intended for debugging or manual inspection. Not used in production flow.
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Define the path to the database
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect to the database and fetch the latest anomalies
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query(
        "SELECT * FROM anomalies ORDER BY id DESC LIMIT 10",
        conn
    )

# Print the results to the console
print("Last 10 anomalies:")
print(df)
