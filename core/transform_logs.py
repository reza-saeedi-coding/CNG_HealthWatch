# ===========================================================
# DATA TRANSFORMATION SCRIPT
#
# This script continuously checks for new rows in `sensor_logs`,
# enriches them (pressure_status, flow_ok, hour), and appends
# the result to `processed_logs`.
# ===========================================================

import time
import pandas as pd
from core.db import get_connection


def transform_and_insert():
    # 1) Find the last processed id
    with get_connection() as conn:
        existing = pd.read_sql_query(
            "SELECT MAX(id) AS max_id FROM processed_logs",
            conn
        )

        if existing.empty or existing["max_id"].isna().all():
            last_id = 0
        else:
            last_id = int(existing["max_id"].iloc[0] or 0)

        # 2) Pull only new sensor rows
        query = f"""
            SELECT *
            FROM sensor_logs
            WHERE id > {last_id}
            ORDER BY id ASC
            LIMIT 50000
        """
        df = pd.read_sql_query(query, conn)

    if df.empty:
        return  # Nothing new

    # 3) Clean & enrich
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df["hour"] = df["timestamp"].dt.hour

    def classify_pressure(p):
        p = float(p)
        if p < 100:
            return "LOW"
        elif p > 180:
            return "HIGH"
        else:
            return "NORMAL"

    df["pressure_status"] = df["pressure"].apply(classify_pressure)
    df["flow_ok"] = (df["flow_rate"].astype(float) >= 50).astype(int)

    # 4) Append to processed_logs
    with get_connection() as conn:
        df.to_sql("processed_logs", conn, if_exists="append", index=False)

    print(f"{len(df)} new rows added to processed_logs.")


if __name__ == "__main__":
    # === Keep running this in a loop, every 10 seconds ===
    while True:
        try:
            transform_and_insert()
        except Exception as e:
            print("Error:", e)
        time.sleep(10)
