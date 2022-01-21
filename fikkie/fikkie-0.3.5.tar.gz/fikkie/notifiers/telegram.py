import logging


__all__ = ["TelegramNotifier"]


class TelegramNotifier:
    """A telegram notifier."""

    TYPE = "telegram"
    ENCODING = "UTF-8"

    def __init__(self, token: str, chat_id: str):
        # Only import the telegram dependency when it's needed
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
