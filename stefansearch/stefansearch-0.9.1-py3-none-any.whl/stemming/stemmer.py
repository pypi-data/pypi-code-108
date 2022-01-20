import abc


class Stemmer(abc.ABC):
    """Base class used to implement a stemmer that performs token stemming."""
    @abc.abstractmethod
    def get_stem(self, token: str) -> str:
        """Returns the stem of the given token."""
        pass
