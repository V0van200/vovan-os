#!/usr/bin/env python3
"""Create a verified, private SQLite backup of the VOVAN OS Hub state."""
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

source = Path("/data/vovan-os-hub/state/hub.sqlite3")
target_dir = Path("/data/vovan-os-hub/backups/hub-api")
target_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
os.chmod(target_dir, 0o700)
if not source.exists():
    raise SystemExit("Hub API database does not exist yet.")
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
fd, tmp_name = tempfile.mkstemp(prefix=".hub-api-", suffix=".sqlite3", dir=target_dir)
os.close(fd)
tmp = Path(tmp_name)
target = target_dir / f"{stamp}.sqlite3"
try:
    with sqlite3.connect(source) as src, sqlite3.connect(tmp) as dst:
        src.backup(dst)
        result = dst.execute("PRAGMA quick_check").fetchone()[0]
        if result != "ok":
            raise RuntimeError("SQLite backup verification failed.")
    os.chmod(tmp, 0o600)
    os.replace(tmp, target)
    old = sorted(target_dir.glob("*.sqlite3"), reverse=True)
    for path in old[14:]:
        path.unlink()
    print(f"Hub API backup verified: {target.name}")
finally:
    tmp.unlink(missing_ok=True)

