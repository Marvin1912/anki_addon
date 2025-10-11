"""
UI components for Anki Vocabulary Addon.
"""

import logging
from typing import List

from aqt.qt import *
from aqt import mw

from .addon_config import (
    WINDOW_TITLE_CHANGED_CARDS,
    WINDOW_TITLE_ERROR,
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


class ErrorDialog(QDialog):
    """
    Dialog to display error messages to the user.
    """

    def __init__(self, error_message: str, parent=None):
        """
        Initialize the error dialog.

        Args:
            error_message: Error message to display
            parent: Parent widget (default: None)
        """
        super().__init__(parent or mw)
        self.error_message = error_message
        self.logger = logging.getLogger(__name__)

        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the dialog UI components."""
        self.setWindowTitle(WINDOW_TITLE_ERROR)
        self.setMinimumSize(*WINDOW_MINIMUM_SIZE)

        layout = QVBoxLayout(self)

        # Error icon and message
        message_layout = QHBoxLayout()

        # Error icon (using a simple text representation)
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 24px;")
        message_layout.addWidget(icon_label)

        # Error message
        message_label = QLabel(self.error_message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        message_layout.addWidget(message_label)

        layout.addLayout(message_layout)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)


def show_changed_cards_dialog(card_result: CardResult) -> None:
    """
    Show the changed cards dialog.

    Args:
        card_result: Result containing changed cards to display
    """
    dialog = ChangedCardsDialog(card_result, mw)
    dialog.exec()


def show_error_dialog(error_message: str) -> None:
    """
    Show an error dialog to the user.

    Args:
        error_message: Error message to display
    """
    dialog = ErrorDialog(error_message, mw)
    dialog.exec()