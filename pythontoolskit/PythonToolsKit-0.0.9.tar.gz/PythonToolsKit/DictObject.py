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

r"""
This package implements tools to build python package and tools.

>>> d = DictObject({"_1": 1})
>>> d._1
1
>>> d["_1"]
1
>>> d.get("_1")
1
>>> d.get("_2")
>>> d = DictObject({"-1": 1})
>>> d["_1"]
1
>>> d["_2"] = 2
>>> d["_2"]
2
>>> d = JsonDeserializer('{"-1": 1}')
>>> d._1
1
>>> d = JsonDeserializer('{"-1": {"-1": 1}}')
>>> d._1._1
1
>>> from io import StringIO
>>> csv = CsvDeserializer(StringIO("-1,-2\n1,2\n3,4"))
>>> [(d._1, d._2) for d in csv]
[('1', '2'), ('3', '4')]
>>> csv = CsvDeserializer(StringIO("-1,-2\n1,2\n3,4"))
>>> [d for d in csv]
[<DictObject.DictObject object at ...>, <DictObject.DictObject object at ...>]
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

__all__ = ["DictObject", "JsonDeserializer", "CsvDeserializer"]

from collections.abc import Callable
from typing import Union, Any
from json import loads, load
from io import TextIOWrapper
from csv import DictReader

Json = Union[str, bytes]


class DictObject:

    """
    This class create object and sub-object from Json Structure.
    """

    def __init__(self, data: dict):
        if isinstance(data, dict):

            for key, value in data.items():
                if isinstance(value, dict):
                    setattr(self, key.replace("-", "_"), DictObject(value))
                else:
                    setattr(self, key.replace("-", "_"), value)

            dict_ = self._dict = self.__dict__
            for attribute in dir(data):
                if isinstance(getattr(data, attribute), Callable) and (
                    not attribute.startswith("__")
                    and not attribute.endswith("__")
                ):
                    setattr(self, attribute, getattr(dict_, attribute))

            for attribute in ("__getitem__", "__setitem__"):
                setattr(self, attribute, getattr(dict_, attribute))

    def __getitem__(self, item: str) -> Any:
        return self._dict[item]

    def __setitem__(self, item: str, value: Any) -> None:
        self._dict[item] = value


class JsonDeserializer(DictObject):

    """
    DictObject for Json.
    """

    def __init__(self, json: Union[Json, TextIOWrapper], *args, **kwargs):
        if isinstance(
            json, (str, bytes)
        ):  # 3.10 isinstance(json, str | bytes)
            data = loads(json, *args, **kwargs)
        elif isinstance(json, TextIOWrapper):
            data = load(json, *args, **kwargs)
        else:
            raise TypeError(
                "argument 'json' should be str, bytes or TextIOWrapper"
            )

        super().__init__(data)


class CsvDeserializer:

    """
    DictObjects from CSV.
    """

    def __init__(self, csv: TextIOWrapper, *args, **kwargs):
        self.reader = DictReader(csv, *args, **kwargs)

    def __iter__(self):
        for dict_ in self.reader:
            yield DictObject(dict_)
