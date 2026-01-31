"""
Unified configuration management for Anki sync operations.

This module provides a centralized configuration system that supports
both file-based and environment-based configuration, making it suitable
for both GUI addons and headless Docker containers.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SyncConfig:
    """
    Unified configuration for Anki sync operations.

    This configuration class supports both GUI addon and headless sync
    scenarios, with sensible defaults and environment variable overrides.
    """

    # API Configuration
    api_base_url: str = "http://backend.home-lab.com"
    flashcards_endpoint: Optional[str] = None  # Computed from api_base_url

    # Anki Configuration
    default_model_name: str = "Einfach"
    anki_field_front: str = "Vorderseite"
    anki_field_back: str = "Rückseite"
    anki_field_description: str = "Description"

    # AnkiWeb Configuration (for headless sync)
    anki_username: Optional[str] = None
    anki_password: Optional[str] = None

    # Collection Configuration (for headless sync)
    collection_path: Optional[str] = None

    # Schedule Configuration (for headless sync)
    schedule: str = "0 */6 * * *"

    # UI Configuration (for GUI addon)
    window_title_changed_cards: str = "Changed Cards"
    window_title_error: str = "Synchronization Error"
    window_minimum_size: tuple = (400, 300)
    menu_action_text: str = "Import cards from server"

    # Logging
    log_no_cards_created: str = "No card was created (possible duplicate or empty fields)."
    log_card_not_found: str = "Card with guid {guid} not found"

    # HTTP Headers
    json_headers: dict = field(default_factory=lambda: {'content-type': 'application/json; charset=utf-8'})

    def __post_init__(self):
        """Compute derived values after initialization."""
        if self.flashcards_endpoint is None:
            self.flashcards_endpoint = f"{self.api_base_url}/vocabulary/flashcards"

    @classmethod
    def from_env(cls) -> 'SyncConfig':
        """
        Create configuration from environment variables.

        This is particularly useful for Docker containers and headless sync.

        Returns:
            SyncConfig instance with values from environment variables
        """
        return cls(
            api_base_url=os.getenv("API_BASE_URL", cls.api_base_url),
            anki_username=os.getenv("ANKI_USERNAME"),
            anki_password=os.getenv("ANKI_PASSWORD"),
            collection_path=os.getenv("ANKI_COLLECTION_PATH"),
            schedule=os.getenv("SCHEDULE", cls.schedule),
        )

    def get_flashcards_endpoint(self) -> str:
        """
        Get the full flashcards endpoint URL.

        Returns:
            Full URL for the flashcards endpoint
        """
        return self.flashcards_endpoint

    def get_json_headers(self) -> dict:
        """
        Get JSON headers for API requests.

        Returns:
            Dictionary of HTTP headers
        """
        return self.json_headers


# Default configuration instance
default_config = SyncConfig()
