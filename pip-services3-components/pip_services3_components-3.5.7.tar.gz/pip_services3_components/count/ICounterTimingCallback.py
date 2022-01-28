# -*- coding: utf-8 -*-
"""
    pip_services3_components.counters.ICounterTimingCallback
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for performance timing callbacks.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC


class ICounterTimingCallback(ABC):
    """
    Interface for a callback to end measurement of execution elapsed time.

    See :class:`CounterTiming <pip_services3_components.count.CounterTiming.CounterTiming>`
    """

    def end_timing(self, name: str, elapsed: float):
        """
        Ends measurement of execution elapsed time and updates specified counter.

        :param name: a counter name
        :param elapsed: execution elapsed time in milliseconds to update the counter.
        """
        raise NotImplementedError('Method from interface definition')
