import json
from dataclasses import dataclass, asdict
from typing import List, Optional

import requests
from anki.cards import CardId
from anki.collection import OpChanges, Collection, OpChangesWithCount
from anki.decks import DeckId
from anki.notes import Note
from aqt import mw
from aqt.operations import CollectionOp
from aqt.qt import *
from requests import Response


@dataclass
class FlashCard:
    deck: str
    front: str
    back: str
    updated: bool
    id: Optional[int] = None
    ankiId: Optional[str] = None
    description: Optional[str] = ''


@dataclass
class CardResult:
    changes: OpChanges
    changed_cards: List[FlashCard]


def set_note_fields(note: Note, card: FlashCard):
    note['Vorderseite'] = card.front
    note['Rückseite'] = card.back
    note['Description'] = card.description


def add_card_to_deck(col: Collection, note: Note, deck_id: DeckId):
    card_ids: list[CardId] = [c.id for c in note.cards()]
    r: OpChangesWithCount = col.set_deck(card_ids, deck_id)
    print(f"Added {r.count} card(s) to deck {col.decks.name(deck_id)}")


def create_and_add_card(col: Collection, deck_id: DeckId, card: FlashCard) -> bool:
    guid = add_card(col, deck_id, card)
    if guid is not None:
        card.ankiId = guid
        card.updated = False
        r: Response = requests.put(
            url="http://localhost:9001/vocabulary/flashcards",
            data=json.dumps(asdict(card)),
            headers={'content-type': 'application/json; charset=utf-8'}
        )
        print(f"Added card {card.front} with id/guid {card.id}/{card.ankiId}. Got status {r.status_code}")
        return True
    return False


def add_card(
        col: Collection,
        deck_id: DeckId,
        card: FlashCard,
        model_name: str = "Einfach"
):
    m = col.models.by_name(model_name)

    note: Note = col.newNote(m)

    set_note_fields(note, card)

    added_cards_count = col.addNote(note)
    if added_cards_count == 0:
        print("No card was created (possible duplicate or empty fields).")
        return None

    print(f"""
        Created card with id/guid {card.id}/{card.ankiId}
        {card}
    """)

    add_card_to_deck(col, note, deck_id)

    return note.guid


def update_card(col: Collection, deck_id: DeckId, card: FlashCard) -> bool:
    if not card.ankiId:
        return False

    note_id = col.db.scalar("SELECT id FROM notes WHERE guid = ?", card.ankiId)
    if not note_id:
        print(f"Card with guid {card.ankiId} not found")
        return False

    note: Note = col.get_note(note_id)

    set_note_fields(note, card)

    col.update_note(note)

    add_card_to_deck(col, note, deck_id)

    card.updated = False
    r: Response = requests.put(
        url="http://localhost:9001/vocabulary/flashcards",
        data=json.dumps(asdict(card)),
        headers={'content-type': 'application/json; charset=utf-8'}
    )
    print(f"Updated card {card.front} with id/guid {card.id}/{card.ankiId}. Got status {r.status_code}")

    return True


def process_cards(col: Collection) -> CardResult:
    r: Response = requests.get(url="http://localhost:9001/vocabulary/flashcards?updated=true")

    changed_cards: List[FlashCard] = []
    for raw_card in r.json():
        card = FlashCard(**raw_card)
        deck_id: DeckId = col.decks.id(card.deck)

        note_id = col.db.scalar("SELECT id FROM notes WHERE guid = ?", card.ankiId)

        if card.ankiId is None or note_id is None:
            changed = create_and_add_card(col, deck_id, card)
        else:
            changed = update_card(col, deck_id, card)

        if changed:
            changed_cards.append(card)

    return CardResult(
        changes=OpChanges(deck=True, note=True, card=True, deck_config=True, browser_table=True),
        changed_cards=changed_cards
    )


def create_operation():
    op = CollectionOp(parent=mw, op=process_cards)
    op.success(on_create_success)
    op.run_in_background()


def on_create_success(changes: CardResult):
    dlg = QDialog(mw)
    dlg.setWindowTitle("Changed Cards")
    dlg.setMinimumSize(400, 300)

    layout = QVBoxLayout(dlg)

    list_widget = QListWidget(dlg)
    list_widget.setStyleSheet("""
        QListWidget::item {
            border: 1px solid gray;
            border-radius: 4px;
            padding: 6px;
        }
        QListWidget::item:selected {
            border: 2px solid blue;
            background: #e0f0ff;
        }
    """)

    cards = changes.changed_cards
    if len(cards) != 0:
        for card in cards:
            QListWidgetItem(f"""
                Front: {card.front}
                Back: {card.back}
                Description: {card.description}
                ------------
            """, list_widget)
    else:
        QListWidgetItem(f"#### Nothing changed ####", list_widget)

    layout.addWidget(list_widget)

    dlg.setLayout(layout)
    dlg.exec()


action = QAction("Import cards from server", mw)
action.triggered.connect(create_operation)
mw.form.menuTools.addAction(action)
