# -*- coding: utf-8 -*-
from typing import Optional

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.refer import IReferenceable, IReferences

from pip_services3_components.log import CompositeLogger, LogLevel, LogLevelConverter
from pip_services3_components.trace.ITracer import ITracer
from pip_services3_components.trace.TraceTiming import TraceTiming


class LogTracer(IConfigurable, IReferenceable, ITracer):
    """
    Tracer that dumps recorded traces to logger.

    ### Configuration parameters ###
        - options:
            - log_level:         log level to record traces (default: debug)

    ### References ###
        - `\*:logger:\*:\*:1.0`         :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to dump the captured counters
        - `\*:context-info:\*:\*:1.0`   (optional) :class:`ContextInfo <pip_services3_components.info.ContextInfo.ContextInfo>` to detect the context id and specify counters source

    See :class:`ITracer <pip_services3_components.trace.ITracer.ITracer>`, :class:`CachedCounters <pip_services3_components.count.CachedCounters.CachedCounters>`, :class:`CompositeLogger <pip_services3_components.log.CompositeLogger.CompositeLogger>`

    Example:

    .. code-block:: python
        tracer = LogTracer()
        tracer.set_references(References.from_tuples(
            Descriptor("pip-services", "logger", "console", "default", "1.0"), ConsoleLogger()
        ))

        timing = tracer.begin_trace("123", "mycomponent", "mymethod")
        try:
            ...
            timing.endTrace()
        except Exception as err:
            timing.end_failure(err)
    """

    __LOGGER = CompositeLogger()

    def __init__(self):
        """
        Creates a new instance of the tracer.
        """
        self.__log_level = LogLevel.Debug

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self.__log_level = LogLevelConverter.to_log_level(config.get_as_object('options.log_level'),
                                                          self.__log_level)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self.__LOGGER.set_references(references)

    def __log_trace(self, correlation_id: Optional[str], component: str, operation: str, error: Optional[Exception], duration: float):
        builder = ''

        if error is not None:
            builder += 'Failed to execute '
        else:
            builder += 'Executed '

        builder += component
        builder += "."
        builder += operation

        if duration > 0:
            builder += " in " + str(duration) + " msec"

        if error is not None:
            self.__LOGGER.error(correlation_id, error, builder)
        else:
            self.__LOGGER.log(self.__log_level, correlation_id, None, builder)

    def trace(self, correlation_id: Optional[str], component: str, operation: str, duration: float):
        """
        Records an operation trace with its name and duration

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param component: a name of called component
        :param operation: a name of the executed operation.
        :param duration: execution duration in milliseconds.
        """
        self.__log_trace(correlation_id, component, operation, None, duration)

    def begin_trace(self, correlation_id: Optional[str], component: str, operation: str) -> TraceTiming:
        """
        Begings recording an operation trace

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param component: a name of called component
        :param operation: a name of the executed operation. 
        :return: a trace timing object.
        """
        return TraceTiming(correlation_id, component, operation, self)
