# ==========================================================
# MQTT INGEST SUBSCRIBER
#
# Purpose
# -------
# Subscribe to an MQTT topic, parse incoming JSON telemetry, and
# write each message into the SQLite table `sensor_logs`.
#
# Responsibilities
# ----------------
# - Ensure the `sensor_logs` table exists (idempotent bootstrap).
# - Convert MQTT raw bytes → UTF-8 text → JSON → Python dict.
# - Validate required keys; coerce types; insert a single row.
# - Run a minimal MQTT client loop with connect/message callbacks.
#
# How to run (from project root)
# ------------------------------
#   python -m ingest.mqtt_subscriber
#
# Environment variables (optional)
# --------------------------------
#   MQTT_HOST        default: "localhost"
#   MQTT_PORT        default: "1883"
#   MQTT_USERNAME    default: unset (anonymous)
#   MQTT_PASSWORD    default: unset (anonymous)
#   MQTT_TOPIC       default: "cng/telemetry"
#
# Expected payload (JSON)
# -----------------------
# {
#   "pressure": 120.0,
#   "temperature": 50.0,
#   "flow_rate": 100.0,
#   "vibration": 5.5,
#   "humidity": 40.0,
#   "compressor_status": 1,
#   "timestamp": "2025-09-15T10:33:40+00:00"   # optional; auto-UTC if missing
# }
#
# Notes
# -----
# - Uses DB_PATH from core.config for a single source of truth.
# - Keeps prints simple; replace with `logging` later if needed.
# - QoS=1 (at-least-once). If duplicates matter, add dedup logic later.
# ==========================================================

"""Subscriber that will read MQTT and write to sensor_logs."""

from __future__ import annotations

import os
import json
from core.db import get_connection
from datetime import datetime, timezone
import warnings
import paho.mqtt.client as mqtt
from core.config import DB_PATH
# --- logging setup (file + console, rotating) ---
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[1] / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR /"mqtt_subscriber.log"
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
console_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[file_handler, console_handler],
)

log = logging.getLogger("mqtt")
# --- end logging setup ---

warnings.filterwarnings("ignore", category=DeprecationWarning, message="Callback API version 1 is deprecated.*")

# ----------------------------------------------------------
# DB bootstrap: ensure the target table exists (idempotent)
# ----------------------------------------------------------
def ensure_tables() -> None:
    """
    Create the `sensor_logs` table if it does not exist.
    Safe to call on every startup (idempotent).
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
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
            """
        )
        # Optional: uncomment to speed up time-window queries later
        # c.execute("CREATE INDEX IF NOT EXISTS ix_sensor_logs_ts ON sensor_logs(timestamp)")
        conn.commit()
    log.info("sensor_logs table ready at: %s", DB_PATH)


# ----------------------------------------------------------
# Single-row insert helper used by the MQTT callback
# ----------------------------------------------------------
def insert_row(d: dict) -> None:
    """
    Insert one telemetry dict into `sensor_logs`.
    - Fills `timestamp` with current UTC ISO-8601 if missing.
    - Casts values to proper numeric types (float/int).
    Raises:
      KeyError / ValueError on bad/missing inputs.
      sqlite3.Error on DB failures.
    """
    ts = d.get("timestamp") or datetime.now(timezone.utc).isoformat()

    row = (
        ts,
        float(d["pressure"]),
        float(d["temperature"]),
        float(d["flow_rate"]),
        float(d["vibration"]),
        float(d["humidity"]),
        int(d["compressor_status"]),
    )

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sensor_logs
            (timestamp, pressure, temperature, flow_rate, vibration, humidity, compressor_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            row,
        )
        conn.commit()


# ----------------------------------------------------------
# MQTT callbacks
# ----------------------------------------------------------
def on_connect(client: mqtt.Client, userdata, flags, rc: int) -> None:
    """
    Called after connecting to the broker.
    Subscribes to the configured topic so messages start flowing.
    rc == 0 means success; non-zero indicates an error.
    """
    topic = os.getenv("MQTT_TOPIC", "cng/telemetry")
    log.info("connected rc=%s -> subscribe %s", rc, topic)
    client.subscribe(topic, qos=1)


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    """
    Called for each incoming message. Decodes bytes → JSON → dict,
    validates required keys, and writes a row to `sensor_logs`.
    Never raises to the network loop; prints errors and continues.
    """
    try:
        # Decode bytes and parse JSON
        d = json.loads(msg.payload.decode("utf-8"))

        # Validate the minimal contract required by insert_row()
        required = {
            "pressure",
            "temperature",
            "flow_rate",
            "vibration",
            "humidity",
            "compressor_status",
        }
        missing = required - d.keys()
        if missing:
            log.warning("skip message: missing keys: %s", missing)
            return

        insert_row(d)
        log.info("row inserted")
    except Exception as e:
        # Keep the subscriber alive even on bad payloads or DB errors
        log.exception("message error")

def on_disconnect(client: mqtt.Client, userdata, rc: int) -> None:
    """
    Called when the client disconnects from the broker.
    rc==0 means a clean disconnect; non-zero means unexpected.
    """
    log.warning("disconnected (rc=%s) will auto re-try", rc)

# ----------------------------------------------------------
# Entry point: configure client, connect, and start loop
# ----------------------------------------------------------
def main() -> None:
    """
    Read connection settings from the environment, ensure the table,
    connect to the broker, and start the forever loop.
    Ctrl+C to stop.
    """
    ensure_tables()

    host = os.getenv("MQTT_HOST", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    user = os.getenv("MQTT_USERNAME")
    pw = os.getenv("MQTT_PASSWORD")

    # For paho-mqtt >= 2.x: specify callback API version for v3.1.1-style callbacks
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)

    if user and pw:
        client.username_pw_set(user, pw)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.reconnect_delay_set(min_delay=1, max_delay=30)

    log.info("connecting to %s:%s ...", host, port)
    client.connect(host, port, keepalive=60)

    try:
        log.info("subscriber running… Ctrl+C to stop.")
        client.loop_forever()
    except KeyboardInterrupt:
        log.info("stopping…")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
