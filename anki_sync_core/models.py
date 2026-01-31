"""
Data models for Anki sync operations.

This module defines the core data structures used throughout the
synchronization process, with no GUI dependencies.
"""

from dataclasses import dataclass
from typing import List, Optional

from anki.collection import OpChanges


@dataclass
class FlashCard:
    """
    Represents a flashcard with front and back content.

    This model is used for both API communication and Anki storage,
    providing a unified representation of flashcard data.

    Attributes:
        deck: The name of the deck this card belongs to
        front: Front side content (German field name preserved for Anki compatibility)
        back: Back side content
        updated: Whether this card has been updated and needs synchronization
        id: Optional local database ID
        ankiId: Optional Anki GUID for synchronization
        description: Optional additional description for the card
    """
    deck: str
    front: str
    back: str
    updated: bool
    id: Optional[int] = None
    ankiId: Optional[str] = None
    description: Optional[str] = ''

    def __str__(self) -> str:
        """Return a string representation of the flashcard."""
        return f"FlashCard(deck={self.deck}, front={self.front}, back={self.back})"


@dataclass
class CardResult:
    """
    Result of card processing operations.

    This model encapsulates the results of synchronization operations,
    including both Anki operation changes and the list of changed cards.

    Attributes:
        changes: Anki operation changes object
        changed_cards: List of cards that were changed during the operation
    """
    changes: OpChanges
    changed_cards: List[FlashCard]

    def __len__(self) -> int:
        """Return the number of changed cards."""
        return len(self.changed_cards)

    def is_empty(self) -> bool:
        """Check if any cards were changed."""
        return len(self.changed_cards) == 0
