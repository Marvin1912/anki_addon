"""
Flashcard synchronization coordinator.

This module provides the main synchronization logic, coordinating between
Anki operations and API communication.
"""

import logging
import time
from typing import List

from anki.collection import Collection, OpChanges

from .anki_manager import AnkiCardManager
from .api_client import VocabularyAPIClient, VocabularyAPIError
from .config import SyncConfig
from .models import FlashCard, CardResult
from .sync_tracking_client import SyncTrackingClient


class FlashcardSynchronizer:
    """
    Coordinates synchronization between Anki and the Vocabulary API.

    Handles the main synchronization logic, coordinating between
    Anki operations and API communication.

    This class has no GUI dependencies and can be used in both
    GUI addons and headless environments.
    """

    def __init__(self, collection: Collection, config: SyncConfig = None):
        """
        Initialize the synchronizer.

        Args:
            collection: Anki collection instance
            config: SyncConfig instance. If None, uses default configuration.
        """
        self.collection = collection
        self.config = config or SyncConfig()
        self.anki_manager = AnkiCardManager(collection, self.config)
        self.api_client = VocabularyAPIClient(self.config)
        self.tracking_client = SyncTrackingClient(self.config)
        self.logger = logging.getLogger(__name__)

    def synchronize_updated_cards(self) -> CardResult:
        """
        Synchronize updated cards from the API with Anki.

        This method:
        1. Fetches updated cards from the API
        2. For each card, creates or updates it in Anki
        3. Marks cards as synchronized on the API
        4. Returns a result with information about changed cards

        Returns:
            CardResult containing information about changed cards

        Raises:
            VocabularyAPIError: If API communication fails
        """
        started_at = time.monotonic()
        try:
            updated_cards = self.api_client.fetch_updated_flashcards()
            changed_cards = []

            for flashcard in updated_cards:
                try:
                    deck_id = self.anki_manager.get_or_create_deck_id(flashcard.deck)

                    # Check if card already exists in Anki
                    existing_note_id = (
                        self.anki_manager.find_note_by_guid(flashcard.ankiId)
                        if flashcard.ankiId
                        else None
                    )

                    if flashcard.ankiId is None or existing_note_id is None:
                        # Create new card
                        guid = self.anki_manager.create_new_card(flashcard, deck_id)
                        if guid:
                            flashcard.ankiId = guid
                            flashcard.updated = False
                            self.api_client.create_flashcard(flashcard)
                            changed_cards.append(flashcard)
                    else:
                        # Update existing card
                        if self.anki_manager.update_existing_card(flashcard, deck_id):
                            flashcard.updated = False
                            self.api_client.update_flashcard(flashcard)
                            changed_cards.append(flashcard)

                except Exception as e:
                    self.logger.error(f"Failed to process card {flashcard.id}: {e}")
                    # Continue with other cards even if one fails
                    continue

            result = CardResult(
                changes=OpChanges(
                    deck=True,
                    note=True,
                    card=True,
                    deck_config=True,
                    browser_table=True
                ),
                changed_cards=changed_cards
            )
            duration_ms = int((time.monotonic() - started_at) * 1000)
            self.tracking_client.report_success(duration_ms, len(changed_cards))
            return result

        except VocabularyAPIError as e:
            duration_ms = int((time.monotonic() - started_at) * 1000)
            self.tracking_client.report_failure(duration_ms, str(e))
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during synchronization: {e}")
            duration_ms = int((time.monotonic() - started_at) * 1000)
            self.tracking_client.report_failure(duration_ms, str(e))
            raise VocabularyAPIError(f"Synchronization failed: {e}")
