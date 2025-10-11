"""
HTTP client for Vocabulary API communication.
"""

import json
import logging
from dataclasses import asdict
from typing import List, Optional

import requests
from requests import Response, RequestException

from .addon_config import FLASHCARDS_ENDPOINT, JSON_HEADERS
from .models import FlashCard


class VocabularyAPIClient:
    """
    Client for communicating with the Vocabulary API server.

    Handles HTTP requests for flashcard synchronization.
    """

    def __init__(self, base_url: str = FLASHCARDS_ENDPOINT):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the vocabulary API
        """
        self.base_url = base_url
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
                headers=JSON_HEADERS
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
            True if update was successful, False otherwise

        Raises:
            VocabularyAPIError: If the API request fails
        """
        try:
            response = requests.put(
                url=self.base_url,
                data=json.dumps(asdict(flashcard)),
                headers=JSON_HEADERS
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
            True if creation was successful, False otherwise

        Raises:
            VocabularyAPIError: If the API request fails
        """
        try:
            response = requests.put(
                url=self.base_url,
                data=json.dumps(asdict(flashcard)),
                headers=JSON_HEADERS
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


class VocabularyAPIError(Exception):
    """
    Exception raised for errors in the Vocabulary API communication.
    """
    pass