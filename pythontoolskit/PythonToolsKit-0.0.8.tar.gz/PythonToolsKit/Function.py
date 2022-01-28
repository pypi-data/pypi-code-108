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

>>> from Function import *
>>> @def_Function
def print_char(char): print(char)
...
>>> _ = print_char << "abc"
a
b
c
>>> print_char('a')
a
>>> print_char = Function(print)
>>> _ = print_char << "abc"
a
b
c
>>> print_char('a')
a
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

__all__ = ["def_Function", "Function"]

from collections.abc import Callable
from typing import List, Any, Iterator


def def_Function(function: Callable) -> Callable:

    """
    This decorator transform basic function in Function.
    """

    return Function(function)


class Function(Callable):

    """
    This class implements features for basic function.
    """

    def __init__(self, function: Callable):
        self.function = function

    def __call__(self, *args, **kwargs) -> Any:
        return self.function(*args, **kwargs)

    def __lshift__(self, other: Iterator) -> List[Any]:

        """
        This function implements '<Function> << <Iterator>'.
        """

        function = self.function
        return [function(x) for x in other]
