# run_full_pipeline.py
#
# Description:
# This script runs the full data pipeline in a loop every 1 minute.
# It executes:
#   1. transform_logs.py - transforms raw logs into processed format
#   2. analyze_data.py - detects anomalies in the processed data
#   3. run_export_wrapper.py - exports summary statistics to CSV
# Useful for automating all stages of the data flow during development or testing.

import subprocess
import time
import sys
from pathlib import Path

# Define base paths
BASE = Path(__file__).resolve().parent
core_dir = BASE / "../core"
scripts_dir = BASE

# Use current Python interpreter
PYTHON_EXEC = sys.executable

def run_script(label, path):
    """Run a script and report the result."""
    print(f"Running {label}...")
    try:
        subprocess.run([PYTHON_EXEC, str(path)], check=True)
        print(f"{label} completed.\n")
    except subprocess.CalledProcessError as e:
        print(f"{label} failed: {e}\n")

if __name__ == "__main__":
    print("Full Pipeline started. Will run every 1 minute.\n")
    while True:
        run_script("Transform Logs", core_dir / "transform_logs.py")
        run_script("Analyze Data", core_dir / "analyze_data.py")
        run_script("Export Summary Wrapper", scripts_dir / "run_export_wrapper.py")
        print("Waiting 1 minute...\n")
        time.sleep(60)
