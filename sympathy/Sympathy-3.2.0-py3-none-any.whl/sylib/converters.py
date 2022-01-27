# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017, Combine Control Systems AB
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
With the considered node it is possible to convert the data types of a number
of selected columns in the incoming Table. In general, the columns in the
internal :ref:`Table` type can have the same data types that exist for numpy
arrays, except for numpy object type. For this node the list of available data
types to convert to is restricted.

The following data types are available for conversion:
    - binary
    - bool
    - datetime (UTC or naive)
    - float
    - integer
    - text


Converting strings to datetimes
-------------------------------
Converting a str/unicode column to datetime might require some extra thought if
the strings include time-zone information. The datetimes stored by Sympathy
have no time zone information (due to limitations in the underlying data
libraries), but Sympathy is able to use the time-zone information when creating
the datetime columns. This can be done in two different ways, which we call
"UTC" and "naive".

datetime (UTC)
##############
The option *datetime (UTC)* will calculate the UTC-time corresponding to each
datetime in the input column. This is especially useful when your data contains
datetimes from different time zones (a common reason for this is daylight
savings time), but when looking in the viewer, exports etc. the datetimes will
not be the same as in the input.

For example the string ``'2016-01-01T12:00:00+0100'`` will be stored as
``2016-01-01T11:00:00`` which is the corresponding UTC time.

There is currently no standard way of converting these UTC datetimes back to
the localized datetime strings with time-zone information.

datetime (naive)
################
The option *datetime (naive)* simply discards any time-zone information. This
corresponds pretty well to how we "naively" think of time when looking at a
clock on the wall.

For example the string ``'2016-01-01T12:00:00+0100'`` will be stored as
``2016-01-01T12:00:00``.

Text vs. binary
---------------
Text data is a string of arbitrary characters from any writing system. Binary
data on the other hand is a series of bytes as they would be stored in a
computer. Text data can be converted to binary data and vice versa by choosing
one of several different character encodings. The character encoding maps the
characters onto series of bytes, but many encodings only support some subset of
all the different writing systems.

This node currently only supports the ASCII encoding, which means that only the
letters a-z (lower and upper case), as well as digits and a limited number of
punctuation characters can be converted. Trying to convert a string with any
other characters will lead to errors.
"""
import pytz
import dateutil.parser
from collections import defaultdict
import numpy as np

from sympathy.api import qt2 as qt_compat
from sympathy.api import exceptions
from sympathy.api import dtypes
from sympathy.api import masked
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')


def _binary_repr(text):
    # repr will show printable ascii characters as usual but will
    # replace any non-ascii or non-printable characters with an escape
    # sequence. The slice removes the quotes added by repr.
    return repr(text)[2:-1]


def _matplotlib_dates():
    from matplotlib import dates as _mpl_dates
    return _mpl_dates


def _str_to_datetime_utc(x, replace=False):
    try:
        dt = dateutil.parser.parse(x)
    except ValueError:
        raise exceptions.SyDataError(
            '"{}" is not a supported time format.'.format(x))

    if dt.tzinfo is None:
        res = np.datetime64(pytz.UTC.localize(dt))
    elif replace:
        res = np.datetime64(dt.replace(tzinfo=pytz.UTC))
    else:
        res = np.datetime64(dt)
    return res


def vectornice(column, func, dtype=None):
    dtype = dtype or func
    if len(column) == 0:
        return np.array([], dtype=dtype)

    if isinstance(column, np.ma.MaskedArray):
        # Vectorize does not seem to work well with masked arrays.  In part
        # since it applies the operation to the masked values, but also because
        # it, in some cases (no repro), can end up with unreasonable
        # fill_values.
        fill_value = np.ma.masked_array([], dtype=dtype).fill_value
        res = np.ma.masked_array(
            data=[func(d) if not m else fill_value
                  for d, m in zip(column.data, column.mask)],
            mask=column.mask, dtype=dtype)
    else:
        res = np.vectorize(func)(column)
    return res


def _str_to_datetime_naive(x):
    return _str_to_datetime_utc(x, replace=True)


def to_string(column):
    if column.dtype.kind == 'S':
        return column
    try:
        return vectornice(
            column, lambda x: str(x).encode('ascii'), bytes)
    except UnicodeEncodeError as e:
        raise exceptions.SyDataError(
            'Character {} could not be converted using ASCII encoding.'.format(
                e.object[e.start:e.end]))


def to_unicode(column):
    if column.dtype.kind == 'S':
        try:
            return vectornice(
                column, lambda x: x.decode('ascii'), str)
        except UnicodeDecodeError as e:
            raise exceptions.SyDataError(
                'Byte {} could not be converted using ASCII encoding.'.format(
                    _binary_repr(e.object[e.start:e.end])))

    return vectornice(column, str)


def to_datetime_common(column):
    if column.dtype.kind == 'M':
        return column
    elif column.dtype.kind == 'f':
        return np.array([_matplotlib_dates().num2date(x)
                         for x in column.tolist()],
                        dtype='datetime64[us]')
    else:
        return None


def to_datetime_utc(column):
    res = to_datetime_common(column)
    if res is None:
        # Assuming string datetime.
        try:
            # Trying faster astype based method.
            res = masked.astype(column, dtype='datetime64[us]')
            if np.any(np.isnat(res)):
                res = None
        except ValueError:
            res = None

        if res is None:
            res = masked.astype(
                vectornice(column, _str_to_datetime_utc, 'datetime64[us]'),
                'datetime64[us]')
    return res


def to_datetime_naive(column):
    result = to_datetime_common(column)
    if result is not None:
        return result
    return masked.astype(
        vectornice(column, _str_to_datetime_naive, 'datetime64[us]'),
        'datetime64[us]')


def to_int(column):
    return masked.astype(column, np.int)


def atof(x):
    return np.float(x.replace(',', '.'))


def to_float(column):
    if column.dtype.kind == 'M':
        return np.array([_matplotlib_dates().date2num(x)
                         for x in column.tolist()])
    try:
        res = masked.astype(column, np.float)
    except ValueError:
        res = vectornice(column, atof, np.float)
    return res


def to_bool(column):
    col = np.greater_equal(column, 1)
    if not isinstance(col, np.ndarray):
        # greater_equal can return NotImplementedType value.
        raise exceptions.SyDataError(
            'Conversion to bool from {} is not a supported.'.format(
                dtypes.typename_from_kind(column.dtype.kind)))
    return masked.astype(col, np.bool)


TYPE_NAMES = {'b': 'bool',
              'f': 'float',
              'i': 'integer',
              'S': 'binary',
              'U': 'text',
              'Mu': 'datetime (UTC)',
              'Mn': 'datetime (naive)'}

CONVERSION_OLD_TYPES_NEW_TYPES = {
    'bool': 'b',
    'float': 'f',
    'int': 'i',
    'str': 'S',
    'unicode': 'U',
    'datetime': 'Mu'}

CONVERSIONS = {'b': defaultdict(lambda: to_bool),
               'f': defaultdict(lambda: to_float),
               'i': defaultdict(lambda: to_int),
               'S': defaultdict(lambda: to_string),
               'U': defaultdict(lambda: to_unicode),
               'Mu': defaultdict(lambda: to_datetime_utc),
               'Mn': defaultdict(lambda: to_datetime_naive)}
