# core/config.py
"""
Centralized configuration for the SAFE IoT Monitoring project.
Small, no-risk: just constants with sensible defaults + env var overrides.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

# Project root (…/SAFE_IoT_Monitoring)
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

# Data directory (…/SAFE_IoT_Monitoring/data)
DATA_DIR: Path = PROJECT_ROOT / "data"

# SQLite database path (override with env var DB_PATH if needed)
# Example override:
#   Linux/mac: DB_PATH=/custom/sensor_data.db python scripts/run_analyzer_loop.py
#   Windows PS: $env:DB_PATH="C:\\custom\\sensor_data.db"; python scripts\run_analyzer_loop.py
DB_PATH: Path = Path(os.getenv("DB_PATH", DATA_DIR / "sensor_data.db"))

# Local timezone for display/exports (used instead of hardcoded offsets)
# Default matches your current usage; override with env var LOCAL_TZ if needed.
LOCAL_TZ: str = os.getenv("LOCAL_TZ", "Europe/Rome")

# Database URL (adapter-friendly). Defaults to SQLite file unless overridden.
DB_URL: str = os.getenv("DB_URL", f"sqlite:///{DB_PATH}")
