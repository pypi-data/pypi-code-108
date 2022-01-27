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
"""
API for working with the Table type.

Import this module like this::

    from sympathy.api import table

A Table with columns, where each column has a name and a data type.
All columns in the Table must always be of the same length.

Any node port with the *Table* type represents an object of this class.

Accessing the data
------------------
There are multiple APIs in the Table for adding and reading columns. The
simplest one is to use indexing with column names::

    >>> from sympathy.api import table
    >>> mytable = table.File()
    >>> mytable['foo'] = np.array([1,2,3])
    >>> print(mytable['foo'])
    [1 2 3]

It is also possible to convert between a Table and a pandas DataFrame
(:meth:`to_dataframe`, :meth:`from_dataframe`), a numpy recarray
(:meth:`to_recarray`, :meth:`from_recarray`), or a generator/list of rows
(:meth:`to_rows`, :meth:`from_rows`).

The size of the table can easily be found with the methods
:meth:`number_of_rows` and :meth:`number_of_columns`. The column names are
available via the method :meth:`column_names`.


.. _`table_attributes`:

Column and Table attributes
---------------------------
Both the Table itself and any of its columns can have attributes attached
to it. Attributes can be either scalar values or one-dimensional numpy arrays,
but not masked arrays. If the attribute value is :class:`bytes` (:class:`str`
in python 2) the value must contain only ASCII characters.

There is currently no support for storing datetimes or timedeltas in
attributes. As a workaround, you can convert the datetimes or timedeltas to
either string or floats and store those instead.

.. _`table_name_restrictions`:

Name restrictions
-----------------
Column names, attribute names and table names can be almost any unicode
strings. For column names an empty string or a single period (.) are not
allowed. For attribute names only the empty string is not allowed. The names of
table attributes must also not be of the format :obj:`__table_*__` since this
is reserved for storing attributes internal to the Sympathy platform.

If any of these names are set using :class:`bytes` (:class:`str` in python 2),
the name must contain only ASCII characters.



Class :class:`table.File`
-------------------------
.. autoclass:: File
   :members:
   :special-members:

Class :class:`table.Column`
---------------------------
.. autoclass:: Column
   :members:

"""
import itertools
import re
import csv

import numpy as np
import json

from .. types import sybase
from .. types import sylist
from .. platform import types
from .. types import exception as type_exc
from .. utils import filebase
from .. utils import complete
from .. utils.context import (deprecated_warn,
                              inherit_doc)
from .. utils import dtypes
from .. platform import exceptions as exc


RES_RE = re.compile('^__table_.*__$')
_TABLE_VERSION = '__table_version__'


def table_sql():
    """Avoid pre-loading table_sql."""
    from . import table_sql
    return table_sql


def _pandas():
    """
    Avoid pre-loading pandas.
    Pandas loads matplotlib taking loads of time.

    Matplotlib import has issues loading when python is installed on a unicode
    path causing unnecessary errors.
    """
    import pandas
    return pandas


def is_table(scheme, filename):
    """Return ``True`` if file at ``filename`` is represents a Table."""
    return File.is_type(filename, scheme)


def is_tables(scheme, filename):
    """
    Return ``True`` if file at ``filename`` is represents a list of Tables.
    """
    return FileList.is_type(filename, scheme)


def _reserved(name):
    return RES_RE.match(name)


def _reserved_attributes(attributes):
    return {k: v for k, v in attributes.items() if _reserved(k)}


def _ordinary_attributes(attributes):
    return {k: v for k, v in attributes.items() if not _reserved(k)}


