# ===========================================================
# LOG ANOMALIES MODULE
#
# This module is responsible for writing anomalies detected by
# the system to either:
#   1. A CSV file (useful for quick backups or viewing)
#   2. A database table (preferred, structured and queryable)
#
# Both functions are used after running anomaly detection.
# ===========================================================

import csv
import datetime
import sqlite3
from pathlib import Path


def log_anomalies_to_csv(anomalies_dict):
    # If there are no anomalies to log, exit quietly
    if not anomalies_dict:
        return

    # Open (or create) the anomalies.csv file in append mode
    with open("data/anomalies.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        for sensor, info in anomalies_dict.items():
            # Timestamp when the anomaly was logged
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            value = info["value"]
            z_score = info["z-score"]
            writer.writerow([timestamp, sensor, value, z_score])


def log_anomalies_to_db(anomalies_dict):
    # If there are no anomalies to log, exit quietly
    if not anomalies_dict:
        return

    # Define the path to the SQLite database
    DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

    # Connect and insert anomaly data
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for sensor, info in anomalies_dict.items():
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            value = info["value"]
            z_score = info["z-score"]
            cursor.execute("""
                INSERT INTO anomalies (timestamp, sensor, value, z_score)
                VALUES (?, ?, ?, ?)
            """, (timestamp, sensor, value, z_score))
        conn.commit()
