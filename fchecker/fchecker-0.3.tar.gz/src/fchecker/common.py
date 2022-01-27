class InputFailure(Exception):
    """
    Exception raised for an input exception message.

    Args:
        exc_message:\\
        \t\\- The incorrect input reason.
    """
    __module__ = 'builtins'

    exc_message: str

    def __init__(self, exc_message: str) -> None:
        self.exc_message = exc_message


class InvalidKeyError(Exception):
    """
    Exception raised for an invalid dictionary key.

    Built in KeyErrors do not format cleanly.

    Attributes:
        exc_message:\\
        \t\\- The invalid key reason.
    """
    __module__ = 'builtins'

    exc_message: str

    def __ini__(self, exc_message: str) -> None:
        self.exc_message = exc_message
