"""
Anki Sync Core Library

This package provides the core functionality for synchronizing flashcards
between Anki and external Vocabulary API servers. It has no GUI dependencies
and can be used in both GUI addons and headless environments.

Main exports:
    - SyncConfig: Configuration class for sync operations
    - FlashCard: Data model for flashcards
    - CardResult: Result model for sync operations
    - VocabularyAPIClient: HTTP client for API communication
    - AnkiCardManager: Manager for Anki collection operations
    - FlashcardSynchronizer: Main synchronization coordinator
    - VocabularyAPIError: Exception for API errors
"""

from .config import SyncConfig, default_config
from .models import FlashCard, CardResult
from .anki_manager import AnkiCardManager
from .file_importer import FileDeckImporter, FileImportError, ImportSummary

__all__ = [
    'SyncConfig',
    'default_config',
    'FlashCard',
    'CardResult',
    'AnkiCardManager',
    'FileDeckImporter',
    'FileImportError',
    'ImportSummary',
]

__version__ = '1.0.0'
