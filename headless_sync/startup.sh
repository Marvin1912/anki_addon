#!/bin/bash
set -eu

# Setup cron schedule (every minute)
cat > /etc/cron.d/anki-scheduler <<EOF
* * * * * ANKI_USERNAME="$ANKI_USERNAME" ANKI_PASSWORD="$ANKI_PASSWORD" API_BASE_URL="$API_BASE_URL" SCHEDULE="$SCHEDULE" /usr/local/bin/python3 /app/sync_script.py
EOF
chmod 0644 /etc/cron.d/anki-scheduler
crontab /etc/cron.d/anki-scheduler

# Run sync script at startup
python3 /app/sync_script.py

# Start manual sync HTTP server in background
python3 /app/sync_server.py &

# Start cron in foreground
cron -f
