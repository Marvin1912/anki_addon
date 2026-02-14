"""
File-based deck import utilities.

Parses newline-delimited JSON flashcards and imports them into Anki decks.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from anki.collection import Collection, OpChanges

from .anki_manager import AnkiCardManager
from .config import SyncConfig
from .models import CardResult, FlashCard


@dataclass
class ImportSummary:
    forward_count: int
    reverse_count: int


class FileImportError(Exception):
    """Raised when file import fails."""


class FileDeckImporter:
    """
    Import flashcards from a newline-delimited JSON file into two decks.

    One deck is front->back, the other is back->front.
    """

    def __init__(self, collection: Collection, config: SyncConfig = None):
        self.collection = collection
        self.config = config or SyncConfig()
        self.anki_manager = AnkiCardManager(collection, self.config)
        self.logger = logging.getLogger(__name__)

    def _parse_line(self, line: str, line_number: int) -> Optional[FlashCard]:
        if not line.strip():
            return None
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise FileImportError(f"Invalid JSON at line {line_number}: {exc}") from exc

        required = ("front", "back")
        for key in required:
            if key not in payload:
                raise FileImportError(
                    f"Missing required field '{key}' at line {line_number}"
                )

        return FlashCard(
            deck=payload.get("deck", ""),
            front=str(payload.get("front", "")),
            back=str(payload.get("back", "")),
            description=str(payload.get("description", "")),
            updated=bool(payload.get("updated", False)),
            id=payload.get("id"),
            ankiId=payload.get("ankiId"),
        )

    def parse_file(self, file_path: str) -> List[FlashCard]:
        path = Path(file_path)
        if not path.exists():
            raise FileImportError(f"Import file not found: {file_path}")

        cards: List[FlashCard] = []
        with path.open("r", encoding="utf-8") as handle:
            for index, line in enumerate(handle, start=1):
                card = self._parse_line(line, index)
                if card:
                    cards.append(card)
        return cards

    def get_summary(self, cards: Iterable[FlashCard]) -> ImportSummary:
        count = sum(1 for _ in cards)
        return ImportSummary(forward_count=count, reverse_count=count)

    def import_cards(
        self,
        cards: Iterable[FlashCard],
        import_forward: bool,
        import_reverse: bool,
    ) -> CardResult:
        forward_deck_id = self.anki_manager.get_or_create_deck_id(
            self.config.import_deck_forward_name
        )
        reverse_deck_id = self.anki_manager.get_or_create_deck_id(
            self.config.import_deck_reverse_name
        )

        changed_cards: List[FlashCard] = []

        for card in cards:
            if import_forward:
                forward_card = FlashCard(
                    deck=self.config.import_deck_forward_name,
                    front=card.front,
                    back=card.back,
                    description=card.description,
                    updated=False,
                    id=card.id,
                    ankiId=card.ankiId,
                )
                guid = self.anki_manager.create_new_card(forward_card, forward_deck_id)
                if guid:
                    changed_cards.append(forward_card)

            if import_reverse:
                reverse_card = FlashCard(
                    deck=self.config.import_deck_reverse_name,
                    front=card.back,
                    back=card.front,
                    description=card.description,
                    updated=False,
                    id=card.id,
                    ankiId=None,
                )
                guid = self.anki_manager.create_new_card(reverse_card, reverse_deck_id)
                if guid:
                    changed_cards.append(reverse_card)

        return CardResult(
            changes=OpChanges(
                deck=True,
                note=True,
                card=True,
                deck_config=True,
                browser_table=True,
            ),
            changed_cards=changed_cards,
        )
