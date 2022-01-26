# -*- coding: utf-8 -*-
from typing import List

from pip_services3_expressions.variants.Variant import Variant


class CalculationStack:
    """
    Implements a stack of Variant values.
    """

    def __init__(self):
        self.__values: List[Variant] = []

    @property
    def length(self) -> int:
        return len(self.__values)

    def push(self, value: Variant):
        self.__values.append(value)

    def pop(self) -> Variant:
        if len(self.__values) == 0:
            raise Exception('Stack is empty.')
        return self.__values.pop()

    def peek_at(self, index: int) -> Variant:
        return self.__values[index]

    def peek(self) -> Variant:
        if len(self.__values) == 0:
            raise Exception('Stack is empty.')
        return self.__values[-1]
