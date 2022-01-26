# -*- coding: utf-8 -*-
"""
    pip_services3_components.counters.LogCounters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Log counters implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List

from pip_services3_commons.convert.StringConverter import StringConverter
from pip_services3_commons.refer import IReferences
from pip_services3_commons.refer.IReferenceable import IReferenceable

from pip_services3_components.count import Counter
from .CachedCounters import CachedCounters
from ..log.CompositeLogger import CompositeLogger


class LogCounters(CachedCounters, IReferenceable):
    """
    Performance counters that periodically dumps counters measurements to logger.

    ### Configuration parameters ###
        - options:
            - interval:          interval in milliseconds to save current counters measurements (default: 5 mins)
            - reset_timeout:     timeout in milliseconds to reset the counters. 0 disables the reset (default: 0)

    ### References ###
        - `*:logger:*:*:1.0`           :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to dump the captured counters
        - `*:context-info:*:*:1.0`     (optional) :class:`ContextInfo <pip_services3_components.info.ContextInfo.ContextInfo>` to detect the context id and specify counters source

    Example:

    .. code-block:: python

        counters = LogCounters()
        counters.set_references(References.from_tuples(
                    Descriptor("pip-services", "logger", "console", "default", "1.0"), ConsoleLogger()))

        counters.increment("mycomponent.mymethod.calls")
        timing = counters.begin_timing("mycomponent.mymethod.exec_time")
        # do something
        timing.end_timing()
    """
    __logger: CompositeLogger = CompositeLogger()

    #

    # def get_descriptor(self):
    #     return LogCountersDescriptor

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self.__logger.set_references(references)

    def __counter_to_string(self, counter: Counter) -> str:
        result = "Counter " + counter.name + " { "
        result += "\"type\": " + str(counter.type)
        if not (counter.last is None):
            result += ", \"last\": " + StringConverter.to_string(counter.last)
        if not (counter.count is None):
            result += ", \"count\": " + StringConverter.to_string(counter.count)
        if not (counter.min is None):
            result += ", \"min\": " + StringConverter.to_string(counter.min)
        if not (counter.max is None):
            result += ", \"max\": " + StringConverter.to_string(counter.max)
        if not (counter.average is None):
            result += ", \"avg\": " + StringConverter.to_string(counter.average)
        if not (counter.time is None):
            result += ", \"time\": " + StringConverter.to_string(counter.time)
        result += " }"
        return result

    @staticmethod
    def _get_counter_name(counter: Counter) -> str:
        return counter.name

    def _save(self, counters: List[Counter]):
        """
        Saves the current counters measurements.

        :param counters: current counters measurements to be saves.
        """
        if self.__logger is None:
            return
        if len(counters) == 0:
            return

        # Sort counters by name
        counters = sorted(counters, key=LogCounters._get_counter_name)

        for counter in counters:
            self.__logger.info("counters", self.__counter_to_string(counter))
