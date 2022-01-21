"""
Implementation of custom exceptions for pragmail.
"""
from functools import wraps
from typing import Any, Callable


class IMAP4Error(Exception):
    """Generic pragmail exception."""


class CommandError(AttributeError, ValueError):
    """Exception raised when command usage is invalid."""


def catch_exception(func: Callable[..., Any]):
    """Function wrapper for catching exceptions and applying pragmail's custom
    exceptions.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        try:
            return func(*args, **kwargs)
        except (AttributeError, ValueError) as common_err:
            raise CommandError(common_err) from common_err
        except Exception as generic_err:
            raise IMAP4Error(generic_err) from generic_err

    return wrapper


if __name__ == "__main__":
    pass
