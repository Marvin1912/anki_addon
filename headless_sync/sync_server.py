#!/usr/bin/python3
"""Lightweight HTTP server to trigger Anki sync on demand."""

import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from sync_script import run_sync_once


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SyncRequestHandler(BaseHTTPRequestHandler):
    _CORS_ALLOWED_METHODS = "POST, OPTIONS"
    _CORS_ALLOWED_HEADERS = "Content-Type"
    _CORS_ALLOWED_ORIGIN = "*"

    def do_OPTIONS(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/sync":
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {"status": "error", "message": "Not found"}
            )
            return

        logger.info("Manual sync trigger received")
        success, error_message = run_sync_once()

        if success:
            logger.info("Manual sync completed successfully")
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return

        self._send_json(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            {"status": "error", "message": error_message or "Unknown error"}
        )

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        logger.info("HTTP %s - %s", self.address_string(), format % args)

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", self._CORS_ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", self._CORS_ALLOWED_METHODS)
        self.send_header("Access-Control-Allow-Headers", self._CORS_ALLOWED_HEADERS)

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8000), SyncRequestHandler)
    logger.info("Manual sync server listening on 0.0.0.0:8000")
    logger.info("Manual sync server starting")
    server.serve_forever()


if __name__ == "__main__":
    main()
