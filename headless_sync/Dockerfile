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

# Install Anki and requests
RUN pip install --no-cache-dir anki requests

# Setup cron schedule (every 6 hours by default)
# Format: minute hour day month day-of-week
# 0 */6 * * * means at minute 0 of every 6th hour
RUN echo "0 */6 * * * root python /app/sync_script.py >> /var/log/anki.log 2>&1" > /etc/cron.d/anki-scheduler
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

# Run cron in foreground
CMD ["cron", "-f"]
