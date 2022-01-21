class TTSError(Exception):
    """Base class for all exceptions related to this library"""


class InvalidEngine(TTSError):
    """Raised when the config detects an invalid engine name."""


class InvalidEffect(TTSError):
    """Raised when an invalid tfm effect is detected in the config."""
