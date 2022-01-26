# -*- coding: utf-8 -*-
from typing import Any, List

from .CharReferenceInterval import CharReferenceInterval


class CharReferenceMap:

    def __init__(self):
        self.__initial_interval = []
        self.__other_intervals: List[CharReferenceInterval] = []
        self.clear()

    def add_default_interval(self, reference: Any):
        self.add_interval(0x0000, 0xfffe, reference)

    def add_interval(self, start: int, end: int, reference: Any):
        if start > end:
            raise Exception('Start must be less or equal End')
        end = 0xfffe if end == 0xffff else end

        index = start
        while index < 0x0100 and index <= end:
            self.__initial_interval[index] = reference
            index += 1

        if end >= 0x0100:
            start = 0x0100 if start < 0x0100 else start
            self.__other_intervals.insert(0, CharReferenceInterval(start, end, reference))

    def clear(self):
        for index in range(0x0100):
            try:
                self.__initial_interval[index] = None
            except IndexError:
                self.__initial_interval.append(None)

        self.__other_intervals = []

    def lookup(self, symbol: int) -> Any:
        if -1 < symbol < 0x0100:
            return self.__initial_interval[symbol]
        else:
            for interval in self.__other_intervals:
                if interval.in_range(symbol):
                    return interval.reference

            return None
