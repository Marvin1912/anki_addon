"""
Anki Vocabulary Addon - Import flashcards from a file.

This addon provides functionality to import flashcards from a newline-delimited
JSON file into Anki. It uses its bundled core library for all business logic.
"""

import logging
import threading

from aqt import mw
from aqt.operations import CollectionOp
from aqt.qt import QAction

from .anki_sync_core import (
    FileDeckImporter,
    FileImportError,
    default_config,
)
from .anki_sync_core.models import CardResult
from .ui_components import (
    show_changed_cards_dialog,
    show_deck_import_selection_dialog,
    show_error_dialog,
)

# Configure logging for the addon
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from typing import Optional, Tuple


def process_file_import(
    collection,
    selection: Optional[Tuple[bool, bool, str, str]],
) -> CardResult:
    """
    Process flashcard import from a newline-delimited JSON file.

    Args:
        collection: Anki collection instance

    Returns:
        CardResult with information about synchronized cards

    Raises:
        FileImportError: If file import fails
    """
    try:
        if not default_config.import_file_path:
            raise FileImportError("Import file path is not configured.")

        if selection is None:
            logger.info("Import canceled by user (no selection provided).")
            return CardResult(changes=None, changed_cards=[])

        importer = FileDeckImporter(collection, default_config)
        cards = importer.parse_file(default_config.import_file_path)
        summary = importer.get_summary(cards)

        import_forward, import_reverse, forward_name, reverse_name = selection
        default_config.import_deck_forward_name = forward_name
        default_config.import_deck_reverse_name = reverse_name
        if not import_forward and not import_reverse:
            logger.info("No decks selected for import.")
            return CardResult(changes=None, changed_cards=[])

        result = importer.import_cards(cards, import_forward, import_reverse)
        logger.info(f"File import completed. {len(result.changed_cards)} cards created.")
        return result

    except FileImportError as e:
        logger.error(f"File import failed: {e}")
        raise


def on_import_success(card_result: CardResult) -> None:
    """
    Handle successful synchronization by showing results dialog.

    Args:
        card_result: Result containing information about synchronized cards
    """
    try:
        logger.info(
            "Scheduling results dialog on main thread (current=%s)",
            threading.current_thread().name,
        )
        mw.taskman.run_on_main(
            lambda: show_changed_cards_dialog(card_result, default_config)
        )
    except Exception as e:
        logger.error(f"Failed to show results dialog: {e}")


def on_import_failure(error) -> None:
    """
    Handle synchronization failures.

    Args:
        error: Exception that occurred during synchronization
    """
    logger.error(f"Import operation failed: {error}")

    # Show user-friendly error message dialog
    error_message = str(error)
    if not error_message:
        error_message = "An unknown error occurred during import."

    try:
        logger.info(
            "Scheduling error dialog on main thread (current=%s)",
            threading.current_thread().name,
        )
        mw.taskman.run_on_main(
            lambda: show_error_dialog(error_message, default_config)
        )
    except Exception as dialog_error:
        logger.error(f"Failed to show error dialog: {dialog_error}")


def create_import_operation() -> None:
    """Create and start the file import operation."""
    try:
        importer = FileDeckImporter(mw.col, default_config)
        cards = importer.parse_file(default_config.import_file_path)
        summary = importer.get_summary(cards)

        selection = show_deck_import_selection_dialog(
            default_config.import_deck_forward_name,
            default_config.import_deck_reverse_name,
            summary.forward_count,
            summary.reverse_count,
        )

        if selection is None:
            logger.info("Import canceled by user.")
            return

        operation = CollectionOp(
            parent=mw,
            op=lambda collection: process_file_import(collection, selection),
        )
        operation.success(on_import_success)
        operation.failure(on_import_failure)
        operation.run_in_background()
        logger.info("Started file import operation")

    except Exception as e:
        logger.error(f"Failed to create import operation: {e}")


def setup_addon() -> None:
    """Set up the addon by adding menu action."""
    try:
        file_action = QAction(default_config.menu_action_text, mw)
        file_action.triggered.connect(create_import_operation)
        mw.form.menuTools.addAction(file_action)
        logger.info("Anki Vocabulary Addon successfully initialized")

    except Exception as e:
        logger.error(f"Failed to initialize addon: {e}")


# Initialize the addon when the module is loaded
setup_addon()
