# ===========================================================
# ANOMALY DETECTION SCRIPT
#
# This script analyzes the latest processed sensor data to detect
# any unusual behaviors using simple z-score analysis. If any
# metric falls outside its expected range, it's flagged.
#
# This is a placeholder for more advanced models in the future
# (e.g. Isolation Forest, Prophet, LSTM).
# ===========================================================

import pandas as pd
import sqlite3
from pathlib import Path


def detect_anomalies():
    # === Setup database path ===
    DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sensor_data.db"

    # === Load the latest 10,000 processed rows from the database ===
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM processed_logs ORDER BY id DESC LIMIT 300", conn)

    # === Just look at the most recent 100 entries ===
    recent_data = df.tail(100)
    print(recent_data)

    # === Calculate mean and standard deviation for each sensor ===
    mean_pressure = recent_data["pressure"].mean()
    std_pressure = recent_data["pressure"].std()

    mean_temperature = recent_data["temperature"].mean()
    std_temperature = recent_data["temperature"].std()

    mean_flow_rate = recent_data["flow_rate"].mean()
    std_flow_rate = recent_data["flow_rate"].std()

    mean_vibration = recent_data["vibration"].mean()
    std_vibration = recent_data["vibration"].std()

    mean_humidity = recent_data["humidity"].mean()
    std_humidity = recent_data["humidity"].std()

    # === Z-scores for the latest entry (how far from average it is) ===
    latest_pressure = recent_data["pressure"].iloc[-1]
    z_pressure = (latest_pressure - mean_pressure)/std_pressure
    print("Z-score Pressure:", round(z_pressure, 2))

    latest_temperature = recent_data["temperature"].iloc[-1]
    z_temperature = (latest_temperature - mean_temperature)/std_temperature
    print("Z-score Temperature:", round(z_temperature, 2))

    latest_flow_rate = recent_data["flow_rate"].iloc[-1]
    z_flow_rate = (latest_flow_rate - mean_flow_rate)/std_flow_rate
    print("Z-score Flow Rate:", round(z_flow_rate, 2))

    latest_vibration = recent_data["vibration"].iloc[-1]
    z_vibration = (latest_vibration - mean_vibration)/std_vibration
    print("Z-score Vibration:", round(z_vibration, 2))

    latest_humidity = recent_data["humidity"].iloc[-1]
    z_humidity = (latest_humidity - mean_humidity)/std_humidity
    print("Z-score Humidity:", round(z_humidity, 2))

    # === Check for anomalies based on z-score thresholds ===
    anomalies = {}

    if abs(z_pressure) > 2.5:
        print("Anomaly Detected in Pressure!")
        anomalies["pressure"] = {"value": latest_pressure, "z-score": round(z_pressure, 2)}

    if abs(z_temperature) > 1.0:
        print("Anomaly Detected in Temperature!")
        anomalies["temperature"] = {"value": latest_temperature, "z-score": round(z_temperature, 2)}

    if abs(z_flow_rate) > 2.0:
        print("Anomaly Detected in Flow Rate!")
        anomalies["flow_rate"] = {"value": latest_flow_rate, "z-score": round(z_flow_rate, 2)}

    if abs(z_vibration) > 2.0:
        print("Anomaly Detected in Vibration!")
        anomalies["vibration"] = {"value": latest_vibration, "z-score": round(z_vibration, 2)}

    if abs(z_humidity) > 0.1:
        print("Anomaly Detected in Humidity!")
        anomalies["humidity"] = {"value": latest_humidity, "z-score": round(z_humidity, 2)}

    print("Collected anomalies:", anomalies)
    return anomalies


# === For standalone testing ===
if __name__ == "__main__":
    result = detect_anomalies()
    print(result)
