#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 26.01.22
@author: felix
"""
from typing import List

from pyoverload import overload


class Example:
    @overload
    def other_func(self):
        return 0

    @overload
    def other_func(self, a: int, b: int):
        return (a * a) / b

    # @overload
    # def my_func(self):
    #     return 0
    #
    # @overload
    # def my_func(self, a: int, b: str):
    #     return b * a
    #
    # @overload
    # def my_func(self, a: int, b: int):
    #     return a * b
    #
    # @overload
    # def my_func(self, a: int, b: int, c: int):
    #     return a * b * c
    #
    # @overload
    # def my_func(self, *, val: int, other_val: int):
    #     return val, other_val
    #
    # @overload
    # def my_func(self, val: List[int], other_val, /):
    #     return [other_val * v for v in val]
    #
    # @overload
    # def my_func(self, val: List[str], other_val, /):
    #     return val, other_val
