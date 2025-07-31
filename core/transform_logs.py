# ===========================================================
# DATA TRANSFORMATION SCRIPT
#
# This script continuously monitors the SQLite database to check
# for any new sensor records logged in the "sensor_logs" table.
# Whenever new data appears, it processes and enhances it with
# additional fields (like pressure status, flow status, hour block),
# then stores the processed version into the "processed_logs" table.
## This script is meant to run in the background and keep processed
# data up-to-date for dashboards or anomaly detection.
# ===========================================================

import sqlite3
from pathlib import Path
import pandas as pd
import time

# --- Locate the database file relative to the project root ---
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# --- Function to transform and insert new records ---
def transform_and_insert():
    with sqlite3.connect(DB_PATH) as conn:
        # Figure out the last ID we already processed
        existing = pd.read_sql_query("SELECT MAX(id) as max_id FROM processed_logs", conn)
        last_id = existing["max_id"].values[0] if existing["max_id"].notna().any() else 0

        # Grab only new records from sensor_logs
        query = f"SELECT * FROM sensor_logs WHERE id > {last_id} ORDER BY id ASC LIMIT 50000"
        df = pd.read_sql_query(query, conn)

    if df.empty:
        return  # Nothing new to do

    # Convert timestamp to datetime (force UTC and drop bad rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # Extract hour for analysis (can be used later in grouping)
    df["hour"] = df["timestamp"].dt.hour

    # Add human-readable pressure status based on simple thresholds
    def classify_pressure(p):
        if p < 100:
            return "LOW"
        elif p > 180:
            return "HIGH"
        else:
            return "NORMAL"

    df["pressure_status"] = df["pressure"].apply(classify_pressure)

    # Add a binary flag for flow rate check (0 = not OK, 1 = OK)
    df["flow_ok"] = (df["flow_rate"] >= 50).astype(int)

    # Store the cleaned and enhanced data into processed_logs
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("processed_logs", conn, if_exists="append", index=False)

    print(f"{len(df)} new rows added to processed_logs.")

# === Keep running this in a loop, every 10 seconds ===
while True:
    try:
        transform_and_insert()
    except Exception as e:
        print("Error:", e)
    time.sleep(10)
