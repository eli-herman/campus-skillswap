#!/bin/bash
# Copies the live SQLite database to ~/backups and keeps the newest 7 copies.
# Uses SQLite's backup API, which is safe while the site is running.
set -euo pipefail

BACKUP_DIR="$HOME/backups"
mkdir -p "$BACKUP_DIR"

"$HOME/venv/bin/python" - "$HOME/campus-skillswap/db.sqlite3" "$BACKUP_DIR" <<'PY'
import datetime
import sqlite3
import sys

source_path, backup_dir = sys.argv[1], sys.argv[2]
stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
target_path = f'{backup_dir}/db-{stamp}.sqlite3'
with sqlite3.connect(source_path) as source, sqlite3.connect(target_path) as target:
    source.backup(target)
print(f'Backed up to {target_path}')
PY

ls -1t "$BACKUP_DIR"/db-*.sqlite3 | tail -n +8 | xargs -r rm --
