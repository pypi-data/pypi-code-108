"""Functions for internal 'helpers' subpackage."""

from __future__ import annotations
import warnings

from typing_extensions import Literal

from .config_module import config
from .str_formating import format_str
from .my_logging import my_logger
from .colors import colors_module

printed_info = set()
original_formatwarning = warnings.formatwarning
level_str_to_int = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}

user__filters = []

logging_functions = {
    "DEBUG": my_logger.logger.debug,
    "INFO": my_logger.logger.info,
    "WARNING": my_logger.logger.warning,
    "ERROR": my_logger.logger.error,
    "CRITICAL": my_logger.logger.critical,
}


class CustomWarning(UserWarning):
    """Custom warning class so it is editable."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def filter_out(
    message: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    once_overwrite: bool = False,
) -> bool:
    """Based on configuration pass or deny log based on filter and level.

    Args:
        message (str): Used message. Necessary for 'once' filter.
        level (Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]): Used level.

    Returns:
        bool: True if message should not be passed (has lover level or already been and filter is 'once').
    """
    # All logging can be turned off
    if config.filter == "ignore":
        return True

    # Check if sufficient level

    if level_str_to_int[level] < level_str_to_int[config.level]:
        return True

    message = config.re_pattern.sub("", message)[:150]

    # Filters
    if config.filter == "once" or once_overwrite:
        if message in printed_info:
            return True
        else:
            printed_info.add(message)

    for i in config.blacklist:
        if i in message:
            return True

    return False


def log_warn(
    message: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    showwarning_details: bool = True,
    stack_level: int = 3,
) -> None:
    """If output is configured, it will log message into defined path. If output == "console" is configured,
    it will log or warn.

    Args:
        message (str): Any string content of warning.
        level (str): 'INFO' or something else, generated automatically from __init__ module.
        showwarning_details (bool, optional): Whether to override warnings details display.
            After warning, default one will be again used. Defaults to True.
        stack_level (int, optional): How many calls to log from error. Defaults to 3.
    """

    if config.filter == "error":
        raise RuntimeError(message)

    if config.console_log_or_warn == "log":
        try:
            # From version 3.8
            logging_functions[level](message, stacklevel=stack_level)
        except TypeError:
            logging_functions[level](message)

    else:
        warnings.formatwarning = formatwarning_detailed if showwarning_details else formatwarning_stripped

        CustomWarning.__name__ = level
        CustomWarning.level = level

        warnings.warn(message, stacklevel=stack_level, category=CustomWarning)

        warnings.formatwarning = original_formatwarning


def call_log_function(message, caption, level):
    """As this would be called in all the log functions, here is shorthand."""
    if not filter_out((caption + message)[:150], level):
        log_warn(format_str(message, caption=caption, use_object_conversion=False, level=level), level=level)


# message, category, filename, lineno
def formatwarning_detailed(_message, category, _filename, _lineno, *_args, **_kwargs):
    """Function that can override warnings printed info."""
    return (
        f"\n\n{colors_module.colorize(category.__name__, level=category.level)}"
        "from {filename}:{lineno} {message}\n"
    )


def formatwarning_stripped(message, *_args, **_kwargs):
    """Function that can override warnings printed info."""
    return f"{message}\n"
