"""
Anki Vocabulary Addon - Synchronize flashcards with external API.

This addon provides functionality to import and synchronize flashcards
from a remote vocabulary API server with Anki.
"""

import logging
from aqt import mw
from aqt.operations import CollectionOp
from aqt.qt import QAction

from .addon_config import MENU_ACTION_TEXT
from .models import CardResult
from .synchronizer import FlashcardSynchronizer
from .ui_components import show_changed_cards_dialog
from .vocabulary_api import VocabularyAPIError

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
        synchronizer = FlashcardSynchronizer(collection)
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
        show_changed_cards_dialog(card_result)
    except Exception as e:
        logger.error(f"Failed to show results dialog: {e}")


def on_synchronization_failure(error) -> None:
    """
    Handle synchronization failures.

    Args:
        error: Exception that occurred during synchronization
    """
    logger.error(f"Synchronization operation failed: {error}")
    # TODO: Show user-friendly error message dialog


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
        action = QAction(MENU_ACTION_TEXT, mw)
        action.triggered.connect(create_synchronization_operation)
        mw.form.menuTools.addAction(action)
        logger.info("Anki Vocabulary Addon successfully initialized")

    except Exception as e:
        logger.error(f"Failed to initialize addon: {e}")


# Initialize the addon when the module is loaded
setup_addon()
