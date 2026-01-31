#!/usr/bin/python3
"""
Headless Anki Vocabulary Synchronizer

Synchronizes flashcards from external API with Anki collection
and syncs with AnkiWeb. Designed to run in Docker container
on a scheduled basis.

This script uses the shared anki_sync_core library for all
business logic, with no GUI dependencies.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import anki_sync_core
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from anki.collection import Collection as aopen
from anki.sync import SyncAuth

# Import core library modules
from anki_sync_core import FlashcardSynchronizer, VocabularyAPIError, SyncConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def synchronize_and_sync(
    collection_path: str,
    anki_username: str,
    anki_password: str,
    config: SyncConfig = None
) -> bool:
    """
    Synchronize flashcards from API and sync with AnkiWeb.

    Args:
        collection_path: Path to Anki collection file
        anki_username: AnkiWeb username
        anki_password: AnkiWeb password
        config: SyncConfig instance. If None, uses default configuration.

    Returns:
        True if successful, False otherwise
    """
    try:
        # Open collection
        logger.info(f"Opening collection: {collection_path}")
        col = aopen(collection_path)

        try:
            # Sync with AnkiWeb at start to get latest collection
            logger.info("Syncing collection from AnkiWeb at start...")
            auth = col.sync_login(
                username=anki_username,
                password=anki_password,
                endpoint=None
            )
            output = col.sync_collection(auth=auth, sync_media=True)
            logger.info(f"Initial AnkiWeb sync completed: {output}")

            # Run synchronization using core library
            logger.info("Starting flashcard synchronization...")
            synchronizer = FlashcardSynchronizer(col, config)
            result = synchronizer.synchronize_updated_cards()

            logger.info(
                f"Synchronization completed. "
                f"{len(result.changed_cards)} cards processed."
            )

            # Sync with AnkiWeb again after API sync
            logger.info("Syncing with AnkiWeb after API sync...")
            auth = col.sync_login(
                username=anki_username,
                password=anki_password,
                endpoint=None
            )
            output = col.sync_collection(auth=auth, sync_media=True)
            logger.info(f"Final AnkiWeb sync completed: {output}")

            return True

        finally:
            # Always close collection
            col.close()
            logger.info("Collection closed")

    except VocabularyAPIError as e:
        logger.error(f"API communication failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return False


def main():
    """Main entry point for headless synchronization."""
    # Get configuration from environment variables
    collection_path = "/data/collection.anki2"
    anki_username = os.getenv("ANKI_USERNAME")
    anki_password = os.getenv("ANKI_PASSWORD")

    # Create configuration from environment variables
    config = SyncConfig.from_env()

    # Validate required configuration
    if not all([anki_username, anki_password]):
        logger.error(
            "Missing required environment variables. "
            "Please set ANKI_USERNAME and ANKI_PASSWORD."
        )
        sys.exit(1)

    # Log configuration (without sensitive data)
    logger.info(f"Collection path: {collection_path}")
    logger.info(f"API base URL: {config.api_base_url}")
    logger.info(f"Schedule: {config.schedule}")

    # Run synchronization
    success = synchronize_and_sync(
        collection_path=collection_path,
        anki_username=anki_username,
        anki_password=anki_password,
        config=config
    )

    if success:
        logger.info("Synchronization completed successfully")
        sys.exit(0)
    else:
        logger.error("Synchronization failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
