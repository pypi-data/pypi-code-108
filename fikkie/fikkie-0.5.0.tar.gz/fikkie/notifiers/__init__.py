from .base import BaseNotifier, Encoding
from .discord import DiscordNotifier
from .email import EmailNotifier
from .slack import SlackNotifier
from .telegram import TelegramNotifier


class Notifier(BaseNotifier):
    """
    A notifier factory which chooses the notifier based on the "type" param.
    """

    NOTIFIERS = [DiscordNotifier, EmailNotifier, SlackNotifier, TelegramNotifier]

    def __new__(cls, type: str, *args, **kwargs):  # pragma: no cover - no complexity
        for notifier in cls.NOTIFIERS:
            if type == notifier.TYPE:  # type: ignore
                return notifier(*args, **kwargs)
        raise ValueError(f"Unknown notifier type: {type}")
