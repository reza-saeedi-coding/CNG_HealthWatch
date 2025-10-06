"""
Sensor Data Migration Script
----------------------------
This script reads sensor data from a CSV file (`sensor_log.csv`) and inserts it
into a SQLite database (`sensor_data.db`) under the `sensor_logs` table.

Key Features:
- Uses `pandas` to load data from CSV
- Iterates through each row to insert into SQLite using parameterized queries
- Skips faulty rows with error handling (won't crash on bad data)
- Prints how many rows were successfully migrated

Use Case:
- Useful for initial bulk import of historical sensor data
- Can be reused for periodic CSV-based batch imports
"""

import pandas as pd
import sqlite3
from pathlib import Path
from core.config import DATA_DIR, DB_PATH

CSV_PATH = DATA_DIR / "sensor_log.csv"


# Load the sensor data from CSV into a pandas DataFrame
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} rows from CSV.")

# Connect to the SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Counter to track how many rows were successfully inserted
row_count = 0

# Iterate through the DataFrame and insert each row into the `sensor_logs` table
for _, row in df.iterrows():
    try:
        cursor.execute("""
            INSERT INTO sensor_logs (
                timestamp, pressure, temperature, flow_rate,
                vibration, humidity, compressor_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row["timestamp"],
            row["pressure"],
            row["temperature"],
            row["flow_rate"],
            row["vibration"],
            row["humidity"],
            row["compressor_status"]
        ))
        row_count += 1
    except Exception as e:
        # Log the error and skip the faulty row
        print(f"Failed to insert row: {e}")
        continue

# Commit the transaction and close the connection
conn.commit()
conn.close()

print(f"Migration Complete. Inserted {row_count} rows into sensor_logs.")
