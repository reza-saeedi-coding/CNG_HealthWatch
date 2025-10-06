# tests/publish_once.py
import os
import time
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.publish as pub
from core.config import DB_PATH  # uses your .env via python-dotenv (loaded in config)

# --- Config (env overrides allowed) ---
TOPIC = os.getenv("MQTT_TOPIC", "cng/dell-demo/telemetry")
HOST = os.getenv("MQTT_HOST", "test.mosquitto.org")
PORT = int(os.getenv("MQTT_PORT", "1883"))

# one message payload (can tweak values if you want to test anomalies)
MSG = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "pressure": 101.5,
    "temperature": 47.8,
    "flow_rate": 130.2,
    "vibration": 6.2,
    "humidity": 38.0,
    "compressor_status": 1,
}

# polling behavior after publish
MAX_RETRIES = 12          # total wait ~ 12 * 0.5s = 6s
SLEEP_SECONDS = 0.5


def _sensor_logs_state(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), MAX(timestamp) FROM sensor_logs")
    count, latest = cur.fetchone()
    return int(count or 0), str(latest or "")


def main():
    db_path = Path(DB_PATH)
    if not db_path.exists():
        print(f"❌ DB not found: {db_path}")
        print("   Make sure you've run the pipeline/subscriber at least once so the DB is created.")
        return

    # snapshot BEFORE publish
    with sqlite3.connect(str(db_path)) as con:
        before_count, before_latest = _sensor_logs_state(con)

    # publish once
    pub.single(TOPIC, json.dumps(MSG), hostname=HOST, port=PORT)
    print(f"published test message to {HOST}:{PORT} topic={TOPIC}")

    # poll for the insert to appear
    inserted = False
    new_count = before_count
    new_latest = before_latest

    for _ in range(MAX_RETRIES):
        time.sleep(SLEEP_SECONDS)
        with sqlite3.connect(str(db_path)) as con:
            new_count, new_latest = _sensor_logs_state(con)

        if new_count > before_count or (new_latest and new_latest != before_latest):
            inserted = True
            break

    if inserted:
        print(f"✅ Insert detected in sensor_logs → {before_count} -> {new_count} (latest: {new_latest})")
    else:
        print("⚠️ No insert detected after publish.")
        print("   Tips:")
        print("   - Ensure the subscriber/pipeline is RUNNING and subscribed to the SAME topic.")
        print(f"   - Subscriber should show: 'connected rc=0 -> subscribe {TOPIC}'")
        print("   - Network may block port 1883, or broker may be unreachable.")
        print("   - Try increasing MAX_RETRIES or SLEEP_SECONDS if your machine is slow.")


if __name__ == "__main__":
    main()
