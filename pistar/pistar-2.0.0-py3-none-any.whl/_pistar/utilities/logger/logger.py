"""
description: this module provides the class Logger.
"""

import logging
import logging.handlers
import sys

import colorlog

from _pistar.utilities.constants import LOGGING_LEVEL
from _pistar.utilities.constants import ENCODE


class BaseLogger(logging.Logger):
    """
    the base class of logger.
    """
    def __init__(self, name):
        super().__init__(name)
        self._format = None
        self._level = None
        self._output_path = None

    def _create_file_handler(self):
        formatter = logging.Formatter(self._format)

        handler = logging.FileHandler(self._output_path, encoding=ENCODE.UTF8, delay=True)
        handler.setLevel(self._level)
        handler.setFormatter(formatter)
        self.addHandler(handler)


class Logger(BaseLogger):
    """
    description: this class is the user logger of pistar.
    """

    def __init__(self, name, logger_format, output_path, level=LOGGING_LEVEL.INFO, no_color=False):
        super().__init__(name)

        self._format = logger_format
        self._level = level
        self._colors = {
            "DEBUG": "fg_cyan",
            "INFO": "fg_green",
            "WARNING": "fg_yellow",
            "ERROR": "fg_red",
            "CRITICAL": "fg_purple",
        }
        self._no_color = no_color
        self.__create_stream_handler()
        self._output_path = output_path
        self._create_file_handler()

    def __create_stream_handler(self):
        if self._no_color:
            formatter = logging.Formatter(self._format)
        else:
            formatter = colorlog.ColoredFormatter("%(log_color)s" + self._format + "%(reset)s", log_colors=self._colors)

        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(self._level)
        handler.setFormatter(formatter)
        self.addHandler(handler)


class ExecuteLogger(BaseLogger):
    """
    description: this class is the frame logger of pistar.
    """

    def __init__(self, name, logger_format, output_path, level=LOGGING_LEVEL.INFO):
        super().__init__(name)
        self._level = level
        self._format = logger_format
        self._output_path = output_path
        self._create_file_handler()
