# ===========================================================
# EXPORT SUMMARY CSVs
#
# This script reads the processed sensor logs from the database
# and creates multiple CSV summary reports based on:
# - Average values by hour, minute, weekday, day
# - Compressor status transitions
# - Anomalies (if available)
#
# Exported CSVs are saved in the `exports/` directory.
# ===========================================================

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import timedelta

# Paths
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"
EXPORT_DIR = Path(__file__).resolve().parents[1] / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def export_summary_csvs():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM processed_logs", conn)

    # Convert timestamp to datetime and shift to local time (UTC+2)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["timestamp"] = df["timestamp"] + timedelta(hours=2)

    # Create time-based columns
    df["hour"] = df["timestamp"].dt.hour
    df["hour_block"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:00:00")
    df["minute_block"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    df["day"] = df["timestamp"].dt.date
    df["weekday"] = df["timestamp"].dt.day_name()
    df["weekday_num"] = df["timestamp"].dt.weekday

    # Summary aggregations
    summaries = {
        "avg_temperature_by_hour.csv":
            df.groupby("hour_block")["temperature"].mean().reset_index(),

        "avg_pressure_by_hour.csv":
            df.groupby("hour_block")["pressure"].mean().reset_index(),

        "avg_pressure_by_minute.csv":
            df.groupby("minute_block")["pressure"].mean().reset_index(),

        "avg_flow_rate_by_hour.csv":
            df.groupby("hour_block")["flow_rate"].mean().reset_index(),

        "avg_humidity_by_day.csv":
            df.groupby("day")["humidity"].mean().reset_index(),

        "compressor_status_by_day.csv":
            df.groupby("day")["compressor_status"].mean().reset_index(),

        "avg_vibration_by_weekday.csv":
            df.groupby(["weekday", "weekday_num"])["vibration"].mean().reset_index().sort_values("weekday_num"),

        "max_temperature_by_day.csv":
            df.groupby("day")["temperature"].max().reset_index(),
    }

    # Calculate compressor ON/OFF transitions
    df = df.sort_values("timestamp")
    df["prev_status"] = df["compressor_status"].shift(1)
    df["status_change"] = df["compressor_status"] != df["prev_status"]
    df_trans = df[df["status_change"] == True].copy()
    df_trans["Status Change"] = df_trans["compressor_status"].map({1: "Turned ON", 0: "Turned OFF"})
    df_trans["day"] = df_trans["timestamp"].dt.date
    transition_counts = df_trans.groupby(["day", "Status Change"]).size().reset_index(name="count")

    # Save compressor transitions
    transition_counts.to_csv(EXPORT_DIR / "compressor_transitions_by_day.csv", index=False)

    # Export main summaries
    for filename, summary_df in summaries.items():
        summary_df.to_csv(EXPORT_DIR / filename, index=False)

    # Export anomalies table if it exists
    try:
        with sqlite3.connect(DB_PATH) as conn:
            anomalies_df = pd.read_sql_query(
                "SELECT id, timestamp, sensor, value, z_score FROM anomalies ORDER BY id", conn
            )
        anomalies_df["timestamp"] = pd.to_datetime(anomalies_df["timestamp"], utc=True)
        anomalies_df["timestamp"] = anomalies_df["timestamp"] + timedelta(hours=2)
        anomalies_df.to_csv(EXPORT_DIR / "anomalies.csv", index=False)
        print("Exported anomalies.csv with local time.")
    except Exception as e:
        print("Skipped anomalies export —", e)

    print(f"Exported {len(summaries)} summary CSV files to: {EXPORT_DIR}")

if __name__ == "__main__":
    export_summary_csvs()
