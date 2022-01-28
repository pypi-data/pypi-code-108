"""Functions for my_traceback subpackage."""

from __future__ import annotations
import traceback as traceback_module
import sys

from typing_extensions import Literal

from ..colors.colors_module import colors_config, colorize_traceback
from ..str_formating import format_str


def get_traceback_with_removed_frames_by_line_string(lines: list) -> str:
    """In traceback call stack, it is possible to remove particular level defined by some line content.

    Args:
        lines (list): Line in call stack that we want to hide.

    Returns:
        str: String traceback ready to be printed.

    Example:
        >>> def buggy():
        ...     return 1 / 0
        ...
        >>> try:
        ...     buggy()
        ... except ZeroDivisionError:
        ...     traceback = get_traceback_with_removed_frames_by_line_string([])
        ...     traceback_cleaned = get_traceback_with_removed_frames_by_line_string(["buggy()"])
        >>> "buggy()" in traceback
        True
        >>> "buggy()" not in traceback_cleaned
        True

    """
    exc = traceback_module.TracebackException(*sys.exc_info())  # type: ignore
    for i in exc.stack[:]:
        if i.line in lines:
            exc.stack.remove(i)

    return "".join(exc.format())


def format_traceback(
    message: str = "",
    caption: str = "error_type",
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "ERROR",
    remove_frame_by_line_str: list = None,
) -> str:
    """Raise warning with current traceback as content. It means, that error was caught, but still
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
    if remove_frame_by_line_str:
        separated_traceback = get_traceback_with_removed_frames_by_line_string(remove_frame_by_line_str)

    else:
        separated_traceback = traceback_module.format_exc()

    if caption == "error_type":
        try:
            caption = sys.exc_info()[1].__class__.__name__
        except AttributeError:
            caption = "Error"

    if colors_config.USE_COLORS:
        separated_traceback = colorize_traceback(separated_traceback)

    separated_traceback = separated_traceback.rstrip()

    separated_traceback = format_str(
        message=message,
        caption=caption,
        use_object_conversion=False,
        uncolored_message=f"\n\n{separated_traceback}" if message else f"{separated_traceback}",
        level=level,
    )

    return separated_traceback
