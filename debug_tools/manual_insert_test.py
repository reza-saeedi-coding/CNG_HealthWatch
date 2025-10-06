"""
manual_insert_test.py

This script manually inserts synthetic sensor logs into the database for testing purposes.
It generates 7 full days of fake readings, one every 15 minutes, and populates the 'sensor_logs' table.

Note:
- All previous records in 'sensor_logs' will be deleted.
- This script is meant to be used in development or debugging environments.
- Place this inside the 'debug_tools' directory.
"""

import sqlite3
import random
from datetime import datetime, timedelta, timezone
from core.config import DB_PATH


def generate_random_log(fake_time):
    """
    Create a synthetic sensor reading for the given time.

    Some time-based variation is added:
    - Pressure is higher during working hours (9 to 17)
    - Temperature is slightly warmer during daytime (6 to 18)
    """
    hour = fake_time.hour
    base_temp = 40 if 6 <= hour <= 18 else 30
    base_pressure = 120 if 9 <= hour <= 17 else 90

    return {
        # Ensure UTC ISO-8601 with timezone, e.g. 2025-09-13T12:00:00+00:00
        "timestamp": fake_time.replace(tzinfo=timezone.utc).isoformat(),
        "pressure": round(random.uniform(base_pressure, base_pressure + 50), 1),
        "temperature": round(random.uniform(base_temp, base_temp + 15), 1),
        "flow_rate": round(random.uniform(40, 140), 1),
        "vibration": round(random.uniform(3, 12), 2),
        "humidity": round(random.uniform(30, 70), 1),
        "compressor_status": random.choice([0, 1]),
    }


# Store all generated logs in a list
logs_to_insert = []

# Start 7 days ago from now (UTC, naive -> we attach UTC tzinfo in generate_random_log)
start_time = datetime.now(timezone.utc) - timedelta(days=7)

# Generate a reading every 15 minutes for 7 days = 672 logs
for i in range(7 * 24 * 4):
    log_time = start_time + timedelta(minutes=i * 15)
    logs_to_insert.append(generate_random_log(log_time))

# Insert logs into the database after clearing previous ones
with sqlite3.connect(str(DB_PATH)) as conn:
    cur = conn.cursor()

    # Clear previous records from sensor_logs
    cur.execute("DELETE FROM sensor_logs")

    # Insert each synthetic log
    for log in logs_to_insert:
        cur.execute("""
            INSERT INTO sensor_logs 
            (timestamp, pressure, temperature, flow_rate, vibration, humidity, compressor_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            log["timestamp"],
            log["pressure"],
            log["temperature"],
            log["flow_rate"],
            log["vibration"],
            log["humidity"],
            log["compressor_status"],
        ))

    conn.commit()

print(f"Inserted {len(logs_to_insert)} synthetic logs over 7 full days.")
