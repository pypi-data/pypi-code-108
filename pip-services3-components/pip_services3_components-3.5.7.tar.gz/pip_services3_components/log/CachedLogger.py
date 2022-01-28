# -*- coding: utf-8 -*-
"""
    pip_services3_components.log.CachedLogger
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Cached logger implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import threading
import time
from abc import abstractmethod
from typing import List, Optional

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.config.IReconfigurable import IReconfigurable
from pip_services3_commons.errors.ErrorDescriptionFactory import ErrorDescriptionFactory

from pip_services3_components.log import LogLevel
from .LogMessage import LogMessage
from .Logger import Logger


class CachedLogger(Logger, IReconfigurable):
    """
    Abstract logger that caches captured log messages in memory and periodically dumps them.
    Child classes implement saving cached messages to their specified destinations.

    ### Configuration parameters ###
        - level:             maximum log level to capture
        - source:            source (context) name
        - options:
            - interval:        interval in milliseconds to save log messages (default: 10 seconds)
            - max_cache_size:  maximum number of messages stored in this cache (default: 100)

    ### References ###
        - `*:context-info:*:*:1.0`     (optional) :class:`ContextInfo <pip_services3_components.info.ContextInfo.ContextInfo>` to detect the context id and specify counters source
    """

    __lock = None

    def __init__(self):
        """
        Creates a new instance of the logger.
        """
        super().__init__()
        self._cache: List[LogMessage] = []
        self._updated = False
        self._interval = 10000
        self._last_dump_time = time.perf_counter() * 1000
        self._max_cache_size = 100
        self.__lock = threading.Lock()

    def _write(self, level: LogLevel, correlation_id: Optional[str], ex: Exception, message: str):
        """
        Writes a log message to the logger destination.

        :param level: a log level.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param ex: an error object associated with this message.

        :param message: a human-readable message to log.
        """
        error = ErrorDescriptionFactory.create(ex) if not (ex is None) else None
        source = self._source  # socket.gethostname()
        log_message = LogMessage(level, source, correlation_id, error, message)

        with self.__lock:
            self._cache.append(log_message)

        self._update()

    @abstractmethod
    def _save(self, messages: List[LogMessage]):
        """
        Saves log messages from the cache.

        :param messages: a list with log messages
        """
        raise NotImplementedError('Method from abstract implementation')

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._interval = config.get_as_float_with_default("interval", self._interval)
        self._max_cache_size = config.get_as_integer_with_default("options.max_cache_size", self._max_cache_size)

    def clear(self):
        """
        Clears (removes) all cached log messages.
        """
        with self.__lock:
            self._cache = []
            self._updated = False

    def dump(self):
        """
        Dumps (writes) the currently cached log messages.
        """
        with self.__lock:
            if self._updated:
                if not self._updated:
                    return

                messages = self._cache
                self._cache = []

                self._save(messages)

                # Truncate cache
                self._cache = messages
                delete_count = len(self._cache) - self._max_cache_size
                if delete_count > 0:
                    self._cache = self._cache[0:delete_count]

                self._updated = False
                self._last_dump_time = time.perf_counter() * 100

    def _update(self):
        """
        Makes message cache as updated and dumps it when timeout expires.
        """
        with self.__lock:
            self._updated = True

        if time.perf_counter() * 1000 > self._last_dump_time + self._interval:
            try:
                self.dump()
            except:
                # Todo: decide what to do
                pass
