#!/bin/bash
# Run on PythonAnywhere (Bash console) to deploy the latest code from GitHub.
# The live database (db.sqlite3) is git-ignored, so pulling never overwrites it.
set -euo pipefail

# Wrapped in braces so bash reads the whole script before running it:
# `git pull` may replace this file mid-run.
{
    APP_DIR="$HOME/campus-skillswap"
    VENV="$HOME/venv"
    WSGI_FILE="/var/www/${USER}_pythonanywhere_com_wsgi.py"

    cd "$APP_DIR"

    # Keep one backup of the live database, replaced on every deploy.
    # SQLite's backup API makes a safe copy even while the site is running.
    "$VENV/bin/python" -c "import sqlite3; sqlite3.connect('db.sqlite3').backup(sqlite3.connect('$HOME/db-backup.sqlite3'))"
    echo "Backed up database to ~/db-backup.sqlite3"

    git pull --ff-only
    "$VENV/bin/pip" install -q -r requirements.txt
    "$VENV/bin/python" manage.py migrate --noinput
    "$VENV/bin/python" manage.py collectstatic --noinput
    "$VENV/bin/python" manage.py check
    touch "$WSGI_FILE" # tells PythonAnywhere to reload the site
    echo "Deployed $(git rev-parse --short HEAD)"
    exit
}
