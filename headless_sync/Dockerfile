FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy core library
COPY anki_sync_core /app/anki_sync_core

# Copy headless script
COPY headless_sync/sync_script.py /app/
RUN chmod +x /app/sync_script.py

# Install Anki and requests
RUN pip install --no-cache-dir anki requests

# Setup cron schedule (every minute)
# Format: minute hour day month day-of-week
# * * * * * means every minute
RUN echo "* * * * * root /usr/local/bin/python3 /app/sync_script.py >> /var/log/anki.log 2>&1" > /etc/cron.d/anki-scheduler
RUN chmod 0644 /etc/cron.d/anki-scheduler
RUN crontab /etc/cron.d/anki-scheduler

# Create log directory
RUN mkdir -p /var/log

# Environment variables (can be overridden at runtime)
ENV ANKI_COLLECTION_PATH=""
ENV ANKI_USERNAME=""
ENV ANKI_PASSWORD=""
ENV API_BASE_URL=""
ENV SCHEDULE="0 */6 * * *"

# Run sync script at startup, then run cron in foreground
CMD /bin/sh -c "/usr/local/bin/python3 /app/sync_script.py && cron -f"
