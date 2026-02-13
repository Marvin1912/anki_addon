"""
HTTP client for Vocabulary API communication.

This module provides a client for communicating with the Vocabulary API
server, handling all HTTP requests for flashcard synchronization.
"""

import json
import logging
from dataclasses import asdict
from typing import List

import requests
from requests import RequestException

from .config import SyncConfig
from .models import FlashCard


class VocabularyAPIError(Exception):
    """
    Exception raised for errors in the Vocabulary API communication.
    """
    pass


class VocabularyAPIClient:
    """
    Client for communicating with the Vocabulary API server.

    Handles HTTP requests for flashcard synchronization, including
    fetching updated cards, creating new cards, and updating existing cards.

    This class has no GUI dependencies and can be used in both
    GUI addons and headless environments.
    """

    def __init__(self, config: SyncConfig = None):
        """
        Initialize the API client.

        Args:
            config: SyncConfig instance. If None, uses default configuration.
        """
        self.config = config or SyncConfig()
        self.base_url = self.config.get_flashcards_endpoint()
        self.logger = logging.getLogger(__name__)

    def fetch_updated_flashcards(self) -> List[FlashCard]:
        """
        Fetch flashcards that have been updated on the server.

        Returns:
            List of updated FlashCard objects

        Raises:
            VocabularyAPIError: If the API request fails
        """
        try:
            response = requests.get(
                url=f"{self.base_url}?updated=true",
                headers=self.config.get_json_headers()
            )
            response.raise_for_status()

            flashcards = []
            for raw_card in response.json():
                flashcard = FlashCard(**raw_card)
                flashcards.append(flashcard)

            return flashcards

        except RequestException as e:
            self.logger.error(f"Failed to fetch updated flashcards: {e}")
            raise VocabularyAPIError(f"Failed to fetch updated flashcards: {e}")

    def update_flashcard(self, flashcard: FlashCard) -> bool:
        """
        Update a flashcard on the server.

        Args:
            flashcard: The flashcard to update

        Returns:
            True if update was successful

        Raises:
            VocabularyAPIError: If the API request fails
        """
        try:
            response = requests.put(
                url=self.base_url,
                data=json.dumps(asdict(flashcard)),
                headers=self.config.get_json_headers()
            )
            response.raise_for_status()

            self.logger.info(
                f"Updated card {flashcard.front} with id/guid {flashcard.id}/{flashcard.ankiId}. "
                f"Got status {response.status_code}"
            )
            return True

        except RequestException as e:
            self.logger.error(f"Failed to update flashcard {flashcard.id}: {e}")
            raise VocabularyAPIError(f"Failed to update flashcard: {e}")

    def create_flashcard(self, flashcard: FlashCard) -> bool:
        """
        Create a new flashcard on the server.

        Args:
            flashcard: The flashcard to create

        Returns:
            True if creation was successful

        Raises:
            VocabularyAPIError: If the API request fails
        """
        try:
            response = requests.put(
                url=self.base_url,
                data=json.dumps(asdict(flashcard)),
                headers=self.config.get_json_headers()
            )
            response.raise_for_status()

            self.logger.info(
                f"Added card {flashcard.front} with id/guid {flashcard.id}/{flashcard.ankiId}. "
                f"Got status {response.status_code}"
            )
            return True

        except RequestException as e:
            self.logger.error(f"Failed to create flashcard {flashcard.id}: {e}")
            raise VocabularyAPIError(f"Failed to create flashcard: {e}")
