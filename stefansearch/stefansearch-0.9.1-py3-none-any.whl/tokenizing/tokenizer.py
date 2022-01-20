import typing
import abc


class Tokenizer(abc.ABC):
    """Base class used to implement a Tokenizer that splits text into tokens."""
    @abc.abstractmethod
    def tokenize_string(
            self,
            string: str,
    ) -> typing.Generator[str, None, None]:
        """Return a generator that yields tokens from `string`."""
        pass
