"""Module with functions for misc subpackage."""
from __future__ import annotations
from typing import Callable, Any, Union
import warnings
from pathlib import Path
import logging
from dataclasses import dataclass
import traceback as traceback_py_module
import sys

from ..my_logging import my_logger
from ..internal_module import filter_out
from ..config_module import config


@dataclass
class RedirectedLogsAndWarnings:
    """Helper so resetting the original behavior is simple."""

    logs: list[logging.LogRecord]
    warnings: list[dict[str, Any]]
    showwarning_backup: Callable
    output_backup: Union[str, Path, None]
    stream_backup: Any

    def close_redirect(self):
        """Stop saving logs and warnings to lists. Restoring original logs and warnings if necessary."""
        warnings.showwarning = self.showwarning_backup
        if self.output_backup:
            config.output = self.output_backup
        if self.output_backup:
            config.stream = self.stream_backup
        config.to_list = None


def redirect_logs_and_warnings(
    used_logs: list[logging.LogRecord], used_warnings: list, keep_logs_and_warnings: bool = True
) -> RedirectedLogsAndWarnings:
    """For example if using many processes with multiprocessing, it may be beneficial to log from one place.
    It's possible to log to variables (logs as well as warnings), pass it to the main process and then log it
    with workings filter etc.

    To log stored logs and warnings, use

    Args:
        used_logs (list): List where logs will be stored
        used_warnings (list): List where warnings will be stored
        keep_logs_and_warnings (bool, optional): If False, warnings and logs will be silenced.
            Default to True.

    Returns:
        RedirectedLogsAndWarnings: Object, where you can reset redirect. Logs and warnings you already have
        from inserted parameters.
    """
    showwarning_backup = warnings.showwarning

    def custom_warn(message, category, filename, lineno, file=None, line=None):
        used_warnings.append(
            {
                "message": message,
                "category": category,
                "filename": filename,
                "lineno": lineno,
                "file": file,
                "line": line,
            }
        )
        if keep_logs_and_warnings:
            showwarning_backup(message, category, filename, lineno, file=None, line=None)

    warnings.showwarning = custom_warn

    if not keep_logs_and_warnings:
        output_backup = config.output
        stream_backup = config.stream

        config.output = None
        config.stream = None

    else:
        output_backup = None
        stream_backup = None

    config.to_list = used_logs

    return RedirectedLogsAndWarnings(
        logs=used_logs,
        warnings=used_warnings,
        showwarning_backup=showwarning_backup,
        output_backup=output_backup,
        stream_backup=stream_backup,
    )


def log_and_warn_from_lists(logs_list: None | list = None, warnings_list: None | list = None) -> None:
    """When logs and warnings was redirected to python lists. This can log it from the lists to file
    or console. Can be useful for example if using multiprocessing.

    Args:
        logs_list (None | list, optional): [description]. Defaults to None.
        warnings_list (None | list, optional): [description]. Defaults to None.

    Raises:
        RuntimeError: [description]
    """
    if logs_list:
        for record in logs_list:
            for handler in my_logger.logger.handlers:
                if isinstance(handler, my_logger.SaveHandler):
                    raise RuntimeError("\n\nYou have to close redirect before log from list.\n\n")
                if not filter_out(record.msg, "WARNING"):
                    handler.emit(record)
    if warnings_list:
        for i in warnings_list:
            warnings.showwarning(**i)
