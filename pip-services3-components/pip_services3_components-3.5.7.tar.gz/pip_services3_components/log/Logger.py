# -*- coding: utf-8 -*-
"""
    pip_services3_components.log.Logger
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Abstract logger implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.config.IReconfigurable import IReconfigurable
from pip_services3_commons.refer import IReferenceable, Descriptor, IReferences

from .ILogger import ILogger
from .LogLevel import LogLevel
from .LogLevelConverter import LogLevelConverter


class Logger(ILogger, IReconfigurable, IReferenceable, ABC):
    """
    Abstract logger that captures and formats log messages.
    Child classes take the captured messages and write them to their specific destinations.

    ### Configuration parameters ###
    
    Parameters to pass to the :func:`configure` method for component configuration:
    
        - level:             maximum log level to capture
        - source:            source (context) name

    ### References ###
        - `*:context-info:*:*:1.0`     (optional) :class:`ContextInfo <pip_services3_components.info.ContextInfo.ContextInfo>` to detect the context id and specify counters source
    """

    def __init__(self):
        self._level = LogLevel.Info
        self._source: str = None

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._level = LogLevelConverter.to_log_level(config.get_as_object("level"))
        self._source = config.get_as_string_with_default("source", self._source)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        context_info = references.get_one_optional(Descriptor("pip-services", "context-info", "*", "*", "1.0"))
        if context_info is not None and self._source is None:
            self._source = context_info.name

    def get_level(self) -> LogLevel:
        """
        Gets the maximum log level. Messages with higher log level are filtered out.

        :return: the maximum log level.
        """
        return self._level

    def set_level(self, level: LogLevel):
        """
        Set the maximum log level.

        :param level: a new maximum log level.
        """
        self._level = level

    def get_source(self) -> str:
        """
        Gets the source (context) name.

        :return: the source (context) name.
        """
        return self._source

    def set_source(self, value: str):
        """
        Sets the source (context) name.

        :param value: a new source (context) name.
        """
        self._source = value

    @abstractmethod
    def _write(self, level: LogLevel, correlation_id: Optional[str], error: Optional[Exception],
               message: Optional[str]):
        """
        Writes a log message to the logger destination.

        :param level: a log level.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param error: an error object associated with this message.

        :param message: a human-readable message to log.
        """
        raise NotImplementedError('Method from abstract implementation')

    def _format_and_write(self, level: LogLevel, correlation_id: Optional[str], error: Exception, message: str,
                          *args: Any, **kwargs: Any):
        """
        Formats the log message and writes it to the logger destination.

        :param level: a log level.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param error: an error object associated with this message.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        if not (message is None) and len(message) > 0 and (len(args) or len(kwargs)) > 0:
            # filter None args
            args = list(filter(lambda arg: arg is not None, args))
            kwargs = list(filter(lambda kwarg: kwarg is not None, kwargs))

            message = message % (*args, *kwargs)
        self._write(level, correlation_id, error, message)

    def log(self, level: LogLevel, correlation_id: Optional[str], error: Optional[Exception], message: Optional[str],
            *args: Any,
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
        self._format_and_write(level, correlation_id, error, message, *args, **kwargs)

    def fatal(self, correlation_id: Optional[str], error: Exception, message: str, *args: Any, **kwargs: Any):
        """
        Logs fatal (unrecoverable) message that caused the process to crash.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param error: an error object associated with this message.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        self._format_and_write(LogLevel.Fatal, correlation_id, error, message, *args, **kwargs)

    def error(self, correlation_id: Optional[str], error: Exception, message: str, *args: Any, **kwargs: Any):
        """
        Logs recoverable application error.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param error: an error object associated with this message.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        self._format_and_write(LogLevel.Error, correlation_id, error, message, *args, **kwargs)

    def warn(self, correlation_id: Optional[str], message: str, *args: Any, **kwargs: Any):
        """
        Logs a warning that may or may not have a negative impact.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        self._format_and_write(LogLevel.Warn, correlation_id, None, message, *args, **kwargs)

    def info(self, correlation_id: Optional[str], message: str, *args: Any, **kwargs: Any):
        """
        Logs an important information message

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        self._format_and_write(LogLevel.Info, correlation_id, None, message, *args, **kwargs)

    def debug(self, correlation_id: Optional[str], message: str, *args: Any, **kwargs: Any):
        """
        Logs a high-level debug information for troubleshooting.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        self._format_and_write(LogLevel.Debug, correlation_id, None, message, *args, **kwargs)

    def trace(self, correlation_id: Optional[str], message: str, *args: Any, **kwargs: Any):
        """
        Logs a low-level debug information for troubleshooting.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param message: a human-readable message to log.

        :param args: arguments to parameterize the message.

        :param kwargs: arguments to parameterize the message.
        """
        self._format_and_write(LogLevel.Trace, correlation_id, None, message, *args, **kwargs)

    def _compose_error(self, error: Exception) -> str:
        """
        Composes an human-readable error description

        :param error: an error to format.
        :return: a human-reable error description.
        """
        builder = ''

        builder += str(error) if not hasattr(error, 'message') else error.message

        app_error = error
        if hasattr(app_error, 'cause'):
            builder += ' Cause by: '
            builder += str(app_error.cause)

        if hasattr(error, 'stack_trace'):
            builder += ' Stack trace: '
            builder += error.stack_trace

        return builder
