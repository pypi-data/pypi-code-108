# -*- coding: utf-8 -*-
"""
    pip_services3_components.log.ILogger
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for logging components.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import Any, Optional

from pip_services3_components.log import LogLevel


class ILogger(ABC):
    """
    Interface for logger components that capture execution log messages.
    """

    def get_level(self) -> LogLevel:
        """
        Gets the maximum log level. Messages with higher log level are filtered out.

        :return: the maximum log level.
        """
        raise NotImplementedError('Method from interface definition')

    def set_level(self, level: LogLevel):
        """
        Set the maximum log level.

        :param level: a new maximum log level.
        """
        raise NotImplementedError('Method from interface definition')

    def log(self, level: LogLevel, correlation_id: Optional[str], error: Optional[Exception], message: Optional[str], *args: Any,
            **kwargs: Any):
        """
        Logs a message at specified log level.

        :param level: a log level.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param error: an error object associated with this message.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        raise NotImplementedError('Method from interface definition')

    def fatal(self, correlation_id: Optional[str], error: Exception, message: str, *args: Any, **kwargs: Any):
        """
        Logs fatal (unrecoverable) message that caused the process to crash.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param error: an error object associated with this message.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        raise NotImplementedError('Method from interface definition')

    def error(self, correlation_id: Optional[str], error: Exception, message: str, *args: Any, **kwargs: Any):
        """
        Logs recoverable application error.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param error: an error object associated with this message.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        raise NotImplementedError('Method from interface definition')

    def warn(self, correlation_id: Optional[str], message: Exception, *args: Any, **kwargs: Any):
        """
        Logs a warning that may or may not have a negative impact.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        raise NotImplementedError('Method from interface definition')

    def info(self, correlation_id: Optional[str], message: str, *args: Any, **kwargs: Any):
        """
        Logs an important information message

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        raise NotImplementedError('Method from interface definition')

    def debug(self, correlation_id: Optional[str], message: str, *args: Any, **kwargs: Any):
        """
        Logs a high-level debug information for troubleshooting.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        raise NotImplementedError('Method from interface definition')

    def trace(self, correlation_id: Optional[str], message: str, *args: Any, **kwargs: Any):
        """
        Logs a low-level debug information for troubleshooting.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        raise NotImplementedError('Method from interface definition')
