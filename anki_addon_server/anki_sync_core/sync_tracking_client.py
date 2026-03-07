"""
Client for reporting sync run results to the backend.

This module provides a client that reports anki sync run outcomes
to the adapter backend, which persists them in the backup_run table.
"""

import logging
from typing import Optional

import requests
from requests import RequestException

from .config import SyncConfig


class SyncTrackingClient:
    """
    Reports sync run results to the backend for persistence.

    Errors are logged but not raised to avoid disrupting the sync flow.
    """

    def __init__(self, config: SyncConfig = None):
        self.config = config or SyncConfig()
        self.endpoint = self.config.get_sync_runs_endpoint()
        self.logger = logging.getLogger(__name__)

    def report_success(self, duration_ms: int, cards_changed: int) -> None:
        """Report a successful sync run."""
        self._report("SUCCESS", duration_ms=duration_ms, cards_changed=cards_changed)

    def report_failure(self, duration_ms: int, error_message: str) -> None:
        """Report a failed sync run."""
        self._report("FAILED", duration_ms=duration_ms, error_message=error_message)

    def _report(
        self,
        status: str,
        duration_ms: int = 0,
        cards_changed: int = 0,
        error_message: Optional[str] = None,
    ) -> None:
        try:
            payload = {
                "status": status,
                "durationMs": duration_ms,
                "cardsChanged": cards_changed,
                "errorMessage": error_message,
            }
            response = requests.post(
                url=self.endpoint,
                json=payload,
                headers=self.config.get_json_headers(),
            )
            response.raise_for_status()
            self.logger.info(
                f"Reported sync run: status={status}, durationMs={duration_ms}, "
                f"cardsChanged={cards_changed}"
            )
        except RequestException as e:
            self.logger.warning(f"Failed to report sync run to backend: {e}")
