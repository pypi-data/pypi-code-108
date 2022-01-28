class BaseAxewException(Exception):
    """The base Axew exception."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = self.__doc__

    def __str__(self):
        return self.message


class EntryNotFound(BaseAxewException):
    """Failed to find the given entry."""


class InvalidParams(BaseAxewException):
    """An entry requires at-least code."""


class ValidationError(BaseAxewException):
    """The given arguments were too long."""

    def __init__(self, var, size):
        super().__init__()
        self.message += f" {var} needs to be shorter then {size}."


class BadRequest(BaseAxewException):
    """Something went wrong."""

    def __init__(self, message):
        super().__init__()
        self.message = message
