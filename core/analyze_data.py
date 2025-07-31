# ===========================================================
# ANALYZE DATA SCRIPT
#
# This script is responsible for:
# 1. Reading sensor data from the database
# 2. Generating various charts (saved to /charts folder)
# 3. Running anomaly detection and logging them to the database
#
# This runs every 10 cycles in the simulator script to keep things fresh.
# ===========================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sqlite3
from core.log_anomalies import log_anomalies_to_db
from core.detect_anomalies import detect_anomalies

# === Setup paths ===
ROOT_DIR = Path(__file__).resolve().parents[1]  # Go up one level from /core
DB_PATH = ROOT_DIR / "data" / "sensor_data.db"
CHARTS_DIR = ROOT_DIR / "charts"
CHARTS_DIR.mkdir(exist_ok=True)  # Create the charts folder if not there

# === Load data from the database ===
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query("SELECT* FROM sensor_logs", conn)

# Convert timestamp to datetime and strip timezone for Matplotlib
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
df["timestamp"] = df["timestamp"].dt.tz_convert(None)

# === Create time-based features ===
df["hour"] = df["timestamp"].dt.hour
df["day"] = df["timestamp"].dt.date
df["minute"] = df["timestamp"].dt.strftime('%Y-%m-%d %H:%M')
df["weekday"] = df["timestamp"].dt.day_name()

# === Chart 1: Average Pressure by Hour ===
df.groupby("hour")["pressure"].mean().plot(kind="bar", title="Average Pressure by Hour", ylabel="Pressure")
plt.tight_layout()
plt.savefig(CHARTS_DIR/"avg_pressure_by_hour.png")
plt.clf()

# === Chart 2: Average Pressure by Minute ===
ax = df.groupby("minute")["pressure"].mean().plot(kind="line", title="Average Pressure by Minute")
plt.xticks(rotation=45, fontsize=8)
plt.tight_layout()
plt.savefig(CHARTS_DIR/"avg_pressure_by_minute.png")
plt.clf()

# === Chart 3: Max Temperature by Day ===
df.groupby("day")["temperature"].max().plot(kind="bar", title="Max Temperature by Day", ylabel="Temperature")
plt.tight_layout()
plt.savefig(CHARTS_DIR/"max_temp_by_day.png")
plt.clf()

# === Chart 4: Average Vibration by Weekday ===
df.groupby("weekday")["vibration"].mean().reindex([
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]).plot(kind="bar", title="Avg Vibration by Weekday", ylabel="Vibration")
plt.tight_layout()
plt.savefig(CHARTS_DIR/"avg_vibration_by_weekday.png")
plt.clf()

# === Chart 5: Average Flow Rate by Hour ===
df.groupby("hour")["flow_rate"].mean().plot(kind="bar", title="Avg Flow Rate by Hour", ylabel="Flow Rate")
plt.tight_layout()
plt.savefig(CHARTS_DIR/"avg_flow_rate_by_hour.png")
plt.clf()

# === Chart 6: Average Humidity by Day ===
df.groupby("day")["humidity"].mean().plot(kind="bar", title="Avg Humidity by Day", ylabel="Humidity")
plt.tight_layout()
plt.savefig(CHARTS_DIR/"avg_humidity_by_day.png")
plt.clf()

# === Chart 7: Compressor ON/OFF breakdown by Day ===
compressor_counts = df.groupby(["day", "compressor_status"]).size().unstack(fill_value=0)
compressor_counts.columns = ["OFF", "ON"]  # Rename columns for clarity
compressor_counts.plot(kind="bar", stacked=True, title="Compressor ON/OFF by Day", ylabel="Count")
plt.tight_layout()
plt.savefig(CHARTS_DIR/"compressor_status_by_day.png")
plt.clf()

print("Analysis completed and charts updated.")

# === Detect anomalies and log them to the database ===
anomalies = detect_anomalies()
log_anomalies_to_db(anomalies)
print(anomalies)
