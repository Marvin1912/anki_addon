"""
UI components for Anki Vocabulary Addon.
"""

import logging
from typing import List

from aqt.qt import *
from aqt import mw

from .addon_config import (
    WINDOW_TITLE_CHANGED_CARDS,
    WINDOW_MINIMUM_SIZE
)
from .models import CardResult, FlashCard


class ChangedCardsDialog(QDialog):
    """
    Dialog to display cards that have been changed during synchronization.
    """

    def __init__(self, card_result: CardResult, parent=None):
        """
        Initialize the dialog with card results.

        Args:
            card_result: Result containing changed cards
            parent: Parent widget (default: None)
        """
        super().__init__(parent or mw)
        self.card_result = card_result
        self.logger = logging.getLogger(__name__)

        self.setup_ui()
        self.populate_cards()

    def setup_ui(self) -> None:
        """Set up the dialog UI components."""
        self.setWindowTitle(WINDOW_TITLE_CHANGED_CARDS)
        self.setMinimumSize(*WINDOW_MINIMUM_SIZE)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet("""
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

        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def populate_cards(self) -> None:
        """Populate the list widget with changed cards."""
        cards = self.card_result.changed_cards

        if not cards:
            item_text = "#### Nothing changed ####"
            QListWidgetItem(item_text, self.list_widget)
            self.logger.info("No cards were changed during synchronization")
        else:
            for card in cards:
                item_text = f"""
                    Front: {card.front}
                    Back: {card.back}
                    Description: {card.description}
                    ------------
                """
                QListWidgetItem(item_text, self.list_widget)
                self.logger.info(f"Displaying changed card: {card.front}")


def show_changed_cards_dialog(card_result: CardResult) -> None:
    """
    Show the changed cards dialog.

    Args:
        card_result: Result containing changed cards to display
    """
    dialog = ChangedCardsDialog(card_result, mw)
    dialog.exec()