# run_export_wrapper.py
#
# Description:
# This script runs two threads:
#   1. One that triggers the full pipeline using run_full_pipeline.py
#   2. One that triggers export_summary_csvs.py every 60 seconds
# It is useful when you want to run both the full data transformation + anomaly detection
# and the summary export in parallel from a single entry point.

import subprocess
import time
import sys
from pathlib import Path
import threading

BASE = Path(__file__).resolve().parent
scripts_dir = BASE
core_dir = BASE / "../core"
PYTHON_EXEC = sys.executable

def run_script(label, path):
    """Run a given Python script and report status."""
    print(f"Running {label}...")
    try:
        subprocess.run([PYTHON_EXEC, str(path)], check=True)
        print(f"{label} completed.\n")
    except subprocess.CalledProcessError as e:
        print(f"{label} failed: {e}\n")

def run_full_pipeline_loop():
    """Starts the full pipeline script (already contains a loop)."""
    run_script("Run Full Pipeline", scripts_dir / "run_full_pipeline.py")

def export_summary_loop():
    """Exports summary CSVs every 60 seconds."""
    while True:
        run_script("Export Summary CSVs", scripts_dir / "export_summary_csvs.py")
        print("Waiting 60s to export summaries again...\n")
        time.sleep(60)

if __name__ == "__main__":
    print("Wrapper started: running full pipeline + export summaries every 60s...\n")

    # Run full pipeline in a background thread
    threading.Thread(target=run_full_pipeline_loop, daemon=True).start()

    # Run export summary in the main thread
    export_summary_loop()
