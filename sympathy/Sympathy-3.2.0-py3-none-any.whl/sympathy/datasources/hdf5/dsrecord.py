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
"""HDF5 record."""
from . import dsgroup


class Hdf5Record(dsgroup.Hdf5Group):
    """Abstraction of an HDF5-list."""
    def __init__(self, factory, **kwargs):
        super().__init__(factory, **kwargs)

    def read_with_type(self, key, type_cls):
        """Reads element at key and returns it as a datasource."""
        key = dsgroup.replace_slash(key)
        group = self.group[key]
        try:
            return self._create_item(type_cls, group)
        except TypeError:
            raise TypeError('Investigating:{} from:{}'.format(
                repr(key), repr(self.group.name)))

    def write_with_type(self, key, value, type_cls):
        """Write group at key and returns the group as a datasource."""
        key_group = self._group_get_or_create(dsgroup.replace_slash(key))
        return self._create_item(type_cls, key_group)

    def link_with(self, key, value):
        key = dsgroup.replace_slash(key)

        if key in self.group:
            assert(False)
        else:
            self.group[key] = value.link()

    def keys(self):
        """Return the record keys"""
        return [dsgroup.restore_slash(key) for key in self.group.keys()]
