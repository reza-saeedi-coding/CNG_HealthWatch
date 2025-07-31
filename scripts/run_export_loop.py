# ===========================================================
# CSV EXPORT LOOP SCRIPT
#
# This script runs continuously in the background and executes the
# `export_summary_csvs.py` script every 5 minutes using the virtual environment's Python interpreter.
# Useful for periodically exporting summaries for external dashboards, reports, or backup.
# ===========================================================

import time
import subprocess
from pathlib import Path

# Path to the script that performs the summary CSV export
EXPORT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_summary_csvs.py"

print("Export loop started. Will export every 5 minutes...")

while True:
    print("Exporting summary CSVs...")
    try:
        # Use the virtual environment's Python interpreter to run the export script
        subprocess.run(
            [
                str(Path(__file__).resolve().parents[1] / ".venv" / "Scripts" / "python.exe"),
                str(EXPORT_SCRIPT)
            ],
            check=True
        )
        print("Export completed.")
    except subprocess.CalledProcessError as e:
        print("Export failed:", e)

    # Sleep for 5 minutes (300 seconds) before next export
    time.sleep(300)
