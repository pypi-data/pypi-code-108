# -*- coding: utf-8 -*-
from typing import Any


class CharReferenceInterval:
    """
    Represents a character interval that keeps a reference.
    This class is internal and used by [[CharReferenceMap]].
    """

    def __init__(self, start: int, end: int, reference: Any):
        if start > end:
            raise Exception('Start must be less or equal End')
        self.__start = start
        self.__end = end
        self.__reference = reference

    @property
    def start(self) -> int:
        return self.__start

    @property
    def end(self) -> int:
        return self.__end

    @property
    def reference(self) -> Any:
        return self.__reference

    def in_range(self, symbol: int) -> bool:
        return self.__start <= symbol <= self.__end
