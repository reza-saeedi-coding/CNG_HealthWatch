# ===========================================================
# DEBUG PROCESSED LOGS
#
# This script loads all rows from the processed_logs table
# and prints the total number of rows along with the earliest
# and latest timestamps. Useful for quick sanity checks.
# ===========================================================

import sqlite3
import pandas as pd
from core.config import DB_PATH


# Load data from processed_logs table
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query("SELECT * FROM processed_logs", conn)

# Print summary
print(f"Processed Logs: {len(df)} rows")
print("Timestamp range:", df["timestamp"].min(), "to", df["timestamp"].max())
