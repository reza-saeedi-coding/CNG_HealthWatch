"""
Smoke test for CNG HealthWatch pipeline.

Quickly checks the three main DB tables and prints counts + latest timestamps.
Exits with code 0 if all checks pass, 1 otherwise.

Run with:
    python -m tests.smoke_test
"""

import sqlite3
from pathlib import Path
from core.config import DB_PATH
from core.config import DB_PATH, DB_URL



def table_count(cur, name: str):
    """Return (count, latest_timestamp) for a given table name."""
    count = cur.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    latest = cur.execute(f"SELECT MAX(timestamp) FROM {name}").fetchone()[0]
    return count, latest


def main():
    import sys
    from datetime import datetime, timedelta, timezone

    db_path = Path(DB_PATH)
    if not db_path.exists():
        print(f"❌ DB not found: {db_path}")
        sys.exit(1)

    unhealthy = False
    now = datetime.now(timezone.utc)   # aware UTC time
    stale_limit = timedelta(minutes=10)

    with sqlite3.connect(str(db_path)) as con:
        cur = con.cursor()
        print(f"\nSmoke test on {DB_PATH}")
        backend = "MSSQL" if DB_URL.startswith(("mssql://", "mssql+pyodbc://")) else "SQLite"
        print(f"DB backend   : {backend}")
        print("-" * 50)

        for table in ["sensor_logs", "processed_logs", "anomalies"]:
            try:
                count, latest = table_count(cur, table)
                print(f"{table:15s} → {count:6d} rows (latest: {latest})")

                # Check: non-empty
                if count == 0:
                    unhealthy = True
                    print(f"❌ {table} is empty")

                # Check: freshness
                if latest:
                    try:
                        ts = datetime.fromisoformat(str(latest).replace("Z", "+00:00"))
                        if ts.tzinfo is None:  # force UTC if naive
                            ts = ts.replace(tzinfo=timezone.utc)

                        age = now - ts
                        if age > stale_limit:
                            unhealthy = True
                            print(f"❌ {table} data is stale (>10 minutes old); age={age}")
                    except Exception as e:
                        unhealthy = True
                        print(f"❌ could not parse timestamp for {table}: {e}")
            except Exception as e:
                unhealthy = True
                print(f"{table:15s} → ERROR: {e}")

        print("-" * 50)

    if unhealthy:
        sys.exit(1)
    else:
        print("✅ Smoke test passed: pipeline healthy")
        sys.exit(0)


if __name__ == "__main__":
    main()
