import sys
from traceback import format_exception
from typing import Any, List


def get_exception_text() -> str:
    """
    When called within an exception, this function returns a text
    representation of the error matching what is found in
    `traceback.print_exception`, but is returned as a string value rather than
    printing.
    """
    return "".join(format_exception(*sys.exc_info()))


def append_exception_text(error: Exception, message: str) -> None:
    """
    Cause `message` to be appended to an error's exception text.
    """
    last_attribute_name: str
    repr_last_attribute_value: str
    for last_attribute_name in ("strerror", "msg"):
        last_attribute_value = getattr(error, last_attribute_name, "")
        if last_attribute_value:
            setattr(
                error, last_attribute_name, f"{last_attribute_value}{message}"
            )
            break
    if not last_attribute_value:
        index: int
        arg: Any
        reversed_args: List[Any] = list(reversed(error.args)) or [""]
        for index, value in enumerate(reversed_args):
            if isinstance(value, str):
                reversed_args[index] = f"{value}{message}"
                break
        error.args = tuple(reversed(reversed_args))
