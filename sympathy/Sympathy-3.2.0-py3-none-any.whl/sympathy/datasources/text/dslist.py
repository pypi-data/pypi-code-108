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
"""Text list."""
from . import dsgroup


class TextList(dsgroup.TextGroup):
    """Abstraction of an Text-list."""
    def __init__(self, factory, **kwargs):
        super().__init__(factory, **kwargs)

    def read_with_type(self, index, type_cls):
        """Reads element at index and returns it as a datasource."""
        key = str(index)
        return self._create_item(type_cls, self.group['items'][key])

    def write_with_type(self, index, value, type_cls):
        """Write group at index and returns the group as a datasource."""
        key = str(index)
        key_group = self._group_get_or_create(key)
        return self._create_item(type_cls, key_group)

    def size(self):
        """Return the list size."""
        return len(self._get_items())
