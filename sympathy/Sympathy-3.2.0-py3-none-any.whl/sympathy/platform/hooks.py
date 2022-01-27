# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
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
"""
Common definitions of hooks for sympathy.app, this provides extensibility for
plugins, etc. by setting individual hooks. In contrast with plugins, each hook
has only a single value.

To define a new hook, create a new definition. On the sympathy.app side, import
and use it. On the user side, import this module and set desired hooks.
"""

from typing import TypeVar, Generic, Callable, List
from sympathy.utils import log
import requests

logger = log.get_logger('app.hooks')

T = TypeVar('T')


class Hook(Generic[T]):
    """
    Typed container for a single hook value.
    """
    def __init__(self, value: T, name: str = ''):
        self._value = value
        self._name = name

    def set(self, value: T):
        """
        Replace hook value.
        """
        logger.info('Hook %s.set(%s)', self._name, value)
        self._value = value

    def get(self) -> T:
        """
        Get hook value.
        """
        return self._value

    @property
    def value(self) -> T:
        """
        Get hook value (property).
        """
        return self.get()


pip_install_options: Hook[Callable[[], List[str]]] = Hook(lambda: [])


class RequestHTTP:
    def get(self, url, **kwargs) -> requests.Response:
        return requests.get(url, **kwargs)

    def post(self, url, **kwargs) -> requests.Response:
        return requests.post(url, **kwargs)

    def put(self, url, **kwargs) -> requests.Response:
        return requests.put(url, **kwargs)

    def patch(self, url, **kwargs) -> requests.Response:
        return requests.patch(url, **kwargs)

    def delete(self, url, **kwargs) -> requests.Response:
        return requests.delete(url, **kwargs)


request_http: Hook[RequestHTTP] = Hook(RequestHTTP())
# TODO(erik): move these back to app?
pip_install_options: Hook[Callable[[], List[str]]] = Hook(lambda: [])
# Up to two brief lines to show on splash.
splash_extra_text: Hook[Callable[[], str]] = Hook(lambda: [])
# Short label to show in toolbar.
status_extra_text: Hook[Callable[[], str]] = Hook(lambda: [])


def _setup_hooks():
    for key, obj in globals().items():
        if isinstance(obj, Hook):
            obj._name = key


_setup_hooks()
