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
from core.config import DATA_DIR, DB_PATH
from core.db import get_connection
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def log_anomalies_to_csv(anomalies_dict):
    # If there are no anomalies to log, exit quietly
    if not anomalies_dict:
        return

    # Write to a project-rooted path, so it works from any CWD
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIR / "anomalies.csv"

    # Open (or create) the anomalies.csv file in append mode
    with open(csv_path, mode="a", newline="") as file:
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

    # Connect and insert anomaly data (DB_PATH from core.config)
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
