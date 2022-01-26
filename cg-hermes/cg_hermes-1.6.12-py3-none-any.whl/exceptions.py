from typing import List


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingFileError(Error):
    """Exception when mandatory file is missing."""

    def __init__(self, files: List[str], message: str):
        self.files = files
        self.message = message

    def __str__(self):
        return self.message
