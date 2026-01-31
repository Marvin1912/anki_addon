#!/bin/bash

# Run sync script at startup
python3 /app/sync_script.py

# Start cron in foreground
cron -f