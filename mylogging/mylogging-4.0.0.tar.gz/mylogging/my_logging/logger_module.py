"""Module with functionality for 'logger' subpackage."""

from __future__ import annotations
from typing import Union, Any
import logging
from pathlib import Path

from ..colors import colorize


class MyLogger:
    """Logger class use python logger and define it in specific way. It contains some filters
    and formatters."""

    def __init__(self) -> None:
        self.formatter_file_str: str
        self.formatter_console_str: str
        self.output: Union[str, Path, None]
        self.level: str
        self.formatter_file_str: str
        self.stream: Any
        self.to_list: Union[None, list[str]]

        self.datefmt = "%Y-%m-%d %H:%M"
        self.logger = logging.getLogger("application")
        self.logger.addFilter(self.ContextFilter())

    def init_formatter(
        self,
        formatter_file_str,
        formatter_console_str,
        output,
        level,
        stream=None,
        to_list=None,
    ):
        """Init some values from config when initializing mylogging module or when some config
        value is changed."""

        self.formatter_file_str = formatter_file_str
        self.formatter_console_str = formatter_console_str
        self.output = output
        self.stream = stream
        self.level = level
        self.to_list = to_list
        self.get_handler()
        self.logger.setLevel(getattr(logging, level))

    def get_handler(self) -> None:
        """If formatter_file_str, formatter_console_str or output change, it need new handler.
        First update new value in logger object, then call this function."""
        while self.logger.handlers:
            self.logger.removeHandler(self.logger.handlers[0])

        if self.stream is not None:
            handler = logging.StreamHandler(stream=self.stream)
            handler.setFormatter(self.get_formatter(self.formatter_console_str))
            # handler.setLevel(getattr(logging, self.level))
            self.logger.addHandler(handler)

        if self.output == "console":
            handler = logging.StreamHandler()
            handler.setFormatter(self.get_formatter(self.formatter_console_str))
            # handler.setLevel(getattr(logging, self.level))
            self.logger.addHandler(handler)

        elif self.output:
            handler = logging.FileHandler(self.output)
            handler.setFormatter(self.get_formatter(self.formatter_file_str))
            # handler.setLevel(getattr(logging, self.level))
            self.logger.addHandler(handler)

        if isinstance(self.to_list, list):
            handler = self.SaveHandler(self.to_list)
            self.logger.addHandler(handler)

    def get_formatter(self, format_str: str) -> logging.Formatter:
        """Create logging formatter with expected params."""
        return logging.Formatter(
            format_str,
            datefmt=self.datefmt,
            style="{",
        )

    class ContextFilter(logging.Filter):
        """Class with logging filter that format output message."""

        def filter(self, record):
            """Logging filter that format output message."""
            record.funcName = "" if record.funcName == "<module>" else f"in function {record.funcName}"
            record.levelname = colorize(record.levelname, record.levelname)
            return True

    class SaveHandler(logging.Handler):
        """Enable to save logs to python list so it can be logged later elsewhere."""

        def __init__(self, to_list) -> None:
            self.to_list = to_list
            super().__init__()

        def emit(self, record) -> None:
            self.to_list.append(record)


my_logger = MyLogger()
"""Logger object is python logger defined in a specific way. It contains some filters and formatters."""
