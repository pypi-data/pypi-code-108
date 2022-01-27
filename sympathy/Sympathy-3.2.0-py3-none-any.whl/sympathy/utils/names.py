# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
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


class Names:
    """
    Helper class to implement names for filebase.File subclasses.
    """
    def __init__(self, kind, fields, store_created=True):
        self._store_created = store_created
        kind = kind or 'cols'

        # Compat options.
        if kind == 'calc':
            fields = 'expr'
            kind = 'cols'
        elif kind == 'col_paths':
            fields = 'path'
            kind = 'cols'

        if fields is None:
            fields = 'name'

        self._kind = kind
        self._fields = fields

        self._is_multi_fields = True
        self._fields_list = self._fields
        if self._fields is None or isinstance(self._fields, str):
            self._is_multi_fields = False
            self._fields_list = [self._fields]

        self._items = []

    def fields(self):
        return self._fields_list

    def create_item(self, item=None):
        r = dict.fromkeys(self._fields_list)
        if item:
            r.update(item)
        if self._store_created:
            self._items.append(r)
        return r

    def updated_args(self):
        """
        Used primarily to get the updated arguments after applying compat
        options.
        """
        return self._kind, self._fields

    def item_to_result(self, data):
        res = data
        if not self._is_multi_fields:
            res = data[self._fields]
        return res

    def created_items_to_result_list(self):
        data_list = self._items
        res = data_list
        if not self._is_multi_fields:
            res = []
            for row in data_list:
                res.append(row[self._fields])
        return res


def names(kind, fields, store_created=True):
    return Names(kind, fields, store_created=True)
