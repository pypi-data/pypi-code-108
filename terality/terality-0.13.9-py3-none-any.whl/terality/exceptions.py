from dataclasses import dataclass


@dataclass
class TeralityError(Exception):
    """Base class for errors in the client"""

    message: str

    def __str__(self):
        return self.message


class TeralityClientError(TeralityError):
    """A client error occurred. Retrying won't help."""
