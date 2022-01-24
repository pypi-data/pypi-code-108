"""Routines for reading in files."""

import abc


class Reader(abc.ABC):
    """Defines an interface all the Reader subclasses should adhere to."""

    @abc.abstractmethod
    def read_data(self, filename: str) -> object:
        pass


class TextFileReader(Reader):
    """Reader for reading data from a text file."""

    def __init__(self) -> None:
        """Initializes TextFileReader for reading."""
        self.encoding: str = "utf-8"

    def read_data(self, filename: str) -> object:
        """
        Reads in a text file.

        Parameters:
            filename.... File to read from.

        Returns:
            The opened file as is (as an file object).
        """
        return open(filename, "r", encoding=self.encoding)
