# core/db.py
from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import urlparse, unquote

from core.config import DB_PATH, DB_URL  # DB_URL may come from .env


def _resolve_db_url() -> str:
    """DB_URL from env, else fallback to sqlite file via DB_PATH."""
    url = (DB_URL or "").strip()
    if url:
        return url
    path = str(DB_PATH)
    return f"sqlite:///{path}" if not path.startswith("sqlite:///") else path


def _connect_sqlite(sqlite_url: str) -> sqlite3.Connection:
    # "sqlite:///./data/sensor_data.db" -> "./data/sensor_data.db"
    path_str = unquote(sqlite_url.replace("sqlite:///", "", 1))
    p = Path(path_str)
    p.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(p), timeout=30, check_same_thread=False)


def _connect_mssql(mssql_url: str):
    """
    Future: MS-SQL via pyodbc.
    .env example:
      DB_URL=mssql+pyodbc://USER:PASS@SERVER:1433/DBNAME?driver=ODBC+Driver+17+for+SQL+Server
    """
    import pyodbc  # requires installing pyodbc + SQL Server ODBC driver
    parsed = urlparse(mssql_url)
    user = parsed.username or ""
    pwd = parsed.password or ""
    host = parsed.hostname or "localhost"
    port = parsed.port or 1433
    dbname = parsed.path.lstrip("/") or ""
    qs = {}
    if parsed.query:
        for kv in parsed.query.split("&"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                qs[k] = v
    driver = qs.get("driver", "ODBC Driver 17 for SQL Server")
    conn_str = (
        f"Driver={{{driver}}};Server={host},{port};Database={dbname};"
        f"UID={user};PWD={pwd};TrustServerCertificate=Yes;Encrypt=Yes;"
    ).format(driver=driver)
    return pyodbc.connect(conn_str, timeout=15)


def get_connection():
    """Return a DB connection based on DB_URL scheme."""
    url = _resolve_db_url()
    if url.startswith("sqlite:///"):
        return _connect_sqlite(url)
    if url.startswith("mssql://") or url.startswith("mssql+pyodbc://"):
        return _connect_mssql(url)
    raise ValueError(f"Unsupported DB_URL: {url}")
