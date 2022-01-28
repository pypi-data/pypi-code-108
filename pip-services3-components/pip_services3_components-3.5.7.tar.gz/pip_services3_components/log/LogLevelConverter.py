# -*- coding: utf-8 -*-
"""
    pip_services3_components.log.LogLevelConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Log level converter implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any

from .LogLevel import LogLevel


class LogLevelConverter(object):
    """
    Helper class to convert log level values.
    """

    @staticmethod
    def to_log_level(value: Any, default_value: LogLevel = LogLevel.Info) -> LogLevel:
        """
        Converts numbers and strings to standard log level values.

        :param value: a value to be converted
        :param default_value: a default value if conversion is not possible

        :return: converted log level
        """
        if value is None:
            return LogLevel.Info

        value = str(value).upper()
        if ("0" == value) or ("NOTHING" == value) or ("NONE" == value):
            return LogLevel.Nothing
        elif ("1" == value) or ("FATAL" == value):
            return LogLevel.Fatal
        elif ("2" == value) or ("ERROR" == value):
            return LogLevel.Error
        elif ("3" == value) or ("WARN" == value) or ("WARNING" == value):
            return LogLevel.Warn
        elif ("4" == value) or ("INFO" == value):
            return LogLevel.Info
        elif ("5" == value) or ("DEBUG" == value):
            return LogLevel.Debug
        elif ("6" == value) or ("TRACE" == value):
            return LogLevel.Trace
        else:
            return default_value

    @staticmethod
    def to_string(level: LogLevel) -> str:
        """
        Converts log level to a string.

        :param level: a log level to convert

        :return: log level name string.
        """
        if level == LogLevel.Fatal:
            return "FATAL"
        if level == LogLevel.Error:
            return "ERROR"
        if level == LogLevel.Warn:
            return "WARN"
        if level == LogLevel.Info:
            return "INFO"
        if level == LogLevel.Debug:
            return "DEBUG"
        if level == LogLevel.Trace:
            return "TRACE"
        return "UNDEF"

    @staticmethod
    def to_integer(level: LogLevel) -> int:
        """
        Converts log level to a number.

        :param level: a log level to convert.

        :return: log level number value.
        """
        if level == LogLevel.Fatal:
            return 1
        if level == LogLevel.Error:
            return 2
        if level == LogLevel.Warn:
            return 3
        if level == LogLevel.Info:
            return 4
        if level == LogLevel.Debug:
            return 5
        if level == LogLevel.Trace:
            return 6
        return 0
