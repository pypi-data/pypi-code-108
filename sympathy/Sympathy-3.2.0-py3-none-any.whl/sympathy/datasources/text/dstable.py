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
"""Table Data source module."""
from collections import OrderedDict
import numpy as np
from . import dsgroup

NAME = '__sy_name__'


class TextTable(dsgroup.TextGroup):
    """Abstraction of an Text-table."""
    def __init__(self, factory, **kwargs):
        super().__init__(factory, **kwargs)
        self._data = self.group.setdefault('columns', OrderedDict())

    def read_column_attributes(self, column_name):
        return self._data[column_name][2]

    def write_column_attributes(self, column_name, properties):
        self._data[column_name][2] = dict(properties)

    def read_column(self, column_name, index=None):
        """Return np.rec.array with data from the given column name."""
        def bool_index(length, int_index):
            """Return bool index vector from int index vector."""
            result = np.zeros(length, dtype=bool)
            result[int_index] = True
            return result

        def indexed(column, index):
            if isinstance(index, list):
                index = bool_index(len(column), index)
            return column[index]

        # Construct the table as numpy array.
        column = np.array(*self._data[column_name][:2])
        return indexed(column, index) if index is not None else column

    def write_column(self, column_name, column):
        """
        Stores table in the Text file, at path,
        with data from the given table
        """
        # Write column data to the group.
        self._data[column_name] = [column.tolist(), str(column.dtype), {}]

    def write_started(self, number_of_rows, number_of_columns):
        pass

    def write_finished(self):
        pass

    def columns(self):
        """Return a list contaning the available column names."""
        return list(self._data)

    def column_type(self, column_name):
        return np.dtype(self._data[column_name][1])

    def number_of_rows(self):
        try:
            return len(next(self._data.itervalues())[0])
        except StopIteration:
            return 0

    def number_of_columns(self):
        return len(self._data)

    def write_name(self, name):
        self.group[NAME] = name

    def read_name(self):
        return self.group.get(NAME, '')

    def read_table_attributes(self):
        return dict(self.group.get('attributes', {}))

    def write_table_attributes(self, properties):
        if properties:
            self.group['attributes'] = dict(properties)
