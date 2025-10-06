# tools/dump_file_timeline.py
"""
Thesis helper — Dump file modification timeline

Scans your project folder and writes a CSV listing every file's path and its
last-modified timestamp. Use this to backfill your thesis log with realistic dates.

Output
------
docs/THESIS_FILE_TIMELINE.csv  with columns: path, last_modified (local time)

How to run
----------
From the project root:
    python tools/dump_file_timeline.py

Customize (optional)
--------------------
- EXCLUDE_DIRS: add folders you don’t want scanned (e.g., build, node_modules).
- This uses the OS "modified time" (mtime). If you need exact history, prefer git log.

Limitations
-----------
- mtime can change if files are copied/moved.
- Times are local to your machine; another PC may show different timezones.
"""

import csv
import time
from pathlib import Path

# project root = parent of /tools
ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}
OUT = ROOT / "docs" / "THESIS_FILE_TIMELINE.csv"

rows = []
for p in ROOT.rglob("*"):
    if not p.is_file():
        continue
    parts = set(p.parts)
    if parts & EXCLUDE_DIRS:
        continue
    mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime))
    rows.append([str(p.relative_to(ROOT)), mtime])

OUT.parent.mkdir(parents=True, exist_ok=True)
rows.sort(key=lambda r: r[1])

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["path", "last_modified"])
    w.writerows(rows)

print("Wrote", OUT)
