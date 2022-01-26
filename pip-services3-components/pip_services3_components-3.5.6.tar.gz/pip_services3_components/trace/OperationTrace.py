# -*- coding: utf-8 -*-
from datetime import datetime

from pip_services3_commons.errors import ErrorDescription


class OperationTrace:
    """
    Data object to store captured operation traces.
    This object is used by :class:`CachedTracer <pip_services3_components.trace.CachedTracer.CachedTracer>`.
    """

    def __init__(self, time: datetime, source: str, component: str,
                 operation: str, correlation_id: str, duration: float, error: ErrorDescription):
        """
        Create new instance of OperationTrace

        :param time: The time when operation was executed
        :param source: The source (context name)
        :param component: The name of component
        :param operation: The name of the executed operation
        :param correlation_id: The transaction id to trace execution through call chain.
        :param duration: The duration of the operation in milliseconds
        :param error: The description of the captured error
        """

        # The time when operation was executed
        self.time: datetime = time
        # The source (context name)
        self.source: str = source
        # The name of component
        self.component: str = component
        # The name of the executed operation
        self.operation: str = operation
        # The transaction id to trace execution through call chain.
        self.correlation_id: str = correlation_id
        # The duration of the operation in milliseconds
        self.duration: float = duration

        """
        The description of the captured error
        
        :class:`ErrorDescription <pip_services3_commons.errors.ErrorDescription.ErrorDescription>`,
        :class:`ApplicationException <pip_services3_commons.errors.ApplicationException.ApplicationException>`
        """
        self.error: ErrorDescription = error
