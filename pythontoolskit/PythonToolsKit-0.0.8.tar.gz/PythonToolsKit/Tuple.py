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

>>> from Tuple import tuple
>>> t = tuple(("a", 'b', 1))
>>> _ = t | print
a
b
1
>>> t |= print
a
b
1
>>> t
(None, None, None)
>>> t = tuple(("a", 'b', 1))
>>> ~t
(1, 'b', 'a')
>>> l = [0, 1]
>>> t -l
('a', 'b')
>>> t -= l
>>> t
('a', 'b')
>>> t = tuple(("a", 'b', 1))
>>> l = ["a", "b"]
>>> t -= l
>>> t
(1,)
>>> str_tuple = tuple(["0", '2', "1"])
>>> int_tuple = str_tuple | int
>>> int_tuple
(0, 2, 1)
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

__all__ = ["tuple"]

from collections.abc import Callable, Iterator
from typing import Tuple, Any


class tuple(tuple):
    def __or__(self, other: Callable) -> Tuple[Any]:

        """
        This function implements '<tuple> | <function>'.
        """

        return tuple(other(x) for x in self)

    def __ior__(self, other: Callable) -> Tuple[Any]:

        """
        This function implements '<tuple> |= <function>'.
        """

        return tuple(other(x) for x in self)

    def __invert__(self) -> Tuple[Any]:

        """
        This function implements '~<tuple>'.
        """

        return self[::-1]

    def __inv__(self) -> Tuple[Any]:

        """
        This function implements '~<tuple>'.
        """

        return self[::-1]

    def __sub__(self, other: Iterator[Any]) -> Tuple[Any]:

        """
        This function implements '<tuple> - <Iterator>'
        """

        return tuple(x for x in self if x not in other)

    def __isub__(self, other: Iterator[Any]) -> Tuple[Any]:

        """
        This function implements '<tuple> -= <Iterator>'
        """

        return tuple(x for x in self if x not in other)
