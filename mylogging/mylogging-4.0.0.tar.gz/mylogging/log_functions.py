"""Internal module for functions that will be imported in __init__.py for shorter syntax.
This module is mainly for writing docstrings."""

from __future__ import annotations

from typing_extensions import Literal

from .internal_module import call_log_function, filter_out, log_warn
from .my_traceback import format_traceback
from .str_formating import format_str

print_function = print


def print(  # pylint: disable=redefined-builtin
    message: str, caption: str = "", level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
) -> None:
    """Log message without details (file, line etc.). Only difference with normal print is
    filter and level in config.

    Args:
        message (str): Message to be logged.
        caption (str, optional): Heading of warning. Defaults to 'User message'.
        level (Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]): Print can have also levels same
            as logs to be able to filter. Defaults to "DEBUG"
    """

    if not filter_out((caption + message)[:150], level):
        print_function(format_str(message, caption=caption, use_object_conversion=False, level=level))


def debug(message: str, caption: str = "") -> None:
    """Log debug info. Only difference with info is filtering level in config.

    Args:
        message (str): Message to be logged.
        caption (str, optional): Heading of warning. Defaults to 'User message'.
    """

    call_log_function(message, caption, "DEBUG")


def info(message: str, caption: str = "") -> None:
    """Log info.

    Args:
        message (str): Message to be logged.
        caption (str, optional): Heading of warning. Defaults to 'User message'.
    """

    call_log_function(message, caption, "INFO")


def warn(message: str, caption: str = "") -> None:
    """Raise warning - just message, not traceback. Can be colorized. Display of warning is based
    on warning settings. You can configure how to cope with warnings with function set_warnings with debug
    parameter. Instead of traceback_warning this is not from caught error. It usually bring some information
    good to know.

    Args:
        message (str): Any string content of warning.
        caption (str, optional): Heading of warning. Defaults to 'User message'.
    """

    call_log_function(message, caption, "WARNING")


def error(message: str, caption: str = "") -> None:
    """Same as warn, but can be filtered different way with level. This is only for logging message.
    If you want to log error code, you can use function traceback.

    Args:
        message (str): Any string content of error.
        caption (str, optional): Heading of error. Defaults to 'User message'.
    """
    call_log_function(message, caption, "ERROR")


def critical(message: str, caption: str = "") -> None:
    """Same as warning, but usually describe error that stopped the application.

    Args:
        message (str): Any string content of error.
        caption (str, optional): Heading of error. Defaults to 'User message'.
    """
    call_log_function(message, caption, "CRITICAL")


def traceback(
    message: str = "",
    caption: str = "error_type",
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "ERROR",
    stack_level: int = 3,
    remove_frame_by_line_str: list = None,
) -> None:
    """Log message with current traceback as content. It means, that error was caught, but still
    something crashed.

    Args:
        message (str): Any string content of traceback.
        caption (str, optional): Caption of warning. If 'error_type', than Error type (e.g. ZeroDivisionError)
        is used. Defaults to 'error_type'.
        level (Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], optional): Defaults to "DEBUG".
        stack_level (int, optional): How many calls to log from error. Defaults to 3.
        remove_frame_by_line_str(None | list, optional): If there is some level in stack that should be
        omitted, add line here. Defaults to None.
    """
    traceback_str = format_traceback(message, caption, level, remove_frame_by_line_str)

    if filter_out(traceback_str, level):
        return

    log_warn(traceback_str, level=level, showwarning_details=False, stack_level=stack_level)
