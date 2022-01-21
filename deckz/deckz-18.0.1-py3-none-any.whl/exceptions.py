from typing import Optional


class DeckzException(Exception):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message)
