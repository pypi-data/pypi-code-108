import logging

from .base import BaseNotifier


__all__ = ["SlackNotifier"]


class SlackNotifier(BaseNotifier):
    """A Slack notifier."""

    TYPE = "slack"

    def __init__(self, token: str, channel_id: str):
        try:
            from slack_sdk import WebClient
        except ModuleNotFoundError:  # pragma: no cover - no complexity here
            logging.error("Please install the `slack_sdk` package.")
            exit(1)

        self._client = WebClient(token=token)
        self._channel_id = channel_id

    def notify(self, text: str) -> None:
        """Sends a message."""
        self._client.chat_postMessage(channel=self._channel_id, text=text)
