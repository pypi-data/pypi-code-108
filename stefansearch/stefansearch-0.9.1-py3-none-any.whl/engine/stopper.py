import typing
import pathlib


class Stopper:
    """Simple class to use for Stopping tokens."""
    def __init__(self, stopwords: typing.Iterable[str]):
        self.stopwords = set(stopwords)

    def is_stopword(self, word: str) -> bool:
        return word in self.stopwords

    @staticmethod
    def from_file(filepath: pathlib.Path) -> 'Stopper':
        """
        Takes the path to a stopwords file (one stopword per line) and
        reads the words into a `Stopper` instance.
        """
        stop_set = set()
        for line in open(filepath, 'r'):
            stop_set.add(line.strip())
        return Stopper(stop_set)
