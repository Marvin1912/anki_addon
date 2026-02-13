"""
UI components for Anki Vocabulary Addon.

This module provides GUI components for displaying synchronization results
and error messages to users.
"""

import logging
from typing import Callable, List, Optional

from aqt.qt import *
from aqt import mw

from anki_sync_core.config import SyncConfig
from anki_sync_core.models import CardResult, FlashCard


class ChangedCardsDialog(QDialog):
    """
    Dialog to display cards that have been changed during synchronization.
    """

    def __init__(self, card_result: CardResult, config: SyncConfig = None, parent=None):
        """
        Initialize the dialog with card results.

        Args:
            card_result: Result containing changed cards
            config: SyncConfig instance. If None, uses default configuration.
            parent: Parent widget (default: None)
        """
        super().__init__(parent or mw)
        self.card_result = card_result
        self.config = config or SyncConfig()
        self.logger = logging.getLogger(__name__)

        self.setup_ui()
        self.populate_cards()

    def setup_ui(self) -> None:
        """Set up the dialog UI components."""
        self.setWindowTitle(self.config.window_title_changed_cards)
        self.setMinimumSize(*self.config.window_minimum_size)

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

    def __init__(self, error_message: str, config: SyncConfig = None, parent=None):
        """
        Initialize the error dialog.

        Args:
            error_message: Error message to display
            config: SyncConfig instance. If None, uses default configuration.
            parent: Parent widget (default: None)
        """
        super().__init__(parent or mw)
        self.error_message = error_message
        self.config = config or SyncConfig()
        self.logger = logging.getLogger(__name__)

        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the dialog UI components."""
        self.setWindowTitle(self.config.window_title_error)
        self.setMinimumSize(*self.config.window_minimum_size)

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


def show_changed_cards_dialog(card_result: CardResult, config: SyncConfig = None) -> None:
    """
    Show the changed cards dialog.

    Args:
        card_result: Result containing changed cards to display
        config: SyncConfig instance. If None, uses default configuration.
    """
    dialog = ChangedCardsDialog(card_result, config, mw)
    dialog.exec()


class DeckImportSelectionDialog(QDialog):
    """
    Dialog for selecting which decks to import from a file.
    """

    def __init__(self, forward_deck_name: str, reverse_deck_name: str,
                 forward_count: int, reverse_count: int,
                 parent=None):
        super().__init__(parent or mw)
        self.forward_deck_name = forward_deck_name
        self.reverse_deck_name = reverse_deck_name
        self.forward_count = forward_count
        self.reverse_count = reverse_count

        self.forward_checkbox: Optional[QCheckBox] = None
        self.reverse_checkbox: Optional[QCheckBox] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        self.setWindowTitle("Import Decks")
        self.setMinimumSize(420, 220)

        layout = QVBoxLayout(self)

        info_label = QLabel("Select the decks to import from the file:")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.forward_checkbox = QCheckBox(
            f"{self.forward_deck_name} ({self.forward_count} cards)"
        )
        self.forward_checkbox.setChecked(True)
        layout.addWidget(self.forward_checkbox)

        self.reverse_checkbox = QCheckBox(
            f"{self.reverse_deck_name} ({self.reverse_count} cards)"
        )
        self.reverse_checkbox.setChecked(True)
        layout.addWidget(self.reverse_checkbox)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        import_button = QPushButton("Import")
        import_button.clicked.connect(self.accept)
        button_layout.addWidget(import_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_selection(self) -> tuple[bool, bool]:
        return (
            bool(self.forward_checkbox and self.forward_checkbox.isChecked()),
            bool(self.reverse_checkbox and self.reverse_checkbox.isChecked()),
        )


def show_deck_import_selection_dialog(
    forward_deck_name: str,
    reverse_deck_name: str,
    forward_count: int,
    reverse_count: int,
) -> Optional[tuple[bool, bool]]:
    dialog = DeckImportSelectionDialog(
        forward_deck_name,
        reverse_deck_name,
        forward_count,
        reverse_count,
        mw,
    )
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_selection()
    return None


def show_error_dialog(error_message: str, config: SyncConfig = None) -> None:
    """
    Show an error dialog to the user.

    Args:
        error_message: Error message to display
        config: SyncConfig instance. If None, uses default configuration.
    """
    dialog = ErrorDialog(error_message, config, mw)
    dialog.exec()
