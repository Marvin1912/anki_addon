# Anki Vocabulary Sync

A powerful, modular system for synchronizing flashcards between Anki and external Vocabulary API servers. This project provides both a GUI addon for Anki Desktop and a headless Docker container for automated synchronization.

## Features

- **Shared Core Library**: Business logic separated from UI, enabling multiple frontends
- **GUI Addon**: Full-featured Anki addon with menu integration and result dialogs
- **Headless Docker Sync**: Automated, scheduled synchronization with AnkiWeb sync
- **Bidirectional Synchronization**: Import and sync flashcards from external vocabulary API servers
- **Automatic Deck Management**: Automatically creates decks if they don't exist
- **Smart Card Matching**: Uses GUIDs to prevent duplicate cards and handle updates
- **Background Processing**: Synchronization runs in the background without blocking Anki
- **Error Handling**: Robust error handling with detailed logging
- **Configuration Management**: Unified configuration supporting both file-based and environment-based settings

## Architecture

```
anki_addon_server/               # Standalone server-sync addon
├── __init__.py                  # Addon initialization and menu setup
├── ui_components.py             # GUI dialogs and components
└── anki_sync_core/              # Bundled core logic (duplicated for this addon)
    ├── config.py
    ├── models.py
    ├── api_client.py
    ├── anki_manager.py
    └── synchronizer.py

anki_addon_file/                 # Standalone file-import addon
├── __init__.py                  # Addon initialization and menu setup
├── ui_components.py             # GUI dialogs and components
└── anki_sync_core/              # Bundled core logic (duplicated for this addon)
    ├── config.py
    ├── models.py
    ├── anki_manager.py
    └── file_importer.py
│
├── headless_sync/               # Headless Docker sync (uses core library)
│   ├── sync_script.py           # Headless synchronization script
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
└── tests/                       # Shared tests for core library
```

## Components

### 1. Anki Sync Core Library (`anki_sync_core/`)

The core library contains all business logic without any GUI dependencies. It can be used independently in both GUI and headless environments.

**Key Classes:**
- `SyncConfig`: Unified configuration with support for environment variables
- `FlashCard`: Data model for flashcards
- `CardResult`: Result model for sync operations
- `VocabularyAPIClient`: HTTP client for API communication
- `AnkiCardManager`: Manager for Anki collection operations
- `FlashcardSynchronizer`: Main synchronization coordinator

### 2. Anki GUI Addon (`anki_addon/`)

Provides GUI integration for Anki Desktop with menu integration and result dialogs.

**Installation:**
1. Copy the `anki_addon/` directory to your Anki addons folder
2. Restart Anki
3. Access via `Tools` > `Import cards from server`

### 3. Headless Docker Sync (`headless_sync/`)

Provides automated, scheduled synchronization without GUI, with automatic AnkiWeb sync.

**Quick Start:**
```bash
cd headless_sync
cp .env.example .env
# Edit .env with your credentials
docker-compose up -d
```

## Requirements

### For GUI Addon
- Anki 2.1+ (desktop version)
- Python 3.7+
- Access to a Vocabulary API server

### For Headless Sync
- Docker and Docker Compose
- AnkiWeb account
- Access to a Vocabulary API server

## Configuration

### API Settings

The addon expects a RESTful API with the following endpoints:

#### GET /vocabulary/flashcards?updated=true
Returns a list of updated flashcards in JSON format:

```json
[
  {
    "deck": "German Vocabulary",
    "front": "das Haus",
    "back": "house",
    "updated": true,
    "id": 123,
    "ankiId": "guid-string",
    "description": "Basic building"
  }
]
```

#### PUT /vocabulary/flashcards
Creates or updates flashcards. Send the same JSON format as above.

### Configuration Options

Configuration can be set via:
1. **Code**: Modify `anki_sync_core/config.py` defaults
2. **Environment Variables**: For headless sync (see `.env.example`)

**Key Configuration Options:**
- `API_BASE_URL`: API endpoint (default: `http://backend.home-lab.com`)
- `DEFAULT_MODEL_NAME`: Anki model name (default: "Einfach")
- `ANKI_FIELD_FRONT`: Front field name (default: "Vorderseite")
- `ANKI_FIELD_BACK`: Back field name (default: "Rückseite")
- `ANKI_FIELD_DESCRIPTION`: Description field name (default: "Description")
- `ANKI_IMPORT_FILE_PATH`: Path to the newline-delimited JSON import file
- `ANKI_IMPORT_DECK_FORWARD_NAME`: Forward deck name (default: "Language A->B")
- `ANKI_IMPORT_DECK_REVERSE_NAME`: Reverse deck name (default: "Language B->A")

## Usage

### GUI Addon Usage

1. Open Anki
2. Go to `Tools` menu
3. Install one addon at a time (either `anki_addon_server/` or `anki_addon_file/`).
4. Server addon: click on "Import cards from server" to sync updated cards from the API.
5. File addon: click on "Import cards from file" to import from a local file.
6. The file import flow will:
   - Read the configured import file
   - Show a deck selection dialog with counts for forward and reverse decks
   - Create new cards in the selected decks
   - Show a results dialog with processed cards

### Headless Sync Usage

1. Copy your Anki collection file to `headless_sync/anki-data/`
2. Configure environment variables in `.env`
3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```
4. View logs:
   ```bash
   docker-compose logs -f
   ```

## Development

### Project Structure

```
anki_addon/
├── anki_sync_core/              # Shared core library
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── api_client.py
│   ├── anki_manager.py
│   └── synchronizer.py
│
├── anki_addon/                  # GUI addon
│   ├── __init__.py
│   └── ui_components.py
│
├── headless_sync/               # Headless sync
│   ├── sync_script.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
├── tests/                       # Tests
├── plans/                       # Planning documents
└── README.md
```

### Key Components

- **VocabularyAPIClient**: Handles HTTP communication with the API server
- **FlashcardSynchronizer**: Coordinates the synchronization process
- **AnkiCardManager**: Manages Anki database operations
- **FlashCard Model**: Represents flashcard data structure

### Testing

Run tests for the core library:
```bash
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure your API server is running and accessible
2. **No Cards Imported**: Check if cards are marked as `updated: true` on the server
3. **Duplicate Cards**: Verify GUID consistency between Anki and the API
4. **Field Mapping Issues**: Check that your Anki model has the required fields

### Logs

- **GUI Addon**: Check Anki's debug console (`Tools` > `Debug Console`)
- **Headless Sync**: Check Docker logs (`docker-compose logs -f`)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with both GUI and headless modes
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Anki's addon documentation
3. Open an issue in the project repository

---

**Note**: This project requires a running Vocabulary API server to function properly. Make sure your server is accessible at the configured URL before attempting synchronization.
