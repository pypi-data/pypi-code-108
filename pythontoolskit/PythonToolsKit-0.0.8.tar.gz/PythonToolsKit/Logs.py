#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> from Logs import *
>>> import Logs
>>> logger = get_custom_logger()
>>> logger = get_custom_logger("MyPackageName")
>>> @log_trace
... def test(): pass
...
>>> test()
>>> Logs.logger.setLevel(5)
>>> test()
[...] TRACE    (5) {...} Start test...
[...] TRACE    (5) {...} End of test.
>>> logger = ColoredLogger(logger)
>>> logger.debug("Debug message")
[...] DEBUG    (10) {...} Debug message
>>> logger.info("Info message")
[...] INFO     (20) {...} Info message
>>> logger.warning("Warning message")
[...] WARNING  (30) {...} Warning message
>>> logger.error("Error message")
[...] ERROR    (40) {...} Error message
>>> logger.critical("Critical message")
[...] CRITICAL (50) {...} Critical message
>>> from Logs import *
>>> logger = get_custom_logger("csv_logger")
>>> logger.handlers[0].setFormatter(CsvFormatter())
>>> logger.critical("test logs")
"2016-06-22 22:06:16","Wed Jun  22 22:06:16 2016","CRITICAL","50","test logs","<stdin>","1","<module>","<stdin>","<stdin>","MainThread","220616","MainProcess","220616"
>>>
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = [
    "log_trace",
    "get_custom_logger",
    "logger",
    "ColoredLogger",
    "CsvFormatter",
    "CompressLogHandler",
]

from logging import StreamHandler, Formatter, Logger, getLogger, addLevelName
from logging.handlers import RotatingFileHandler
from time import gmtime, asctime, strftime
from collections.abc import Callable
from csv import writer, QUOTE_ALL
from types import FunctionType
from functools import wraps
from os.path import exists
from gzip import compress
from io import StringIO
from sys import stdout
from os import remove


def get_custom_logger(name: str = __name__) -> Logger:

    """
    This function create a custom logger.
    """

    logger = getLogger(name)

    formatter = Formatter(
        fmt=(
            "%(asctime)s%(levelname)-9s(%(levelno)s) "
            "{%(name)s - %(filename)s:%(lineno)d} %(message)s"
        ),
        datefmt="[%Y-%m-%d %H:%M:%S] ",
    )
    stream = StreamHandler(stream=stdout)
    stream.setFormatter(formatter)

    logger.addHandler(stream)

    return logger


logger: Logger = get_custom_logger()
logger_debug: Callable = logger.debug
logger_info: Callable = logger.info
logger_warning: Callable = logger.warning
logger_error: Callable = logger.error
logger_critical: Callable = logger.critical
logger_log: Callable = logger.log

addLevelName(5, "TRACE")

logger.trace: Callable = lambda x: logger_log(5, x)
logger_trace: Callable = logger.trace


def log_trace(function: FunctionType) -> FunctionType:

    """
    This decorator trace functions (start and end).
    """

    @wraps(function)
    def wrapper(*args, **kwds):
        name = function.__name__
        logger_trace(f"Start {name}...")
        values = function(*args, **kwds)
        logger_trace(f"End of {name}.")
        return values

    return wrapper


class CsvFormatter(Formatter):

    """
    This class implements a CSV logging formatter.
    """

    def __init__(self):
        super().__init__()
        output = self.output = StringIO()
        self.getlog = output.getvalue
        self.trunc = output.truncate
        self.seek = output.seek
        writer_ = self.writer = writer(output, quoting=QUOTE_ALL)
        self.writerow = writer_.writerow

    def format(self, record):

        """
        This function formats record in CSV.
        """

        time_ = gmtime(record.created)
        date = asctime(time_)
        time_ = strftime("%Y-%m-%d %H:%M:%S", time_)
        self.writerow(
            [
                time_,
                date,
                record.levelname,
                str(record.levelno),
                record.msg,
                record.filename,
                str(record.lineno),
                record.funcName,
                record.pathname,
                record.module,
                record.threadName,
                str(record.thread),
                record.processName,
                str(record.process),
            ]
        )
        data = self.getlog()
        self.trunc(0)
        self.seek(0)
        return data.strip()


class ColoredLogger:

    """
    This class implements a colored logger.
    """

    def __init__(self, logger: Logger):
        self.logger = logger
        self._debug = logger.debug
        self._info = logger.info
        self._warning = logger.warning
        self._error = logger.error
        self._critical = logger.critical

    def debug(self, log: str) -> None:

        """
        This function logs a colored debug message.
        """

        self._debug(f"\x1b[32m{log}\x1b[0m")

    def info(self, log: str) -> None:

        """
        This function logs a colored info message.
        """

        self._info(f"\x1b[34m{log}\x1b[0m")

    def warning(self, log: str) -> None:

        """
        This function logs a colored warning message.
        """

        self._warning(f"\x1b[33m{log}\x1b[0m")

    def error(self, log: str) -> None:

        """
        This function logs a colored error message.
        """

        self._error(f"\x1b[35m{log}\x1b[0m")

    def critical(self, log: str) -> None:

        """
        This function logs a colored critical message.
        """

        self._critical(f"\x1b[31m{log}\x1b[0m")


class CompressLogHandler(RotatingFileHandler):

    """
    This class implements a handler to compress and rotate log files.
    """

    def doRollover(self):

        """
        Do a rollover, as described in __init__().
        """

        stream = self.stream

        if stream:
            stream.close()
            stream = None

        if self.backupCount > 0:
            rotation_filename = self.rotation_filename
            base_filename = filename = self.baseFilename
            i = 0
            while exists(filename):
                i += 1
                filename = rotation_filename("%s.%d" % (base_filename, i))

            self.rotate(base_filename, filename)

        if not self.delay:
            stream = self._open()

    def namer(self, name: str) -> str:

        """
        This function returns the new name of the old log files.
        """

        return f"{name}.gz"

    def rotator(self, source: str, destination: str) -> None:

        """
        This function compresses old log files.
        """

        with open(source, "rb") as source_file:
            compressed = compress(source_file, 9)

            with open(destination, "wb") as destination_file:
                destination_file.write(compressed)

        remove(source)
