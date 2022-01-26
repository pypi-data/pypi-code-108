# -*- coding: utf-8 -*-
from typing import Optional

from pip_services3_components.trace.ITracer import ITracer
from pip_services3_components.trace.TraceTiming import TraceTiming


class NullTracer(ITracer):
    """
    Dummy implementation of tracer that doesn't do anything.

    It can be used in testing or in situations when tracing is required
    but shall be disabled.

    See :class:`ITracer <pip_services3_components.trace.ITracer.ITracer>`
    """

    def trace(self, correlation_id: Optional[str], component: str, operation: str, duration: float):
        """
        Records an operation trace with its name and duration

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param component: a name of called component
        :param operation: a name of the executed operation.
        :param duration: execution duration in milliseconds.
        :return:
        """
        # Do nothing...

    def failure(self, correlation_id: Optional[str], component: str, operation: str, error: Exception,
                duration: float):
        """
        Records an operation failure with its name, duration and error

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param component: a name of called component
        :param operation: a name of the executed operation.
        :param error: an error object associated with this trace.
        :param duration: execution duration in milliseconds.
        """
        # Do nothing...

    def begin_trace(self, correlation_id: Optional[str], component: str, operation: str) -> TraceTiming:
        """
        Begings recording an operation traceBegings recording an operation trace

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param component: a name of called component
        :param operation: a name of the executed operation.
        :return: a trace timing object.
        """
        return TraceTiming(correlation_id, component, operation, self)
