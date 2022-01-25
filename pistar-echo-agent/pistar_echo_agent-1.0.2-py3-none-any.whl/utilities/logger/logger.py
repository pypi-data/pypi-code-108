"""
description: this module provides the class Logger.
"""

import logging
import logging.handlers
from pathlib import Path

import colorlog

from pistar_echo_agent.utilities.constants import LOGGING_LEVEL
from pistar_echo_agent.utilities.constants import ENCODE


class Logger(logging.Logger):
    """
    description: this class is the logger of pistar echo agent.
    """

    __output_path = None
    __level = None
    __format = None
    __colors = None

    def __init__(self, name, logger_format, level=LOGGING_LEVEL.DEBUG,
                 output_path=None):
        super().__init__(name)

        self.__format = logger_format
        self.__level = level
        self.__colors = {
            'DEBUG': 'fg_cyan',
            'INFO': 'fg_green',
            'WARNING': 'fg_yellow',
            'ERROR': 'fg_purple',
            'CRITICAL': 'fg_red'
        }

        self.__create_stream_handler()
        self.__output_path = output_path

    def __create_stream_handler(self):
        formatter = PathTruncatingFormatterColor(
            '%(log_color)s' + self.__format + '%(reset)s',
            log_colors=self.__colors
        )

        handler = logging.StreamHandler()
        handler.setLevel(self.__level)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def create_file_handler(self):
        directory = Path(self.__output_path).parent
        directory.mkdir(exist_ok=True, parents=True)
        formatter = PathTruncatingFormatter(self.__format)
        handler = logging.FileHandler(
            self.__output_path,
            encoding=ENCODE.UTF8,
            delay=True
        )
        handler.setLevel(self.__level)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def close(self):
        """
        description: this function is used to
                     close the file handler of the logger.
        """

        for handler in self.handlers:
            handler.close()
            self.removeHandler(handler)

    @property
    def output_path(self):
        """
        description: return the private member __output_path.
        """

        return self.__output_path


class PathTruncatingFormatter(logging.Formatter):
    """
    description: this class is the truncating formatter of file handler.
    """

    def format(self, record):
        application = "pistar_echo_agent"
        paths = record.pathname.split(application)
        record.pathname = application + paths[-1]
        return super().format(record)


class PathTruncatingFormatterColor(colorlog.ColoredFormatter):
    """
    description: this class is the truncating formatter with color of stream handler.
    """

    def format(self, record):
        application = "pistar_echo_agent"
        paths = record.pathname.split(application)
        record.pathname = application + paths[-1]
        return super().format(record)
