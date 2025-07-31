"""
preview_processed_logs.py

This debug script connects to the local SQLite database and retrieves
the 5 most recent entries from the `processed_logs` table.

Useful for inspecting data after transformation and before visualization.
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Define the path to the SQLite database
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Connect and fetch recent processed log entries
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query("SELECT * FROM processed_logs ORDER BY id DESC LIMIT 5", conn)

# Print to terminal for quick check
print(df)
