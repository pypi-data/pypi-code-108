"""Module with functions for 'config' subpackage."""

from __future__ import annotations
from typing import Union, Any
from pathlib import Path
import re
import logging

from typeguard import typechecked
from typing_extensions import Literal

from .my_logging import my_logger
from . import str_formating
from .colors.colors_module import colors_config


@typechecked
class Config:
    """Usually used created instace from this module called config as usually no need of
    another instances... All variables has own docstrings."""

    def __init__(self):
        self.__output = "console"
        self.__level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
        self.__around: Literal[True, False, "auto"] = "auto"
        self.__colorize: Literal[True, False, "auto"] = "auto"
        self.__filter: Literal["ignore", "once", "always", "error"] = "once"
        self.__formatter_file_str = "{asctime} {levelname} {filename}:{lineno}{message}"
        self.__formatter_console_str = "\n{levelname} from {pathname}:{lineno} {funcName}{message}"
        self.__blacklist = []
        self.__to_list = None
        self.__stream = None
        self.__console_log_or_warn: Literal["log", "warn"] = "log"
        self.re_pattern = re.compile(r"[\W_]+")

        my_logger.init_formatter(self.formatter_file_str, self.formatter_console_str, self.output, self.level)

    @property
    def filter(self) -> Literal["ignore", "once", "always", "error"]:
        """
        Define what to do with logs, that repeats.

        Only first 100 symbols of message will be used if using once.

        Do not affect warnings library. Use `my_warnings` module if you need that.
        Options: ["ignore", "once", "always", "error"]

        Defaults to: 'once'

        "error" means that application stop on log as on error.
        """
        return self.__filter

    @filter.setter
    def filter(self, new: Literal["ignore", "once", "always", "error"]) -> None:
        self.__filter = new

    @property
    def around(self) -> Literal[True, False, "auto"]:
        """
        True: separate logs with ===== and line breaks for better visibility.

        False: keep message short

        "auto": False if output == "file/path", True if output == "console"

        Defaults to: "auto"
        """
        return self.__around

    @around.setter
    def around(self, new: Literal[True, False, "auto"]) -> None:
        if new == "auto":
            str_formating.USED_AROUND = True if self.output == "console" else False
        else:
            str_formating.USED_AROUND = new
        self.__around = new

    @property
    def formatter_file_str(self) -> str:
        """You can edit used formatter if you want. Just go to source of logging.Formatter to see
        all possible options. This is only main string of formatter class (style="{" is used).
        Message itself is formatted in format_str function. This is for formatter if logging to console.

        Defaults to: "{asctime} {levelname} {filename}:{lineno}{message}"

        """
        return self.__formatter_file_str

    @formatter_file_str.setter
    def formatter_file_str(self, new: str) -> None:
        self.__formatter_file_str = new
        my_logger.formatter_file_str = new
        my_logger.get_handler()

    @property
    def formatter_console_str(self) -> str:
        """You can edit used formatter if you want. Just go to source of logging.Formatter to see
        all possible options. This is only main string of formatter class (style="{" is used).
        Message itself is formatted in format_str function. This is for formatter if logging to console.

        Defaults to: "\n{levelname}from {pathname}:{lineno} {funcName}{message}"
        """
        return self.__formatter_console_str

    @formatter_console_str.setter
    def formatter_console_str(self, new: str):
        self.__formatter_console_str = new
        my_logger.formatter_console_str = new
        my_logger.get_handler()

    @property
    def colorize(self) -> Literal[True, False, "auto"]:
        """Whether colorize results.

        Options: [True, False, 'auto']

        Defaults to: 'auto'

        'auto' means color if to console, not color if to file.
        """
        return self.__colorize

    @colorize.setter
    def colorize(self, new: Literal[True, False, "auto"]):
        if new == "auto":
            if self.output == "console":
                colors_config.USE_COLORS = True
            else:
                colors_config.USE_COLORS = False
        else:
            colors_config.USE_COLORS = new
        self.__colorize = new

    @property
    def output(self) -> Union[str, Path, None]:
        """Whether log to file or to console. If None, nor console, nor file will be
        used (stream logs to a variable is still possible).

        Options: ["console", pathlib.Path, r"path/to/file", None]

        Defaults to: "console"
        """
        return self.__output

    @output.setter
    def output(self, new: Union[str, Path, None]) -> None:
        self.__output = new
        self.around = self.around  # If auto, change it
        self.colorize = self.colorize  # If auto, change it
        my_logger.output = new
        my_logger.get_handler()

    @property
    def stream(self) -> Any:
        """Whether save all logs to stream (that stream can be variable).

        Example: io.StringIO()

        Defaults to: None
        """
        return self.__stream

    @stream.setter
    def stream(self, new: Any):
        self.__stream = new
        my_logger.stream = new
        my_logger.get_handler()

    @property
    def blacklist(self) -> list[str]:
        """Log messages can be filtered out. Only part of message can be used.
        Numeric letters are removed in message comparison, to be able to filter
        out same errors from different places. Only last 100 messages is kept in memory...

        Example: ["Matrix inversion failed"]

        Defaults to: None"""
        return self.__blacklist

    @blacklist.setter
    def blacklist(self, new: list[str]):
        self.__blacklist = [self.re_pattern.sub("", i) for i in new]

    @property
    def to_list(self) -> Union[None, list[str]]:
        """You can store all logs in list and then emit when you want.

        Defaults to: None"""
        return self.__to_list

    @to_list.setter
    def to_list(self, new: Union[None, list]):
        self.__to_list = new
        my_logger.to_list = new
        my_logger.get_handler()

    @property
    def level(self) -> Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        """Logs can be filtered out based on log severity.

        Options: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        Defaults to: "INFO"
        """
        return self.__level

    @level.setter
    def level(self, new: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]):
        if self.output:
            my_logger.logger.setLevel(getattr(logging, new))
        self.__level = new

    @property
    def console_log_or_warn(self) -> Literal["log", "warn"]:
        """Used mostly internally. It can use only warnings when logging. Make sense only when
        logging to console."""
        return self.__console_log_or_warn

    @console_log_or_warn.setter
    def console_log_or_warn(self, new: Literal["log", "warn"]):
        self.__console_log_or_warn = new


config = Config()
"""You can configure mylogging from here. All variables has own docstrings."""
