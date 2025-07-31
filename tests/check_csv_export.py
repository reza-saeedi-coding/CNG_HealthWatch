"""
check_csv_export.py

This script checks whether a specific summary CSV file (such as temperature by hour)
exists and is correctly formatted. It prints the first few rows and verifies the
number of unique hours to confirm that data export worked as expected.

Intended for debugging and testing CSV export functionality.
Place this file in the `tests/` directory.
"""

import pandas as pd

# Path to the exported summary CSV (adjust if needed)
csv_path = "../exports/avg_temperature_by_hour.csv"

try:
    # Attempt to read the CSV
    df = pd.read_csv(csv_path)
    print("\nCSV loaded successfully.")

    # Display sample rows and basic stats
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nTotal rows:", len(df))
    print("Unique hours:", df['hour'].nunique())

except FileNotFoundError:
    print(f"\nFile not found: {csv_path}")
    print("Make sure the CSV was generated and exists in the 'exports/' folder.")

except Exception as e:
    print("\nAn error occurred:")
    print(str(e))
