# Headless Anki Vocabulary Synchronizer

This project provides a headless Docker container for running the Anki Vocabulary Sync on a scheduled basis with automatic AnkiWeb sync.

## Overview

This implementation uses the shared `anki_sync_core` library to synchronize flashcards without any GUI dependencies. The container:

1. **Synchronizes flashcards** from external REST API
2. **Updates Anki collection** with new/modified cards
3. **Syncs with AnkiWeb** automatically
4. **Runs on schedule** via cron (default: every 6 hours)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Docker Container                    │
│  ┌──────────────────────────────────────┐   │
│  │  Cron Scheduler (every 6 hours)  │   │
│  └──────────────────────────────────────┘   │
│              ↓                              │
│  ┌──────────────────────────────────────┐   │
│  │  sync_script.py (Headless)       │   │
│  │  - Opens Anki collection          │   │
│  │  - Runs FlashcardSynchronizer     │   │
│  │  - Syncs with AnkiWeb            │   │
│  └──────────────────────────────────────┘   │
│           ↓              ↓                     │
│  ┌──────────────┐  ┌──────────────────┐        │
│  │ anki_sync_  │  │ anki_sync_core │        │
│  │ core/       │  │ (shared lib)   │        │
│  └──────────────┘  └──────────────────┘        │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Find Your Collection Path

First, find the path to your Anki collection file:

**Option 1: Using Anki Desktop**
1. Open Anki Desktop
2. Go to `Tools` > `Preferences` > `Backup`
3. Look for the "Collection folder" path
4. The collection file is named `collection.anki2` in that folder

**Option 2: Using Default Paths**

| OS | Default Path |
|-----|-------------|
| Linux | `~/.local/share/Anki2/User 1/collection.anki2` |
| macOS | `~/Library/Application Support/Anki2/User 1/collection.anki2` |
| Windows | `%APPDATA%\Anki2\User 1\collection.anki2` |

**Note**: Replace `User 1` with your actual Anki profile name if different.

### 2. Copy Your Collection

Copy your Anki collection file to the `anki-data` directory:

```bash
# Linux
cp ~/.local/share/Anki2/User\ 1/collection.anki2 headless_sync/anki-data/

# macOS
cp ~/Library/Application\ Support/Anki2/User\ 1/collection.anki2 headless_sync/anki-data/

# Windows
copy "%APPDATA%\Anki2\User 1\collection.anki2" headless_sync\anki-data\
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cd headless_sync
cp .env.example .env
# Edit .env with your credentials
nano .env
```

Required variables:
- `ANKI_USERNAME` - Your AnkiWeb username
- `ANKI_PASSWORD` - Your AnkiWeb password
- `ANKI_COLLECTION_PATH` - Path to collection file (default: `/data/collection.anki2`)

Optional variables:
- `API_BASE_URL` - Custom API endpoint (default: `http://backend.home-lab.com`)
- `SCHEDULE` - Cron schedule (default: `0 */6 * * *` = every 6 hours)

### 3. Build and Run

Using Docker Compose (recommended):

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Using Docker directly:

```bash
# Build image
docker build -t anki-vocab-sync -f headless_sync/Dockerfile ..

# Run container
docker run -d \
  --name anki-vocab-sync \
  --env-file headless_sync/.env \
  -v $(pwd)/headless_sync/anki-data:/data \
  -v $(pwd)/headless_sync/logs:/var/log \
  anki-vocab-sync
```

## File Structure

```
headless_sync/
├── sync_script.py         # Headless synchronization script
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Monitoring

### View Container Logs

```bash
# Docker logs
docker logs -f anki-vocabulary-sync

# Application logs
tail -f headless_sync/logs/anki.log
```

### Check Synchronization Status

Open your Anki collection in the GUI to verify that cards have been added/updated correctly.

## Configuration

### Schedule Format

The `SCHEDULE` variable uses cron format: `minute hour day month day-of-week`

Examples:
- `0 */6 * * *` - Every 6 hours (default)
- `0 */1 * * *` - Every hour
- `0 0 * * *` - Daily at midnight
- `*/15 * * * *` - Every 15 minutes
- `30 8 * * 1-5` - Weekdays at 8:30 AM

### Collection Path

The collection path depends on your operating system:

| OS | Default Path |
|-----|-------------|
| Linux | `~/.local/share/Anki2/User 1/collection.anki2` |
| macOS | `~/Library/Application Support/Anki2/User 1/collection.anki2` |
| Windows | `%APPDATA%\Anki2\User 1\collection.anki2` |

**Note**: Replace `User 1` with your actual Anki profile name if different.

**Finding Your Collection Path**:
1. Open Anki Desktop
2. Go to `Tools` > `Preferences` > `Backup`
3. Look for "Collection folder" path
4. The collection file is named `collection.anki2` in that folder

For Docker, mount the appropriate directory to `/data/collection.anki2`.

## Troubleshooting

### Container Won't Start

1. Check that all required environment variables are set
2. Verify that the collection file exists in `anki-data/`
3. Check Docker logs: `docker logs anki-vocabulary-sync`

### Synchronization Fails

1. Check application logs: `tail -f headless_sync/logs/anki.log`
2. Verify API endpoint is accessible
3. Verify AnkiWeb credentials are correct
4. Check that collection file is not corrupted

### Cards Not Appearing

1. Open collection in Anki GUI to verify
2. Check that you're using the correct profile
3. Verify deck names match API response

## Security

- **Never commit** `.env` file to version control
- **Use strong passwords** for AnkiWeb account
- **Limit API access** if possible
- **Monitor logs** for suspicious activity

## Development

### Testing Locally

To test the script without Docker:

```bash
# Install dependencies
pip install anki requests

# Run script
ANKI_COLLECTION_PATH=/path/to/collection.anki2 \
ANKI_USERNAME=your_username \
ANKI_PASSWORD=your_password \
python headless_sync/sync_script.py
```

### Modifying Schedule

Edit the `SCHEDULE` variable in `.env` and restart the container:

```bash
# Edit .env
nano headless_sync/.env

# Restart container
docker-compose restart
```

## How It Works

1. **Cron triggers** the script at scheduled intervals
2. **Script opens** Anki collection using pylib
3. **FlashcardSynchronizer** (from `anki_sync_core`) fetches updated cards from API
4. **Cards are created/updated** in Anki collection
5. **Collection is synced** with AnkiWeb
6. **Collection is closed** and script exits
7. **Process repeats** on next scheduled run

## Advantages Over GUI Add-on

| Feature | GUI Add-on | Headless Docker |
|----------|--------------|----------------|
| Manual execution | ✅ Required | ❌ Automated |
| Scheduling | ❌ No | ✅ Cron-based |
| Sync automation | ❌ Manual | ✅ Automatic |
| Resource usage | Higher (GUI) | Lower (headless) |
| 24/7 operation | ❌ No | ✅ Yes |
| Monitoring | Manual | Logs + Docker logs |
| Docker compatible | ❌ No | ✅ Yes |

## License

This implementation reuses code from the Anki Vocabulary Sync project, which is licensed under AGPL-3.0-or-later.

## Support

For issues with:
- **Anki itself**: Visit [Anki Forums](https://forums.ankiweb.net/)
- **This implementation**: Check logs and verify configuration
- **API endpoint**: Contact API provider
