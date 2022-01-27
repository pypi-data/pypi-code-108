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
"""HDF5 list."""
from . import dsgroup


class Hdf5List(dsgroup.Hdf5Group):
    """Abstraction of an HDF5-list."""
    def __init__(self, factory, **kwargs):
        super().__init__(factory, **kwargs)

    def read_with_type(self, index, type_cls):
        """Reads element at index and returns it as a datasource."""
        try:
            group = self.group[str(index)]
            return self._create_item(type_cls, group)
        except TypeError:
            raise TypeError('Investigating:{} from:{}'.format(
                repr(index), repr(self.group.name)))

    def write_with_type(self, index, value, type_cls):
        """Write group at index and returns the group as a datasource."""
        key_group = self._group_get_or_create(str(index))
        return self._create_item(type_cls, key_group)

    def link_with(self, index, value):
        key = str(index)

        if key in self.group:
            assert(False)
        else:
            self.group[key] = value.link()

    def size(self):
        """Return the list size."""
        return len(self.group)
