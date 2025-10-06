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
from core.db import get_connection
from core.config import DATA_DIR, LOCAL_TZ


EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def export_summary_csvs():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM processed_logs", conn)

    # Convert to tz-aware UTC, then to local timezone (DST-safe)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert(LOCAL_TZ)

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

    # --- Fixed: Calculate compressor ON/OFF transitions (no overcount) ---
    # Sort, keep only unique (timestamp, status) pairs to avoid duplicates,
    # then count only TRUE status changes between consecutive rows.
    df_trans_base = (
        df.sort_values("timestamp")
          .loc[:, ["timestamp", "compressor_status"]]
          .drop_duplicates()
          .copy()
    )
    # Ensure int (sometimes read as float)
    df_trans_base["compressor_status"] = df_trans_base["compressor_status"].astype(int)

    df_trans_base["prev_status"] = df_trans_base["compressor_status"].shift(1)
    transitions = df_trans_base[df_trans_base["compressor_status"] != df_trans_base["prev_status"]].copy()

    transitions["Status Change"] = transitions["compressor_status"].map({1: "Turned ON", 0: "Turned OFF"})
    transitions["day"] = transitions["timestamp"].dt.date

    transition_counts = (
        transitions.groupby(["day", "Status Change"])
        .size()
        .reset_index(name="count")
    )
    # ---------------------------------------------------------------

    # Save compressor transitions
    transition_counts.to_csv(EXPORT_DIR / "compressor_transitions_by_day.csv", index=False)

    # Export main summaries
    for filename, summary_df in summaries.items():
        summary_df.to_csv(EXPORT_DIR / filename, index=False)

    # Export anomalies table if it exists
    try:
        with get_connection() as conn:
            anomalies_df = pd.read_sql_query(
                "SELECT id, timestamp, sensor, value, z_score FROM anomalies ORDER BY id", conn
            )
        anomalies_df["timestamp"] = pd.to_datetime(anomalies_df["timestamp"], utc=True)
        anomalies_df["timestamp"] = anomalies_df["timestamp"].dt.tz_convert(LOCAL_TZ)
        anomalies_df.to_csv(EXPORT_DIR / "anomalies.csv", index=False)
        print("Exported anomalies.csv with local time.")
    except Exception as e:
        print("Skipped anomalies export —", e)

    print(f"Exported {len(summaries)} summary CSV files to: {EXPORT_DIR}")


if __name__ == "__main__":
    export_summary_csvs()
