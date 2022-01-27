#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 27.01.22
@author: felix
"""
from pyoverload import overload
from pyoverload.tmp import Example


class Other(Example):
    @overload
    def other_func(self, a):
        return a ** a + a

    @overload
    def other_func(self, a: int, b: int):
        return ((a * a) / b) + a

    @overload
    def other_func(self, a, b, c):
        return a + b + c


if __name__ == "__main__":
    other = Other()
    print(other.other_func())
    print(other.other_func(2))
    print(other.other_func(2, 3))
    print(other.other_func(2, 3, 4))
