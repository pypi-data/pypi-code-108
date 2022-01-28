#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> from List import list
>>> l = list(["a", 'b', 1])
>>> _ = l | print
a
b
1
>>> l |= print
a
b
1
>>> l
[None, None, None]
>>> ~l
[1, 'b', 'a']
>>> t = (0, 1)
>>> l - t
['a', 'b']
>>> l -= t
Traceback (most recent call last):
  ...
ValueError: list.remove(x): x not in list
>>> t = ("a", "b")
>>> l -= t
>>> l
[1]
>>> str_list = list(["0", '2', "1"])
>>> int_list = str_list | int
>>> int_list
[0, 2, 1]
>>> 
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["list"]

from collections.abc import Callable, Iterator
from typing import List, Any


class list(list):
    def __or__(self, other: Callable) -> List[Any]:

        """
        This function implements '<list> | <function>'.
        """

        return [other(x) for x in self]

    def __ior__(self, other: Callable) -> List[Any]:

        """
        This function implements '<list> |= <function>'.
        """

        return [other(x) for x in self]

    def __invert__(self) -> List[Any]:

        """
        This function implements '~<list>'.
        """

        return self[::-1]

    def __inv__(self) -> List[Any]:

        """
        This function implements '~<list>'.
        """

        return self[::-1]

    def __sub__(self, other: Iterator[Any]) -> List[Any]:

        """
        This function implements '<list> - <Iterator>'
        """

        return [x for x in self if x not in other]

    def __isub__(self, other: Iterator[Any]) -> List[Any]:

        """
        This function implements '<list> -= <Iterator>'
        """

        [self.remove(x) for x in other]
        return self
