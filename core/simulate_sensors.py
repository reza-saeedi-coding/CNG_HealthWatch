# ===========================================================
# SENSOR SIMULATOR SCRIPT
#
# This file simulates sensor readings (pressure, temperature,
# flow, vibration, humidity, and compressor status) and logs
# them into a SQLite database and a CSV file every 5 seconds.
# It’s designed to mimic real-world fluctuations and trigger
# alerts when thresholds are breached.
#
# The data from here feeds into the rest of the monitoring
# system (like anomaly detection and dashboards).
# ===========================================================

import datetime
import time
import random
import csv
import subprocess
import sys
import os
import sqlite3
from pathlib import Path

# ----------- Starting baseline values for our simulation -----------
pressure = 110
temperature = 58
flow_rate = 162.5
vibration = 5.3
humidity = 40
compressor_status = 1  # 1 = ON, 0 = OFF

# === Define where the database is going to be ======================
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

# === Create the sensor_logs table if it doesn't exist ==============
with sqlite3.connect(DB_PATH) as _conn:
    _cur = _conn.cursor()
    _cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pressure REAL,
            temperature REAL,
            flow_rate REAL,
            vibration REAL,
            humidity REAL,
            compressor_status INTEGER
        )
    """)
    _conn.commit()

# === This part is just to make sure the CSV is ready if we ever want to use it ===
if not os.path.exists("../data/sensor_log.csv"):
    with open("../data/sensor_log.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp", "pressure", "temperature", "flow_rate",
            "vibration", "humidity", "compressor_status"
        ])

count = 0  # We'll use this to track how many records have been logged

while True:
    # --- Sensor fluctuation simulation (to mimic real-world behavior) ---
    pressure += random.uniform(-5.0, 5.0)
    temperature += random.uniform(-0.3, 0.3)
    flow_rate += random.uniform(-10.0, 10.0)
    vibration += random.uniform(-0.2, 0.2)
    humidity += random.uniform(-0.7, 0.7)

    # Bound the values so they don't get out of hand
    pressure = round(max(0, min(pressure, 250)), 1)
    temperature = round(temperature, 1)
    flow_rate = round(max(0, flow_rate), 1)
    vibration = round(vibration, 2)
    humidity = round(max(0, min(humidity, 100)), 1)

    # --- Compressor logic: simple ON/OFF rules based on pressure ---
    if pressure < 100:
        compressor_status = 1
        print("Compressor Turned ON!")
    elif pressure > 180:
        compressor_status = 0
        print("Compressor Turned OFF!")

    # --- Simple alerts based on thresholds ---
    if pressure > 200:
        print("ALERT: Pressure too high!")
    if temperature > 55:
        print("ALERT: Overheating detected!")
    if vibration > 10:
        print("ALERT: Abnormal vibration!")
    if flow_rate < 30:
        print("ALERT: Flow too low!")
    if humidity > 70:
        print("ALERT: High humidity!")

    # --- Compose this round's reading ---
    sensor_reading = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pressure": pressure,
        "temperature": temperature,
        "flow_rate": flow_rate,
        "vibration": vibration,
        "humidity": humidity,
        "compressor_status": compressor_status
    }

    print(sensor_reading)  # Just so we can watch it in the console
    time.sleep(5)  # simulate delay between sensor readings (5 seconds)

    # === Save to SQLite database ===
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sensor_logs (
                timestamp, pressure, temperature, flow_rate,
                vibration, humidity, compressor_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            sensor_reading["timestamp"],
            sensor_reading["pressure"],
            sensor_reading["temperature"],
            sensor_reading["flow_rate"],
            sensor_reading["vibration"],
            sensor_reading["humidity"],
            sensor_reading["compressor_status"]
        ))
        conn.commit()

    # === Backup to CSV too, in case we want to use it later ===
    with open("../data/sensor_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            sensor_reading["timestamp"],
            sensor_reading["pressure"],
            sensor_reading["temperature"],
            sensor_reading["flow_rate"],
            sensor_reading["vibration"],
            sensor_reading["humidity"],
            sensor_reading["compressor_status"]
        ])

    # === Every 10 rounds, run the analyzer ===
    count += 1
    if count % 10 == 0:
        print("Running Analysis....")
        subprocess.run([sys.executable, "../core/analyze_data.py"])
