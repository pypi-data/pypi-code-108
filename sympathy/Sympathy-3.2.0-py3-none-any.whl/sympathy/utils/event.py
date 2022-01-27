# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

from contextlib import contextmanager
from typing import Callable


def _func(f):
    return f.__func__


def _self(f):
    return f.__self__


def _class(f):
    return f.__class__


class Event:
    """
    Basic event framework for in thread callbacks.
    """

    def __init__(self, *args, **kwargs):
        self._handlers = {}

    def add_handler(self, method: Callable) -> None:
        self._handlers[(_self(method), _func(method))] = True

    def remove_handler(self, method: Callable) -> None:
        self._handlers.pop((_self(method), _func(method)), None)

    @contextmanager
    def block_handler(self, method: Callable) -> None:
        key = (_self(method), _func(method))
        old = self._handlers[key]
        self._handlers[key] = False
        try:
            yield
        finally:
            self._handlers[key] = old

    def emit(self, *args, **kwargs) -> None:
        for (obj, func), enabled in self._handlers.items():
            if enabled:
                func(obj, *args, **kwargs)
