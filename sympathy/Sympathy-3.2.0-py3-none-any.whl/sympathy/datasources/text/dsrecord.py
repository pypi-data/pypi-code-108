# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
"""Text record."""
from . import dsgroup


class TextRecord(dsgroup.TextGroup):
    """Abstraction of an Text-list."""
    def __init__(self, factory, **kwargs):
        super().__init__(factory, **kwargs)

    def read_with_type(self, key, type_cls):
        """Reads element at key and returns it as a datasource."""
        key = str(key)
        return self._create_item(type_cls, self.group['items'][key])

    def write_with_type(self, key, value, type_cls):
        """Write group at key and returns the group as a datasource."""
        key = str(key)
        key_group = self._group_get_or_create(key)
        return self._create_item(type_cls, key_group)

    def keys(self):
        """Return the record keys"""
        return self._get_items().keys()
