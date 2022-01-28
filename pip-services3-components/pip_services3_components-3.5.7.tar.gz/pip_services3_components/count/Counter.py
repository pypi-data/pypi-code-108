# -*- coding: utf-8 -*-
"""
    pip_services3_components.counters.Counter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Counter object implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import datetime
from typing import Optional

from pip_services3_components.count import CounterType


class Counter:
    """
    Data object to store measurement for a performance counter.
    This object is used by :class:`CachedCounters <pip_services3_components.count.CachedCounters.CachedCounters>` to store counters.
    """

    def __init__(self, name: str = None, tipe: CounterType = None):
        """
        Creates a instance of the data obejct

        :param name: a counter name.

        :param tipe: a counter type.
        """
        # The last recorded value
        self.last: Optional[float] = None
        # The total count
        self.count: Optional[int] = None
        # The minimum value
        self.min: Optional[float] = None
        # The maximum value
        self.max: Optional[float] = None
        # The average value
        self.average: Optional[float] = None
        # The recorded timestamp
        self.time: Optional[datetime.datetime] = None
        # The counter unique name
        self.name: str = name
        # The counter type that defines measurement algorithm
        self.type: CounterType = tipe
