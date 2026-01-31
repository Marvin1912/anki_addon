"""
Anki Vocabulary Addon - Synchronize flashcards with external API.

This addon provides functionality to import and synchronize flashcards
from a remote vocabulary API server with Anki. It uses the shared
anki_sync_core library for all business logic.
"""

import logging
from aqt import mw
from aqt.operations import CollectionOp
from aqt.qt import QAction

from anki_sync_core import FlashcardSynchronizer, VocabularyAPIError, default_config
from anki_sync_core.models import CardResult
from .ui_components import show_changed_cards_dialog, show_error_dialog

# Configure logging for the addon
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_synchronization(collection) -> CardResult:
    """
    Process flashcard synchronization with the external API.

    Args:
        collection: Anki collection instance

    Returns:
        CardResult with information about synchronized cards

    Raises:
        VocabularyAPIError: If API communication fails
    """
    try:
        synchronizer = FlashcardSynchronizer(collection, default_config)
        result = synchronizer.synchronize_updated_cards()
        logger.info(f"Synchronization completed. {len(result.changed_cards)} cards processed.")
        return result

    except VocabularyAPIError as e:
        logger.error(f"Synchronization failed: {e}")
        raise


def on_synchronization_success(card_result: CardResult) -> None:
    """
    Handle successful synchronization by showing results dialog.

    Args:
        card_result: Result containing information about synchronized cards
    """
    try:
        show_changed_cards_dialog(card_result, default_config)
    except Exception as e:
        logger.error(f"Failed to show results dialog: {e}")


def on_synchronization_failure(error) -> None:
    """
    Handle synchronization failures.

    Args:
        error: Exception that occurred during synchronization
    """
    logger.error(f"Synchronization operation failed: {error}")

    # Show user-friendly error message dialog
    error_message = str(error)
    if not error_message:
        error_message = "An unknown error occurred during synchronization."

    try:
        show_error_dialog(error_message, default_config)
    except Exception as dialog_error:
        logger.error(f"Failed to show error dialog: {dialog_error}")


def create_synchronization_operation() -> None:
    """Create and start the synchronization operation."""
    try:
        operation = CollectionOp(parent=mw, op=process_synchronization)
        operation.success(on_synchronization_success)
        operation.failure(on_synchronization_failure)
        operation.run_in_background()
        logger.info("Started flashcard synchronization operation")

    except Exception as e:
        logger.error(f"Failed to create synchronization operation: {e}")


def setup_addon() -> None:
    """Set up the addon by adding menu action."""
    try:
        action = QAction(default_config.menu_action_text, mw)
        action.triggered.connect(create_synchronization_operation)
        mw.form.menuTools.addAction(action)
        logger.info("Anki Vocabulary Addon successfully initialized")

    except Exception as e:
        logger.error(f"Failed to initialize addon: {e}")


# Initialize the addon when the module is loaded
setup_addon()
