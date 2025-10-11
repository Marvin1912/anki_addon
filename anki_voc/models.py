"""
Data models for Anki Vocabulary Addon.
"""

from dataclasses import dataclass
from typing import List, Optional

from anki.collection import OpChanges


@dataclass
class FlashCard:
    """
    Represents a flashcard with front and back content.

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


@dataclass
class CardResult:
    """
    Result of card processing operations.

    Attributes:
        changes: Anki operation changes object
        changed_cards: List of cards that were changed during the operation
    """
    changes: OpChanges
    changed_cards: List[FlashCard]