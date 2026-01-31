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

# Copy headless script and startup script
COPY headless_sync/sync_script.py /app/
COPY headless_sync/startup.sh /app/
RUN chmod +x /app/sync_script.py /app/startup.sh

# Install Anki and requests
RUN pip install --no-cache-dir anki requests

# Setup cron schedule (every minute)
RUN echo "* * * * * env ANKI_USERNAME=\$ANKI_USERNAME ANKI_PASSWORD=\$ANKI_PASSWORD API_BASE_URL=\$API_BASE_URL SCHEDULE=\$SCHEDULE /usr/local/bin/python3 /app/sync_script.py >> /var/log/anki.log 2>&1" > /etc/cron.d/anki-scheduler
RUN chmod 0644 /etc/cron.d/anki-scheduler
RUN crontab /etc/cron.d/anki-scheduler

# Create log directory
RUN mkdir -p /var/log

# Environment variables (can be overridden at runtime)
ENV ANKI_USERNAME=""
ENV ANKI_PASSWORD=""
ENV API_BASE_URL=""
ENV SCHEDULE="0 */6 * * *"

# Run startup script
CMD ["./startup.sh"]
