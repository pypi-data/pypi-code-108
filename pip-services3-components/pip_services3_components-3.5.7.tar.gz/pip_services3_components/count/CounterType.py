# -*- coding: utf-8 -*-
"""
    pip_services3_components.counters.CounterType
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Counter type enumeration
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from enum import Enum


class CounterType(Enum):
    """
    Types of counters that measure different types of metrics
    """
    # Counters that measure execution time intervals
    Interval = 0
    # Counters that keeps the latest measured value
    LastValue = 1
    # Counters that measure min/average/max statistics
    Statistics = 2
    # Counter that record timestamps
    Timestamp = 3
    # Counter that increment counters
    Increment = 4

    @staticmethod
    def to_string(typ):
        if typ == CounterType.Interval:
            return "INTERVAL"
        if typ == CounterType.LastValue:
            return "LAST"
        if typ == CounterType.Statistics:
            return "STATS"
        if typ == CounterType.Timestamp:
            return "TIME"
        if typ == CounterType.Increment:
            return "COUNT"
        return "UNDEF"
