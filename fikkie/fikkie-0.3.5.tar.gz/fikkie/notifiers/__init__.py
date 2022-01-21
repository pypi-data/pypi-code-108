from .email import EmailNotifier
from .telegram import TelegramNotifier


class Notifier:
    """
    A notifier factory which chooses the notifier based on the "type" param.
    """

    NOTIFIERS = [EmailNotifier, TelegramNotifier]

    # NOTE: The following properties should never be used, but are added to help mypy
    # understand the properties of a Notifier class (e.g. TelegramNotifier). The same
    # counts for the `notify()` method below.
    TYPE = None
    ENCODING = None

    def __new__(cls, type: str, *args, **kwargs):  # pragma: no cover - no complexity
        for notifier in cls.NOTIFIERS:
            if type == notifier.TYPE:  # type: ignore
                return notifier(*args, **kwargs)
        raise ValueError(f"Unknown notifier type: {type}")

    def notify(self, text: str) -> None:  # pragma: no cover - placeholder
        """Sends a message."""
        raise NotImplementedError()
