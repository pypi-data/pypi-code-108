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
from typing import TypeVar, Generic, Dict
import pkg_resources

T = TypeVar('T')


class Plugin(Generic[T]):
    def __init__(self, identifier: str, interface: T):
        self.identifier = identifier
        self.interface = interface
        self._plugins = None
        self._errors = None
        self._require_errors = None
        self._entry_points = None

    def plugins(self) -> Dict[str, T]:
        if self._plugins is None:
            self._plugins = {}
            self._require_errors = {}
            self._errors = {}
            for name, entry in self.entry_points().items():
                try:
                    entry.require()
                except Exception as e:
                    self._require_errors[name] = e
                try:
                    self._plugins[name] = entry.resolve()
                except Exception as e:
                    self._errors[name] = e
        return self._plugins

    def errors(self) -> Dict[str, Exception]:
        self.plugins()
        return self._errors

    def require_errors(self) -> Dict[str, Exception]:
        self.plugins()
        return self._require_errors

    def entry_points(self) -> Dict[str, pkg_resources.EntryPoint]:
        if self._entry_points is None:
            self._entry_points = {
                e.name: e for e in pkg_resources.iter_entry_points(
                    self.identifier)}
        return self._entry_points
