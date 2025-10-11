# Anki Vocabulary Addon

A powerful Anki addon that synchronizes flashcards with an external Vocabulary API server, enabling seamless integration between your local Anki collection and remote vocabulary databases.

## Features

- **Bidirectional Synchronization**: Import and sync flashcards from external vocabulary API servers
- **Automatic Deck Management**: Automatically creates decks if they don't exist
- **Smart Card Matching**: Uses GUIDs to prevent duplicate cards and handle updates
- **Background Processing**: Synchronization runs in the background without blocking Anki
- **Error Handling**: Robust error handling with detailed logging
- **User-Friendly Interface**: Simple menu integration with results dialog

## Requirements

- Anki 2.1+ (desktop version)
- Python 3.7+
- Access to a Vocabulary API server (default: `http://localhost:9001`)

## Installation

1. Download the addon files
2. In Anki, go to `Tools` > `Add-ons` > `Get Add-ons...`
3. Copy the addon code to the clipboard
4. Paste it into the "Code" field and click "OK"
5. Restart Anki

## Configuration

The addon can be configured by modifying the `addon_config.py` file:

### API Settings
- **API Base URL**: Default is `http://localhost:9001`
- **Flashcards Endpoint**: `http://localhost:9001/vocabulary/flashcards`

### Anki Field Mapping
- **Default Model**: "Einfach" (Basic model)
- **Front Field**: "Vorderseite" (German for compatibility)
- **Back Field**: "Rückseite" (German for compatibility)
- **Description Field**: "Description"

## Usage

### Basic Synchronization

1. Open Anki
2. Go to `Tools` menu
3. Click on "Import cards from server"
4. The addon will:
   - Connect to the configured Vocabulary API
   - Fetch updated flashcards
   - Create new cards or update existing ones
   - Show a results dialog with processed cards

### What Happens During Sync

1. **Fetch Updated Cards**: The addon requests flashcards marked as updated from the API
2. **Process Each Card**:
   - Creates deck if it doesn't exist
   - Checks if card already exists using GUID
   - Creates new cards or updates existing ones
   - Marks cards as synchronized on the server
3. **Display Results**: Shows how many cards were processed

## API Integration

The addon expects a RESTful API with the following endpoints:

### GET /vocabulary/flashcards?updated=true
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

### PUT /vocabulary/flashcards
Creates or updates flashcards. Send the same JSON format as above.

## Development

### Project Structure

```
anki_addon/
├── anki_voc/
│   ├── __init__.py          # Main addon initialization
│   ├── addon_config.py      # Configuration constants
│   ├── anki_operations.py   # Anki database operations
│   ├── models.py            # Data models (FlashCard, CardResult)
│   ├── synchronizer.py      # Main synchronization logic
│   ├── ui_components.py     # User interface components
│   └── vocabulary_api.py    # HTTP client for API communication
└── README.md
```

### Key Components

- **VocabularyAPIClient**: Handles HTTP communication with the API server
- **FlashcardSynchronizer**: Coordinates the synchronization process
- **AnkiCardManager**: Manages Anki database operations
- **FlashCard Model**: Represents flashcard data structure

### Error Handling

The addon includes comprehensive error handling:
- Network failures are logged and reported to users
- Individual card failures don't stop the entire sync process
- API errors are properly distinguished from other errors
- Detailed logging for troubleshooting

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure your API server is running and accessible
2. **No Cards Imported**: Check if cards are marked as `updated: true` on the server
3. **Duplicate Cards**: Verify GUID consistency between Anki and the API
4. **Field Mapping Issues**: Check that your Anki model has the required fields

### Logs

Check Anki's debug console (`Tools` > `Debug Console`) for detailed logs:
- Look for messages prefixed with `anki_voc`
- Errors include specific details about what went wrong

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with Anki
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Anki's addon documentation
3. Open an issue in the project repository

---

**Note**: This addon requires a running Vocabulary API server to function properly. Make sure your server is accessible at the configured URL before attempting synchronization.