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

>>> from Dict import *
>>> a = {"a": 0, 0: "a", (0, "a"): ("a", 0)}
>>> b = a.copy()
>>> cleandict(b, ["a"])
{'a': 0}
>>> cleandict(a, ["a"], invers=True)
{0: 'a', (0, 'a'): ('a', 0)}
>>> a
{0: 'a', (0, 'a'): ('a', 0)}
>>> b
{'a': 0}
>>> a = {"a": 0, 0: "a", (0, "a"): ("a", 0)}
>>> copy_cleandict(a, ["a"])
{'a': 0}
>>> copy_cleandict(a, ["a"], invers=True)
{0: 'a', (0, 'a'): ('a', 0)}
>>> a
{'a': 0, 0: 'a', (0, 'a'): ('a', 0)}
>>> d = dict(zip([0,1], (2,3)))
>>> _ = d | print
0 2
1 3
>>> _ = d @ print
0
1
>>> _ = d >> print
2
3
>>> d - [0]
{1: 3}
>>> d + [0]
{0: 2}
>>> from math import factorial, gcd
>>> d @= factorial
>>> d
{0: 1, 1: 1}
>>> d = dict(zip([0,1], (2,3)))
>>> d >>= factorial
>>> d
{0: 2, 1: 6}
>>> d |= gcd
>>> d
{0: 2, 1: 1}
>>> ~d
{2: 0, 1: 1}
>>> d -= [0]
>>> d
{1: 1}
>>> d[2] = 0
>>> d += [2]
>>> d
{2: 0}
>>>
"""

__version__ = "0.0.4"
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

__all__ = ["cleandict", "copy_cleandict", "dict"]

from collections.abc import Hashable, Iterator, Callable
from typing import List, Dict, Any


def cleandict(dict_: dict, keys: List[Hashable], invers: bool = False) -> dict:

    """
    This function clean a dictionary.
    """

    if invers:
        for key in keys:
            del dict_[key]
        return dict_

    to_delete = [key for key in dict_.keys() if key not in keys]

    for key in to_delete:
        del dict_[key]
    return dict_


def copy_cleandict(dict_: dict, *args, **kwargs) -> dict:

    """
    This function copy and clean a dictionary.

    args and kwargs are passed to cleandict.
    """

    return cleandict(dict_.copy(), *args, **kwargs)


class dict(dict):
    def __or__(self, other: Callable) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> | <function>'.
        """

        return dict((k, other(k, v)) for k, v in self.items())

    def __ior__(self, other: Callable) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> |= <function>'.
        """

        return dict((k, other(k, v)) for k, v in self.items())

    def __matmul__(self, other: Callable) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> @ function'.
        """

        return dict((k, other(k)) for k in self.keys())

    def __imatmul__(self, other: Callable) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> @= function'.
        """

        return dict((k, other(k)) for k in self.keys())

    def __invert__(self) -> Dict[Hashable, Any]:

        """
        This function implements '~<dict>'.
        """

        return dict((v, k) for k, v in self.items())

    def __inv__(self) -> Dict[Hashable, Any]:

        """
        This function implements '~<dict>'.
        """

        return dict((v, k) for k, v in self.items())

    def __rshift__(self, other: Callable) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> >> function'.
        """

        return dict((k, other(v)) for k, v in self.items())

    def __irshift__(self, other: Callable) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> >> function'.
        """

        return dict((k, other(v)) for k, v in self.items())

    def __sub__(self, other: Iterator[Hashable]) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> - <Iterator>'
        """

        return dict((k, v) for k, v in self.items() if k not in other)

    def __isub__(self, other: Iterator[Hashable]) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> -= <Iterator>'
        """

        return dict((k, v) for k, v in self.items() if k not in other)

    def __add__(self, other: Iterator[Hashable]) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> + <Iterator>'
        """

        return dict((k, v) for k, v in self.items() if k in other)

    def __iadd__(self, other: Iterator[Hashable]) -> Dict[Hashable, Any]:

        """
        This function implements '<dict> += <Iterator>'
        """

        return dict((k, v) for k, v in self.items() if k in other)
