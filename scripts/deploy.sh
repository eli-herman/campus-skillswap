#!/bin/bash
# Run on PythonAnywhere (Bash console) to deploy the latest code from GitHub.
# The live database (db.sqlite3) is git-ignored, so pulling never overwrites it.
set -euo pipefail

APP_DIR="$HOME/campus-skillswap"
VENV="$HOME/venv"
WSGI_FILE="/var/www/${USER}_pythonanywhere_com_wsgi.py"

cd "$APP_DIR"
"$APP_DIR/scripts/backup_db.sh"           # safety copy before migrations
git pull --ff-only
"$VENV/bin/pip" install -q -r requirements.txt
"$VENV/bin/python" manage.py migrate --noinput
"$VENV/bin/python" manage.py collectstatic --noinput
"$VENV/bin/python" manage.py check
touch "$WSGI_FILE"                        # tells PythonAnywhere to reload the site
echo "Deployed $(git rev-parse --short HEAD)"
