FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy core library
COPY anki_addon_server/anki_sync_core /app/anki_sync_core

# Copy headless scripts and startup script
COPY headless_sync/sync_script.py /app/
COPY headless_sync/sync_server.py /app/
COPY headless_sync/startup.sh /app/
RUN chmod +x /app/sync_script.py /app/sync_server.py /app/startup.sh

# Install Anki and requests
RUN pip install --no-cache-dir anki requests

# Create log directory
RUN mkdir -p /var/log

# Environment variables (can be overridden at runtime)
ENV ANKI_USERNAME=""
ENV ANKI_PASSWORD=""
ENV API_BASE_URL=""
ENV SCHEDULE="0 */6 * * *"

# Manual sync HTTP server
EXPOSE 8000

# Run startup script
CMD ["./startup.sh"]
