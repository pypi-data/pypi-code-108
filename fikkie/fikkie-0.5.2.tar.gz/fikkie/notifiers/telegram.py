import logging

from .base import BaseNotifier


__all__ = ["TelegramNotifier"]


class TelegramNotifier(BaseNotifier):
    """A telegram notifier."""

    TYPE = "telegram"

    def __init__(self, token: str, chat_id: str):
        try:
            from telegram import Bot
        except ModuleNotFoundError:  # pragma: no cover - no complexity here
            logging.error("Please install the `python-telegram-bot` package.")
            exit(1)

        self._bot = Bot(token=token)
        self._chat_id = chat_id

    def notify(self, text: str) -> None:
        """Sends a message."""
        self._bot.sendMessage(chat_id=self._chat_id, text=text)
