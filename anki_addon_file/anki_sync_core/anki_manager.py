"""
Anki collection operations for flashcard management.

This module provides a manager for Anki collection operations,
handling creation, updating, and deck assignment of flashcards.
"""

import logging
from typing import Optional

from anki.cards import CardId
from anki.collection import Collection, OpChangesWithCount
from anki.decks import DeckId
from anki.notes import Note

from .config import SyncConfig
from .models import FlashCard


class AnkiCardManager:
    """
    Manages Anki collection operations for flashcards.

    Handles creation, updating, and deck assignment of flashcards.
    This class has no GUI dependencies and can be used in both
    GUI addons and headless environments.
    """

    def __init__(self, collection: Collection, config: SyncConfig = None):
        """
        Initialize the card manager with an Anki collection.

        Args:
            collection: Anki collection instance
            config: SyncConfig instance. If None, uses default configuration.
        """
        self.collection = collection
        self.config = config or SyncConfig()
        self.logger = logging.getLogger(__name__)

    def set_note_fields(self, note: Note, flashcard: FlashCard) -> None:
        """
        Set the fields of an Anki note from a flashcard.

        Args:
            note: Anki note to set fields on
            flashcard: FlashCard containing field data
        """
        note[self.config.anki_field_front] = flashcard.front
        note[self.config.anki_field_back] = flashcard.back
        note[self.config.anki_field_description] = flashcard.description

    def add_card_to_deck(self, note: Note, deck_id: DeckId) -> None:
        """
        Add a note's cards to a specific deck.

        Args:
            note: Anki note containing cards
            deck_id: Target deck ID
        """
        card_ids: list[CardId] = [card.id for card in note.cards()]
        result: OpChangesWithCount = self.collection.set_deck(card_ids, deck_id)

        deck_name = self.collection.decks.name(deck_id)
        self.logger.info(f"Added {result.count} card(s) to deck {deck_name}")

    def create_new_card(self, flashcard: FlashCard, deck_id: DeckId,
                       model_name: str = None) -> Optional[str]:
        """
        Create a new Anki card from a flashcard.

        Args:
            flashcard: FlashCard data to create from
            deck_id: Target deck ID
            model_name: Anki model name to use (default from config)

        Returns:
            Note GUID if successful, None otherwise
        """
        model_name = model_name or self.config.default_model_name
        model = self.collection.models.by_name(model_name)
        if model is None:
            self.logger.error(f"Model '{model_name}' not found")
            return None

        note: Note = self.collection.newNote(model)
        self.set_note_fields(note, flashcard)

        added_cards_count = self.collection.addNote(note)
        if added_cards_count == 0:
            self.logger.warning(self.config.log_no_cards_created)
            return None

        self.logger.info(
            f"Created card with id/guid {flashcard.id}/{flashcard.ankiId}\n{flashcard}"
        )

        self.add_card_to_deck(note, deck_id)
        return note.guid

    def update_existing_card(self, flashcard: FlashCard, deck_id: DeckId) -> bool:
        """
        Update an existing Anki card.

        Args:
            flashcard: FlashCard with updated data
            deck_id: Target deck ID

        Returns:
            True if update was successful, False otherwise
        """
        if not flashcard.ankiId:
            self.logger.warning("Cannot update card without Anki GUID")
            return False

        note_id = self.collection.db.scalar(
            "SELECT id FROM notes WHERE guid = ?",
            flashcard.ankiId
        )

        if not note_id:
            self.logger.warning(
                self.config.log_card_not_found.format(guid=flashcard.ankiId)
            )
            return False

        note: Note = self.collection.get_note(note_id)
        self.set_note_fields(note, flashcard)
        self.collection.update_note(note)
        self.add_card_to_deck(note, deck_id)

        return True

    def find_note_by_guid(self, guid: str) -> Optional[int]:
        """
        Find a note ID by its GUID.

        Args:
            guid: Anki note GUID

        Returns:
            Note ID if found, None otherwise
        """
        return self.collection.db.scalar("SELECT id FROM notes WHERE guid = ?", guid)

    def get_or_create_deck_id(self, deck_name: str) -> DeckId:
        """
        Get deck ID by name, creating the deck if it doesn't exist.

        Args:
            deck_name: Name of the deck

        Returns:
            Deck ID
        """
        try:
            return self.collection.decks.id(deck_name)
        except Exception:
            # If deck doesn't exist, create it
            deck_id = self.collection.decks.new(deck_name)
            self.logger.info(f"Created new deck '{deck_name}' with ID {deck_id}")
            return deck_id
