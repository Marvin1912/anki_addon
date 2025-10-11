"""
Configuration constants for Anki Vocabulary Addon.
"""

# API Configuration
API_BASE_URL = "http://localhost:9001"
FLASHCARDS_ENDPOINT = f"{API_BASE_URL}/vocabulary/flashcards"

# HTTP Headers
JSON_HEADERS = {'content-type': 'application/json; charset=utf-8'}

# Anki Configuration
DEFAULT_MODEL_NAME = "Einfach"
ANKI_FIELD_FRONT = "Vorderseite"
ANKI_FIELD_BACK = "Rückseite"
ANKI_FIELD_DESCRIPTION = "Description"

# UI Configuration
WINDOW_TITLE_CHANGED_CARDS = "Changed Cards"
WINDOW_TITLE_ERROR = "Synchronization Error"
WINDOW_MINIMUM_SIZE = (400, 300)
MENU_ACTION_TEXT = "Import cards from server"

# Logging
LOG_NO_CARDS_CREATED = "No card was created (possible duplicate or empty fields)."
LOG_CARD_NOT_FOUND = "Card with guid {guid} not found"