"""Functions for my_warnings subpackage."""

from __future__ import annotations
import warnings
from dataclasses import dataclass

from typing_extensions import Literal

from ..internal_module import filter_out


@dataclass
class Backups:
    show_warning_backup = warnings.showwarning
    warning_filters_backup = warnings.filters.copy()  # type: ignore


backups = Backups()


def filter_once(level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"):
    """If filter (once) in warnings from 3rd party libraries don't work, this implements own filter.

    Note:
        Default warnings function is overwritten, do not forget to reset original filters.

    Args:
        level (Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], optional): Used level in filter.
            Defaults to "WARNING".

    Returns:
        FilterOnce: Object containing reset function.

    """
    backups.show_warning_backup = warnings.showwarning

    def custom_warn(message, category, filename, lineno, file=None, line=None):
        custom_message = f"In {filename} - {str(category)}: {str(message)}"
        if not filter_out(custom_message, level, once_overwrite=True):
            backups.show_warning_backup(message, category, filename, lineno, file=file, line=line)

    warnings.showwarning = custom_warn


def reset_filter_once() -> None:
    """Reset custom warnings filter."""
    warnings.showwarning = backups.show_warning_backup


def filter_always(messages: None | list = None, messages_and_categories: None | list = None) -> Filter:
    """Also other libraries you use can raise warnings. This function can filter warnings from
    such a libraries.

    Note:
        Default warnings function is overwritten, do not forget to reset original filters.

    Args:
        messages (None | list, optional): List of warnings (any part of inner string) that will be ignored
            even if debug is set. Example ["AR coefficients are not stationary.", "Mean of empty slice",].
            Defaults to None.
        messages_and_categories (None | list, optional): List of tuples (string of module that raise it and
            warning type) that will be ignored even if debug is set. Example `[('statsmodels.tsa.arima_model',
            FutureWarning)]`. Defaults to None.

    Returns:
        Filter: Object containing reset function.
    """
    backups.warning_filters_backup = warnings.filters.copy()  # type: ignore

    if messages:
        for i in messages:
            warnings.filterwarnings("ignore", message=fr"[\s\S]*{i}*")

    if messages_and_categories:
        for i in messages_and_categories:
            warnings.filterwarnings("ignore", module=i[0], category=i[1])


def reset_filter_always() -> None:
    """Reset custom warnings filter."""
    warnings.filters = backups.warning_filters_backup
