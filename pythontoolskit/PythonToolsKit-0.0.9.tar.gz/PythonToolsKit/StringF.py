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

>>> string_lengthformat("azerty")
'azerty,       '
>>> string_lengthformat("azertyazertyazerty")
'azertyazer...,'
>>> print(strings_tableformat([(0, 1), ("a" * 50, "b" * 50)]))
|0            |1            |
|aaaaaaaaaa...|bbbbbbbbbb...|
>>> print(strings_tableformat([(0, 1), ("a" * 50, "b" * 50)], length=[13, 26]))
|0            |1                         |
|aaaaaaaaaa...|bbbbbbbbbbbbbbbbbbbbbbb...|
>>> print(strings_tableformat([(0, 1), ("a" * 50, "b" * 50)], length=[13, 26]))
>>> class A:
...     def __init__(self):
...             self.a = "a"
...             self.b = "b"
...             self.azerty = 1.1
...
>>> a = A()
>>> print(str(Object_StringF(a)))
A(a='a', b='b', azerty=1.1)
>>> print(str(Object_StringF(a, table_mode=True)))
A
|Attribut     |Value        |
|-------------|-------------|
|a            |a            |
|b            |b            |
|azerty       |1.1          |
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

__all__ = ["string_lengthformat", "strings_tableformat", "Object_StringF"]

from collections.abc import Iterator, Sequence
from typing import Union


def string_lengthformat(
    string: str, length: int = 13, end: str = "...", separator: str = ","
) -> str:

    """
    This function formats string length.
    """

    if not isinstance(string, str):
        string = str(string)

    length_string = len(string)

    if length_string > length:
        string = f"{string[:length - len(end)]}...{separator}"
    else:
        string = f"{string}{' ' * (length - length_string)}{separator}"

    return string


def strings_tableformat(
    strings: Iterator[Iterator[str]],
    length: Union[Sequence[int], int] = 13,
    end: str = "...",
    separator: str = "|",
    columns: Iterator[str] = None,
) -> str:

    """
    This function returns a formatted table of strings.
    """

    table = []

    if not isinstance(length, int):
        llength = len(length)

        global counter
        counter = 0

        def get_length():
            global counter
            value = length[counter % llength]
            counter += 1
            return value

    else:

        def get_length():
            return length

    if columns is not None:
        first_line = [separator]
        second_line = [separator]

        for string in columns:
            first_line.append(
                string_lengthformat(string, get_length(), end, separator)
            )
            second_length = get_length()
            second_line.append(
                string_lengthformat(
                    "-" * second_length, second_length, end, separator
                )
            )

        table.append(first_line)
        table.append(second_line)

    for string_iter in strings:

        line = [separator]
        for string in string_iter:
            line.append(
                string_lengthformat(string, get_length(), end, separator)
            )

        table.append(line)

    return "\n".join(["".join(strings) for strings in table])


class Object_StringF:

    """
    This class implements a generic __str__ methods.
    """

    def __init__(
        self, object_: object, *args, table_mode: bool = False, **kwargs
    ):
        self.get_items = object_.__dict__.items
        self.table_mode = table_mode
        self.object = object_
        self.kwargs = kwargs
        self.args = args

    def __str__(self):
        if self.table_mode:
            string = f"{self.object.__class__.__name__}\n"
            string += strings_tableformat(
                self.get_items(),
                *self.args,
                **self.kwargs,
                columns=["Attribut", "Value"],
            )
        else:
            string = f"{self.object.__class__.__name__}("
            string += ", ".join(
                [
                    "=".join((key, repr(value)))
                    for key, value in self.get_items()
                ]
            )
            string += ")"
        return string
