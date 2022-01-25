# Copyright (c) 2014 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# XXX: Please add types to the functions in this file. Static type checking in
# Python prevents bugs!
# mypy: ignore-errors


import copy
import json


def dict_to_object(dictionary):
    return Object(copy.deepcopy(dictionary))


def json_to_object(string):
    return dict_to_object(json.loads(string))


class Object:
    """Object wrapper for a dictionary"""

    __hash__ = None

    def __init__(self, d=None):
        object.__setattr__(self, '_Object__dict', dict() if d is None else d)

    # Dictionary-like access / updates
    def __getitem__(self, name):
        value = self.__dict[name]
        if isinstance(value, dict):  # recursively view sub-dicts as objects
            value = Object(value)
        return value

    def __setitem__(self, name, value):
        self.__dict[name] = value

    def __delitem__(self, name):
        del self.__dict[name]

    def __len__(self) -> int:
        return len(self.__dict)

    # Object-like access / updates
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(repr(e))

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.__dict!r})'

    def __str__(self) -> str:
        return str(self.__dict)

    def __eq__(self, other: object) -> bool:
        return self.__class__ == other.__class__ and self.__dict == other.__dict

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def dictionary(self):
        return self.__dict
