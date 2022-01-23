from enum import Enum

try:
    # Python 3.8+
    from typing import Literal
except ImportError:  # pragma: no cover - no need to test Python's stdlib
    # Python 3.7
    from typing_extensions import Literal  # type: ignore


__all__ = ["BaseNotifier", "Encoding"]


class Encoding(Enum):
    ASCII = 1
    UTF8 = 2


class BaseNotifier:  # pragma: no cover - base-class for typing purposes
    """A base-class for notifiers to allow typing."""

    TYPE: str = "UNKNOWN"
    ENCODING: Encoding = Encoding.UTF8

    def notify(self, text: str) -> None:
        """Sends a message."""
        raise NotImplementedError()
