# ===========================================================
# DEBUG PROCESSED LOGS
#
# This script loads all rows from the processed_logs table
# and prints the total number of rows along with the earliest
# and latest timestamps. Useful for quick sanity checks.
# ===========================================================

import sqlite3
from pathlib import Path
import pandas as pd

# Adjusted DB path for debug_tools location
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# Load data from processed_logs table
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query("SELECT * FROM processed_logs", conn)

# Print summary
print(f"Processed Logs: {len(df)} rows")
print("Timestamp range:", df["timestamp"].min(), "to", df["timestamp"].max())
