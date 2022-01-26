# -*- coding: utf-8 -*-

import datetime
import threading
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List, Optional

from pip_services3_commons.config import IReconfigurable, ConfigParams
from pip_services3_commons.errors import ErrorDescriptionFactory
from pip_services3_commons.refer import IReferenceable, IReferences, Descriptor

from pip_services3_components.trace.ITracer import ITracer
from pip_services3_components.trace.OperationTrace import OperationTrace
from pip_services3_components.trace.TraceTiming import TraceTiming


class CachedTracer(ITracer, IReconfigurable, IReferenceable, ABC):
    """
    Abstract tracer that caches recorded traces in memory and periodically dumps them.
    Child classes implement saving cached traces to their specified destinations.

    ### Configuration parameters ###
        - source:            source (context) name
        - options:
            - interval:        interval in milliseconds to save log messages (default: 10 seconds)
            - max_cache_size:  maximum number of messages stored in this cache (default: 100)

    ### References ###
        - `\*:context-info:\*:\*:1.0`    (optional) :class:`ContextInfo <pip_services3_components.info.ContextInfo.ContextInfo>` to detect the context id and specify counters source


    See :class:`ITracer <pip_services3_components.trace.ITracer.ITracer>`, :class:`OperationTrace <pip_services3_components.trace.OperationTrace.OperationTrace>`
    """

    def __init__(self):
        """
        Creates a new instance of the logger.
        """
        super().__init__()

        self._source: str = None
        self._cache: List[OperationTrace] = []
        self._updated = False
        self._last_dump_time: float = datetime.datetime.now().timestamp()
        self._max_cache_size = 100
        self._interval = 10000
        self.__lock = threading.Lock()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._interval = config.get_as_long_with_default("options.interval", self._interval)
        self._max_cache_size = config.get_as_integer_with_default("options.max_cache_size", self._max_cache_size)
        self._source = config.get_as_string_with_default("source", self._source)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        context_info = references.get_one_optional(Descriptor("pip-services", "context-info", "*", "*", "1.0"))
        if context_info is not None and self._source is None:
            self._source = context_info.name

    def _write(self, correlation_id: Optional[str], component: str, operation: str, error: Optional[Exception],
               duration: float):
        """
        Writes a log message to the logger destination.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param component: a name of called component
        :param operation: a name of the executed operation.
        :param error: an error object associated with this trace.
        :param duration: execution duration in milliseconds.
        """
        error_desc = None if error is None else ErrorDescriptionFactory.create(error)
        trace = OperationTrace(
            datetime.datetime.now(),
            self._source,
            component,
            operation,
            correlation_id,
            duration,
            error_desc
        )

        with self.__lock:
            self._cache.append(trace)

        self._update()

    def trace(self, correlation_id: Optional[str], component: str, operation: str, duration: float):
        """
        Records an operation trace with its name and duration

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param component: a name of called component
        :param operation: a name of the executed operation.
        :param duration: execution duration in milliseconds.
        """
        self._write(correlation_id, component, operation, None, duration)

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
        self._write(correlation_id, component, operation, error, duration)

    def begin_trace(self, correlation_id: Optional[str], component: str, operation: str) -> TraceTiming:
        """
        Begings recording an operation trace

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param component: a name of called component
        :param operation: a name of the executed operation.
        :return: a trace timing object.
        """

        return TraceTiming(correlation_id, component, operation, self)

    @abstractmethod
    def _save(self, messages: List[OperationTrace]):
        """
        Saves log messages from the cache.

        :param messages: a list with log messages
        :return: error or `None` for success.
        """

    def clear(self):
        """
        Clears (removes) all cached log messages.
        """
        self._cache = []
        self._updated = False

    def dump(self):
        """
        Dumps (writes) the currently cached log messages.

        See :func:`_write <pip_services3_components.trace.CachedTracer.CachedTracer._write>`
        """
        with self.__lock:
            if self._updated:
                if not self._updated:
                    return
                traces = self._cache
                self._cache = []

                try:
                    self._save(traces)
                except Exception as err:
                    # Adds traces back to the cache
                    traces += deepcopy(self._cache)

                    # Truncate cache
                    delete_count = len(self._cache) - self._max_cache_size
                    if delete_count > 0:
                        self._cache = self._cache[delete_count:]

                self._updated = False
                self._last_dump_time = datetime.datetime.now().timestamp() * 1000

    def _update(self):
        """
        Makes trace cache as updated
        and dumps it when timeout expires.

        See :func:`dump <pip_services3_components.trace.CachedTracer.CachedTracer.dump>`
        """
        with self.__lock:
            self._updated = True
        now = datetime.datetime.now().timestamp() * 1000
        if now > self._last_dump_time + self._interval:
            try:
                self.dump()
            except Exception as err:
                # Todo: decide what to do
                pass
