from enum import Enum

try:
    from typing import Literal
except ImportError:  # pragma: no cover - no need to test Python's stdlib
    # NOTE: The typing library of Python 3.7 does not contain Literal
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
