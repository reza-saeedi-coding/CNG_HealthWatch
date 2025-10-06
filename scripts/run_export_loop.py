# ===========================================================
# CSV EXPORT LOOP SCRIPT
#
# What this does
# --------------
# Runs forever and, every 5 minutes, executes `scripts/export_summary_csvs.py`
# using your *Windows* virtual environment interpreter. This keeps the
# summary CSV files in `data/exports/` up to date for dashboards/reports.
#
# How to run (Windows PowerShell, from project root)
# --------------------------------------------------
#   python scripts/run_export_loop.py
# (Leave this terminal open; press Ctrl + C to stop.)
#
# Output / side effects
# ---------------------
# - On each run, prints status to the console.
# - Updates/creates CSVs under:  <project>\data\exports\*.csv
#
# Customize
# ---------
# - Change the frequency: adjust `time.sleep(300)` (seconds).
# - If your venv path is different, update the interpreter path below.
#
# Cross-platform tip (optional)
# -----------------------------
# This file is currently Windows-specific because it calls:
#   <project>\.venv\Scripts\python.exe
# If you need it to work on Linux/macOS too, replace the `subprocess.run(...)`
# call to use the *current* interpreter:
#
#     import sys
#     subprocess.run([sys.executable, str(EXPORT_SCRIPT)], check=True)
#
# Troubleshooting
# ---------------
# - If you see "FileNotFoundError" for the interpreter, your venv path differs.
#   Point the path below to the correct python.exe inside your .venv.
# - If exports don’t appear, try running `python scripts/export_summary_csvs.py`
#   once manually and check for errors.
# ===========================================================

import time
import subprocess
from pathlib import Path
import sys

# Path to the script that performs the summary CSV export
EXPORT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_summary_csvs.py"

print("Export loop started. Will export every 5 minutes...")

while True:
    print("Exporting summary CSVs...")
    try:
        # Use the virtual environment's Python interpreter to run the export script (Windows-specific)
        subprocess.run([sys.executable, "-m", "scripts.export_summary_csvs"], check=True)
        print("Export completed.")
    except subprocess.CalledProcessError as e:
        print("Export failed:", e)

    # Sleep for 5 minutes (300 seconds) before next export
    time.sleep(300)
