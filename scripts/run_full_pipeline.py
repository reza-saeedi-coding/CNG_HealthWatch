# ===========================================================
# RUN FULL PIPELINE (OS-portable)
#
# Starts the end-to-end stack as separate processes:
# - core.simulate_sensors         (ingest)
# - core.transform_logs           (transform)
# - scripts.run_analyzer_loop     (anomaly detection loop)
# - scripts.run_export_loop       (exports every 5 minutes)
#
# How to run (from project root):
#   python -m scripts.run_full_pipeline
#
# Stop with Ctrl+C; this script will terminate child processes.
# ===========================================================

import subprocess
import sys
import time
import os

PROCS = []

def spawn(module: str):
    """Start a module as a child process with the current interpreter."""
    p = subprocess.Popen([sys.executable, "-m", module])
    PROCS.append((module, p))
    print(f"▶ Started {module} (pid={p.pid})")

def main():
    try:
        ingest_mode = os.getenv("INGEST_MODE", "sim").lower()  # "sim" or "mqtt"
        ingest_module = "core.simulate_sensors" if ingest_mode == "sim" else "ingest.mqtt_subscriber"

        # Ingest + pipelines
        spawn(ingest_module)
        time.sleep(1)  # small stagger helps with logs
        spawn("core.transform_logs")
        time.sleep(1)
        spawn("scripts.run_analyzer_loop")
        time.sleep(1)
        spawn("scripts.run_export_loop")

        print("\n Full pipeline running. Press Ctrl+C to stop.\n")
        # Keep the supervisor alive while children run
        while True:
            # Optionally, check if any child died and print status
            still_running = []
            for mod, p in PROCS:
                ret = p.poll()
                if ret is None:
                    still_running.append((mod, p))
                else:
                    print(f" {mod} exited with code {ret}")
            PROCS[:] = still_running
            if not PROCS:
                print("All child processes exited.")
                break
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n Stopping… (Ctrl+C)")
    finally:
        # Terminate children
        for mod, p in PROCS:
            try:
                p.terminate()
                print(f"Terminated {mod} (pid={p.pid})")
            except Exception:
                pass

if __name__ == "__main__":
    main()