@filebase.typeutil('sytypealias table = sytable')
@inherit_doc
class File(filebase.TypeAlias):
    """
    A Table with columns, where each column has a name and a data type.
    All columns in the Table must always be of the same length.
    """

    VERSION = '1.2'

    def __init__(self, mode=None, **kwargs):
        super(File, self).__init__(mode=mode, **kwargs)

        if mode != 'r':
            attributes = self._data.get_table_attributes()
            if _TABLE_VERSION not in attributes:
                attributes[_TABLE_VERSION] = self.VERSION
                self._data.set_table_attributes(attributes)
            else:
                self.version()

    def clear(self):
        """Clear the table. All columns and attributes will be removed."""
        for column_name in self.column_names():
            del self._data[column_name]
        self.set_table_attributes({})
        self.set_name(None)

    def version(self):
        """
        Return the version as a string.
        This is useful when loading existing files from disk.

        .. versionadded:: 1.2.5
        """
        return self._data.get_table_attributes().get(_TABLE_VERSION, '1.2')

    def column_names(self):
        """Return a list with the names of the table columns."""
        return self._data.columns()

    def column_type(self, column):
        """Return the dtype of column named ``column``."""
        return self._data.column_type(column)

    def number_of_rows(self):
        """Return the number of rows in the table."""
        return self._data.number_of_rows()

    def number_of_columns(self):
        """Return the number of columns in the table."""
        return self._data.number_of_columns()

    def is_empty(self):
        """Returns ``True`` if the table is empty."""
        return self._data.is_empty()

    @staticmethod
    def from_recarray(recarray):
        """
        Return a new :class:`table.File` with data from numpy.recarray object
        ``recarray``.
        """
        result = File()
        result._data.set(recarray)
        return result

    def to_recarray(self):
        """
        Return numpy.recarray object with the table content or None if there
        are no columns.
        """
        return self._data.value()

    @staticmethod
    def from_dataframe(dataframe):
        """
        Return a new :class:`table.File` with data from pandas dataframe
        ``dataframe``.
        """
        result = File()
        for key, value in iter(dataframe.items()):
            result.set_column_from_series(value, name=key)
        return result

    def to_dataframe(self):
        """Return pandas DataFrame object with all columns in table."""
        data = {}
        for name in self.column_names():
            arr = self[name]
            if isinstance(arr, np.ma.MaskedArray):
                kind = arr.dtype.kind
                mask = np.ma.getmaskarray(arr)
                arr = arr.data.astype('O', copy=True)
                arr[mask] = None
            data[name] = arr
        return _pandas().DataFrame(data)

    @staticmethod
    def from_matrix(column_names, matrix):
        """
        Return a new :class:`table.File` with data from numpy matrix
        ``matrix``. ``column_names`` should be a list of strings which are
        used to name the resulting columns.
        """
        result = File()
        matrix = matrix.T
        if len(matrix) != len(column_names):
            raise ValueError(
                "The number of columns in matrix is not the same as the "
                "number of column names.")
        for key, value in zip(column_names, matrix):
            result.set_column_from_array(
                key, np.squeeze(np.asarray(value), 0))
        return result

    def to_matrix(self):
        """Return numpy matrix with all the columns in the table."""
        return np.mat(
            [self.get_column_to_array(column)
             for column in self.column_names()]).T

    @staticmethod
    def _rows_to_csv(filename, rows, headers=None, encoding='UTF-8',
                     delimiter=';', quotechar='"'):

        # TODO(erik): copied from plugin_csv_exporter, why is it even needed?
        def encode_values(data_row, encoding):
            """
            Return a list of encoded strings with the values of the
            sequence data_row.

            The values in the sequences are converted to unicode first so if
            any values are already encoded strings, they must be encoded with
            'ascii' codec.
            """
            return [value.decode(encoding) if isinstance(value, bytes)
                    else str(value)
                    for value in data_row]

        f = open(filename, 'w', encoding=encoding, newline='')

        csv_writer = csv.writer(f,
                                delimiter=delimiter,
                                quotechar=quotechar,
                                doublequote=True,
                                quoting=csv.QUOTE_MINIMAL)
        with f:
            if headers:
                csv_writer.writerow(
                    encode_values(headers, encoding))

            if rows is not None:
                csv_writer.writerows(encode_values(row, encoding)
                                     for row in rows)

    def to_csv(self, filename, header=True, encoding='UTF-8', delimiter=';',
               quotechar='"'):
        """
        Save/Export table to filename.
        """
        headers = []
        if header:
            headers = self.column_names()

        self._rows_to_csv(filename, self.to_rows(), headers,
                          encoding=encoding,
                          delimiter=delimiter, quotechar=quotechar)


    @staticmethod
    def from_rows(column_names, rows, column_types=None):
        """
        Returns new :class:`table.File` with data from iterable rows and
        the specified column names.

        Parameters
        ----------

        column_names: [str]
            Used to name the resulting columns.
        rows: iterable
            Zero or more rows of cell values. Number of values should be the
            same for each row in the data.
        column_types: [str or np.dtype], optional
            Used to specify type for the resulting columns, required for
            columns that would contain only None values which are otherwise
            ignored.

        The lengths of column_names and column_types (when provided) should
        match the number of cell values for each row.

        Returns
        -------
        table.File

        """
        def tableiter(maxrows):
            rowiter = iter(rows)
            column_data = list(zip(*itertools.islice(rowiter, maxrows)))

            if column_data:
                while column_data:
                    column_table = File()
                    for key, value, type_ in zip(
                            column_names, column_data, column_types):
                        arr = np.array(value)
                        if arr.dtype.kind == 'O':
                            # For older numpy, otherwise, arr == None.
                            mask = np.equal(arr, None)
                            if np.all(mask):
                                if type_:
                                    arr = np.ma.masked_array(
                                        np.zeros(len(arr), dtype=type_), mask)
                                else:
                                    # No information about the actual type.
                                    # => silently ignoring it.
                                    arr = None
                            elif np.any(mask):
                                # Repeat the first non-masked value in all
                                # masked positions.
                                fill = arr[np.nonzero(~mask)[0][0]]
                                arr[mask] = fill
                                arr = np.ma.masked_array(
                                    arr.tolist(), mask, dtype=type_)
                            elif type_:
                                arr = np.array(arr, dtype=type_)

                        if arr is not None:
                            column_table.set_column_from_array(key, arr)

                    yield column_table
                    column_data = list(
                        zip(*itertools.islice(rowiter, maxrows)))
            else:
                column_table = File()
                void = np.array([], dtype=np.void)
                for key in column_names:
                    column_table.set_column_from_array(key, void)
                yield column_table

        # Set the size of the sub tables (in rows).
        # This will only be one row in the case where
        # number_of_columns >= maxcells.
        # Intended to limit memory use.
        maxcells = 2 ** 15
        number_of_columns = len(column_names)
        maxrows = maxcells // number_of_columns if number_of_columns else 1
        result = File()
        if column_types is None:
            column_types = itertools.repeat(None)

        result.vjoin(tableiter(maxrows), '', '', None, 0)
        return result

    def to_rows(self):
        """
        Return a generator over the table's rows.

        Each row will be represented as a tuple of values.
        """
        # Set the size of the sub tables (in rows).
        # This will only be one row in the case where
        # number_of_columns >= maxcells.
        # Intended to limit memory use.
        maxcells = 2 ** 15
        number_of_columns = self.number_of_columns()
        maxrows = maxcells // number_of_columns if number_of_columns else 1
        column_names = self.column_names()
        for i in range(0, self.number_of_rows(), maxrows):
            column_table = self[i: i + maxrows]
            for row in zip(*[column_table.get_column_to_array(key).tolist()
                             for key in column_names]):
                yield row

    def set_column_from_array(self, column_name, array, attributes=None):
        """
        Write numpy array to column named by column_name.
        If the column already exists it will be replaced.
        """
        try:
            self._data.set_column(column_name, array)
        except type_exc.DatasetTypeError:
            raise exc.SyColumnTypeError(
                'Input array contains unsupported objects')

        if attributes is not None:
            self.set_column_attributes(column_name, attributes)

    def get_column_to_array(self, column_name, index=None, kind='numpy'):
        """
        Return named column as an array.

        Return type is numpy.array when kind is 'numpy' (by default)
        and dask.array.Array when kind is 'dask'.

        Dask arrays can be used to reduce memory use in locked subflows by
        handling data more lazily.
        """
        return self._data.get_column(column_name, index, kind=kind)

    def _require_column(self, parameter, types=None, name=None):
        """
        Intended for internal use.
        """
        if name:
            pass
        elif parameter.type == 'list':
            name = parameter.selected
        elif parameter.type == 'string':
            name = parameter.value
        else:
            name = ''
            raise exc.SyConfigurationError(
                f'{parameter.label}: parameter must be text (string).')
        if not name:
            parameter._require()

        if not isinstance(name, str):
            raise exc.SyConfigurationError(
                f'{parameter.label}: (column {name}) must be text (string).')
        elif name not in self:
            raise exc.SyDataError(
                f'{parameter.label}: (column {name}) is missing in data.')

        column = self.get_column_to_array(name)
        dtype = column.dtype
        if types and dtype.kind not in types:
            try:
                desc = dtypes.desc(dtypes.typename_from_kind(dtype.kind))
            except KeyError:
                desc = str(dtype)
            raise exc.SyDataError(
                f'{parameter.label}: (column {name}) is of unsupported type, '
                f'{desc.lower()}.')
        return column

    def set_column_from_series(self, series, name=None):
        """
        Write pandas series to column named by `name`, if name is None
        series.name is used as name. The resulting name should not be None.

        If the column already exists it will be replaced.
        """

        def time_dtype(old_dtype):
            new_dtype = old_dtype
            if old_dtype.type == np.datetime64:
                new_dtype = 'datetime64[us]'
            elif old_dtype.type == np.timedelta64:
                new_dtype = 'timedelta64[us]'
            return new_dtype

        def general_dtype(old_dtype):
            dtype_kind = dtype.kind
            new_dtype = dtype
            if dtype_kind in ['S', 'U', 'f', 'i', 'u']:
                new_dtype = dtype_kind
            elif dtype_kind == 'c':
                new_dtype = 'complex'
            return new_dtype

        if name is None:
            name = series.name

        if name is None:
            raise Exception(
                'Series needs to have a name; assign series.name or '
                'supply name using the `name` argument')
        if series.dtype.kind == 'O':
            # Make a guess based on first value, mixed types are unsupported.
            valid = ~_pandas().isna(series).values
            all_valid = valid.all()
            if series.size == 0:
                value = np.nan
            elif not all_valid:
                i = valid.argmax()
                if valid[i]:
                    value = series.iat[i]
                else:
                    value = np.nan
            else:
                value = series.iat[0]

            dtype = dtypes.numpy_value_from_python_value(value).dtype
            dtype_kind = dtype.kind
            new_dtype = general_dtype(dtype)

            fill = np.nan
            # Numerics
            if dtype_kind == 'f':
                valid = ~np.equal(series.values, None)
                all_valid = valid.all()
            elif dtype_kind == 'c':
                fill = np.nan + 1j * np.nan
                valid = ~np.equal(series.values, None)
                all_valid = valid.all()
            else:
                fill = np.zeros(1, dtype)[0]
            series = series.fillna(fill)

            array = np.array(series.values, new_dtype)

            if not all_valid:
                array = np.ma.masked_array(array, ~valid)
        else:
            array = np.array(series.values, dtype=time_dtype(series.dtype))
        self.set_column_from_array(name, array)

    def get_column_to_series(self, column_name):
        """Return named column as pandas series."""
        return _pandas().Series(
            self._data.get_column(column_name), name=column_name, copy=True)

    def set_name(self, name):
        """Set table name. Use None to unset the name."""
        self._data.set_name(name)

    def get_name(self):
        """Return table name or None if name is not set."""
        return self._data.get_name()

    def get_column_attributes(self, column_name):
        """Return dictionary of attributes for column_name."""
        return self._data.get_column_attributes(column_name).get()

    def set_column_attributes(self, column_name, attributes):
        """
        Set dictionary of scalar attributes for column_name.

        Attribute values can be any numbers or strings.
        """
        self._data.get_column_attributes(column_name).set(attributes)

    def get_table_attributes(self):
        """Return dictionary of attributes for table."""
        return _ordinary_attributes(self._data.get_table_attributes())

    def set_table_attributes(self, attributes):
        """
        Set table attributes to those in dictionary attributes.

        Attribute values can be any numbers or strings. Replaces any old table
        attributes.

        Example::

            >>> from sympathy.api import table
            >>> mytable = table.File()
            >>> mytable.set_table_attributes(
            ...     {'Thou shall count to': 3,
            ...      'Ingredients': 'Spam'})
        """
        attributes = dict(attributes)
        reserved = _reserved_attributes(self._data.get_table_attributes())
        attributes.update(reserved)
        self._data.set_table_attributes(attributes)

    def get_attributes(self):
        """
        Get all table attributes and all column attributes.

        Returns a tuple where the first element contains all the table
        attributes and the second element contains all the column attributes.
        """
        return (self.get_table_attributes(),
                {column: self.get_column_attributes(column)
                 for column in self.column_names()})

    def set_attributes(self, attributes):
        """Set table attributes and column attrubutes at the same time.

        Input should be a tuple of dictionaries where the first element of the
        tuple contains the table attributes and the second element contains the
        column attributes.
        """
        if not (isinstance(attributes, tuple) or isinstance(attributes, list)):
            raise ValueError(
                "attributes must be either list or tuple not {}.".format(
                    type(attributes)))
        if len(attributes) != 2:
            raise ValueError("attributes must have exactly two elements.")

        self.set_table_attributes(attributes[0])
        for column in set(self.column_names()) & set(attributes[1].keys()):
            self.set_column_attributes(column, attributes[1][column])

    def update(self, other_table):
        """
        Updates the columns in the table with columns from other table keeping
        the old ones.

        If a column exists in both tables the one from other_table is used.
        Creates links where possible.
        """
        self._data.update(other_table._data)

    def update_column(self, column_name, other_table, other_name=None):
        """
        Updates a column from a column in another table.

        The column other_name from other_table will be copied into column_name.
        If column_name already exists it will be replaced.

        When other_name is not used, then column_name will be used instead.
        """
        if other_name is None:
            other_name = column_name

        self._data.update_column(
            column_name, other_table._data, other_name)

    def __getitem__(self, index):
        """
        :rtype: table.File

        Return a new :class:`table.File` object with a subset of the table
        data.

        This method fully supports both one- and two-dimensional single indices
        and slices.

        Examples::

            >>> from sympathy.api import table
            >>> mytable = table.File.from_rows(
            ...     ['a', 'b', 'c'],
            ...     [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            >>> mytable.to_dataframe()
               a  b  c
            0  1  2  3
            1  4  5  6
            2  7  8  9
            >>> mytable[1].to_dataframe()
               a  b  c
            0  4  5  6
            >>> mytable[:,1].to_dataframe()
               b
            0  2
            1  5
            2  8
            >>> mytable[1,1].to_dataframe()
               b
            0  5
            >>> mytable[:2,:2].to_dataframe()
               a  b
            0  1  2
            1  4  5
            >>> mytable[::2,::2].to_dataframe()
               a  c
            0  1  3
            1  7  9
            >>> mytable[::-1,:].to_dataframe()
               a  b  c
            0  7  8  9
            1  4  5  6
            2  1  2  3


        If the key (index) is a string, it is assumed to be a column name and
        that column array will be returned.
        """
        if isinstance(index, str):
            return self.get_column_to_array(index)
        else:
            return File(data=self._data[index])

    def __setitem__(self, index, other_table):
        """
        Update the values at index with the values from other_table.

        This method fully supports both one- and two-dimensional single indices
        and slices, but the dimensions of the slice must be the same as the
        dimensions of other_table.

        If the key (index) is a string, it is assumed to be a column name and
        the value (other_table) argument an array.
        """

        if isinstance(index, str):
            self.set_column_from_array(index, other_table)
        else:
            self._data[index] = other_table._data

    def __contains__(self, key):
        """
        Return True if table contains a column named key.

        Equivalent to :meth:`has_column`.
        """
        return self._data.has_column(key)

    def has_column(self, key):
        """
        Return True if table contains a column named key.

        .. versionadded:: 1.1.3
        """
        return self._data.has_column(key)

    def hjoin(self, other_table, mask=False, rename=False):
        """
        Add the columns from other_table.

        Analoguous to :meth:`update`.
        """
        sybase.hjoin(self._data, other_table._data, mask=mask, rename=rename)

    def vjoin(self, other_tables, input_index='', output_index='', fill=True,
              minimum_increment=1):
        """
        Add the rows from the other_tables at the end of this table.

        Parameters
        ----------
        other_tables: [table]
        input_index: str
                     Column name for specified index column (deprecated).
        output_index: str
                      Column name for output index column generated
        fill: bool or None
              When True, attempt to fill with NaN or a zero-like value.
              When False, discard columns not present in all other_tables.
              When None, mask output.
        minimum_increment: int
                           Index increment added for empty tables.

        Returns
        -------
        table

        """
        if input_index:
            deprecated_warn("vjoin with input index", "4.0.0")
        input_list = sylist(types.from_string('[sytable]'))
        for other_table in other_tables:
            input_list.append(other_table._data)
        try:
            sybase.vjoin(self._data, input_list, input_index, output_index,
                         fill, minimum_increment)
        except type_exc.DatasetTypeError:
            raise exc.SyColumnTypeError(
                'Input columns to stack have incompatible types')

    def vsplit(self, output_list, input_index, remove_fill):
        """Split the current table to a list of tables by rows."""
        temp_list = []
        sybase.vsplit(
            self._data, temp_list, input_index, remove_fill)
        for pair in temp_list:
            output_list.append(File(data=pair[1]))

    def source(self, other_table, shallow=False):
        self._data.source(other_table._data, shallow=False)

    def __copy__(self):
        obj = super(File, self).__copy__()
        obj._data = self._data.__copy__()
        return obj

    def __deepcopy__(self, memo=None):
        obj = super(File, self).__copy__()
        obj._data = self._data.__deepcopy__()
        return obj

    @classmethod
    def viewer(cls):
        from .. platform import table_viewer
        return table_viewer.TableViewer

    @classmethod
    def icon(cls):
        return 'ports/table.svg'

    @property
    def name(self):
        name = self._data.get_name()
        return name if name is not None else ''

    @name.setter
    def name(self, value):
        self.set_name(value)

    def names(self, kind=None, fields=None, **kwargs):
        """
        The names that can be automatically adjusted from a table.

        kind should be one of 'cols' (all column names), 'attrs' (all table
        attribute names), or 'name' (the table name).
        """
        names = filebase.names(kind, fields)
        kind, fields = names.updated_args()
        fields_list = names.fields()

        if kind == 'cols':
            for name in self.column_names():
                item = names.create_item()
                for f in fields_list:
                    if f == 'name':
                        item[f] = name
                    elif f == 'type':
                        item[f] = self.column_type(name)
                    elif f == 'expr':
                        item[f] = "[{}]".format(filebase.calc_quote(name))
                    elif f == 'path':
                        item[f] = [('[]', name)]

        elif kind == 'attrs':
            for name in self.attrs().keys():
                item = names.create_item()
                for f in fields_list:
                    if f == 'name':
                        item[f] = name
        elif kind == 'name':
            item = names.create_item()
            for f in fields_list:
                if f == 'name':
                    item[f] = name

        return names.created_items_to_result_list()

    def completions(self, **kwargs):
        def column_names(ctx):
            return self.column_names()

        def table_attrs(ctx):
            return self.attrs.keys()

        builder = complete.CompletionBuilder()
        builder.prop('attr').call(table_attrs)
        builder.prop('name')
        builder.prop('number_of_rows').call()
        builder.prop('number_of_columns').call()
        builder.prop('column_names').call()
        cols = builder.prop('col').call(column_names)
        cols.prop('data')
        cols.prop('attr')
        builder.getitem(column_names)
        return builder

    def attr(self, name):
        """Get the table's attribute with `name`."""
        attributes = _ordinary_attributes(self._data.get_table_attributes())
        return attributes.get(name, '')

    def set_attr(self, name, value):
        assert not _reserved(name)
        attributes = self._data.get_table_attributes()
        attributes[name] = value
        self.set_table_attributes(attributes)

    @property
    def attrs(self):
        """
        Return dictionary of attributes for table.

        .. versionadded:: 1.3.4
        """
        return self._data.get_table_attributes()

    def cols(self):
        """
        Get a list of all columns as :class:`Column` objects.

        .. versionadded:: 1.3.4
        """
        return [self.col(name) for name in self.column_names()]

    def col(self, name):
        """
        Get a :class:`Column` object for column with `name`.

        .. versionadded:: 1.3.4
        """
        return Column(name, self._data)

    def equal_to(self, other, col_order=True, col_attrs=True, tbl_names=True,
                 tbl_attrs=True, inexact_float=False, rel_tol=1e-05,
                 abs_tol=1e-08, raise_exc=False, exc_cls=AssertionError):
        def not_equal(exc_msg, *exc_args):
            if raise_exc:
                raise exc_cls(
                    exc_msg.format(*exc_args))
            return False

        def nan_equal_diff(column1, column2, normal_diff):
            # Need to special case NaN since it isn't equal to itself.
            nans1 = np.isnan(column1)
            nans2 = np.isnan(column2)
            no_nans = np.logical_not(np.logical_or(nans1, nans2))
            normal_diff = np.logical_and(normal_diff, no_nans)
            nan_diff = nans1 != nans2
            return np.logical_or(normal_diff, nan_diff)

        # Column names/order
        t1_cols = set(self.column_names())
        t2_cols = set(other.column_names())
        if t1_cols != t2_cols:
            only_in_a = t1_cols - t2_cols
            if only_in_a:
                return not_equal(
                    "Tables are not equal. Some columns only exist in "
                    "table A: {}", list(only_in_a))
            only_in_b = t2_cols - t1_cols
            if only_in_b:
                return not_equal(
                    "Tables are not equal. Some columns only exist in "
                    "table B: {}", list(only_in_b))

            # Should never happen.
            return not_equal(
                'Tables are not equal. Different column names.')
        if col_order:
            if self.column_names() != other.column_names():
                return not_equal(
                    'Tables are not equal. Different column order.')

        # Column data/attributes
        if self.number_of_rows() != other.number_of_rows():
            return not_equal(
                "Tables are not equal. Different number of rows.")
        for col_name in self.column_names():
            column1 = self.get_column_to_array(col_name)
            column2 = other.get_column_to_array(col_name)

            # Dtypes
            if column1.dtype.kind != column2.dtype.kind:
                return not_equal(
                    "Tables are not equal. Different column data type for "
                    "column '{}'.", col_name)

            # Masks
            if isinstance(column1, np.ma.MaskedArray):
                mask1 = column1.mask
                column1 = column1.compressed()
            else:
                mask1 = False
            if isinstance(column2, np.ma.MaskedArray):
                mask2 = column2.mask
                column2 = column2.compressed()
            else:
                mask2 = False
            if np.any(mask1 != mask2):
                return not_equal(
                    "Tables are not equal. Different masks for column "
                    "'{}'.", col_name)

            if inexact_float and column1.dtype.kind == 'f':
                normal_diff = np.logical_not(np.isclose(
                    column1, column2, rel_tol, abs_tol, equal_nan=True))
            else:
                normal_diff = (column1 != column2)

            if column1.dtype.kind == 'f':
                diff = nan_equal_diff(column1, column2, normal_diff)
            elif column1.dtype.kind == 'c':
                diff = np.logical_or(
                    nan_equal_diff(column1.real, column2.real, normal_diff),
                    nan_equal_diff(column1.imag, column2.imag, normal_diff))
            else:
                diff = normal_diff

            if diff.any():
                return not_equal(
                    "Tables are not equal. "
                    "Different values in column '{}' "
                    "(first difference at row {}).",
                        col_name, np.flatnonzero(diff)[0])
            if col_attrs:
                if (self.get_column_attributes(col_name) !=
                        other.get_column_attributes(col_name)):
                    return not_equal(
                        "Tables are not equal. Different "
                        "attributes for column '{}'.", col_name)

        # Table name/attributes
        if tbl_names:
            if self.name != other.name:
                return not_equal(
                    'Tables are not equal. Different table names.')
        if tbl_attrs:
            if (dict(self.get_table_attributes()) !=
                    dict(other.get_table_attributes())):
                return not_equal(
                    'Tables are not equal. Different table attributes.')
        return True


@inherit_doc
class FileList(filebase.FileListBase):
    """
    FileList has been changed and is now just a function which creates
    generators to sybase types.

    Old documentation follows:

    The :class:`FileList` class is used when working with lists of Tables.

    The main interfaces in :class:`FileList` are indexing or iterating for
    reading (see the :meth:`__getitem__()` method) and the :meth:`append()`
    method for writing.
    """

    sytype = '[table]'
    scheme = 'hdf5'


class Column(object):
    """
    The :class:`Column` class provides a read-only interface to a column in a
    Table.
    """

    def __init__(self, name, parent_data):
        self._name = name
        self._data = parent_data

    @property
    def data(self):
        """
        The data of the column as a numpy array. Equivalent to calling
        :meth:`File.get_column_to_array`.
        """
        return self._data.get_column(self._name)

    @property
    def name(self):
        """The name of the column."""
        return self._name

    def attr(self, name):
        """Return the value of the column attribute ``name``."""
        return self._data.get_column_attributes(self._name).get_attribute(name)

    @property
    def attrs(self):
        """A dictionary of all column attributes of this column."""
        return self._data.get_column_attributes(self._name).get()
