# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
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
Utility functionality for working with the fundamental data types in sympathy.
"""
import collections


import numpy as np
import datetime
import re


_bool_dtype = np.dtype(bool)
_complex_dtype = np.dtype(complex)
_datetime_dtype = np.dtype('datetime64[us]')
_date_dtype = np.dtype('datetime64[D]')
_timedelta_dtype = np.dtype('timedelta64[us]')


_KINDS = {'b': 'bool',
          'i': 'integer',
          'u': 'integer',
          'f': 'float',
          'c': 'complex',
          'S': 'bytes',
          'U': 'text',
          'M': 'datetime',
          'm': 'timedelta'}

_DTYPES = collections.OrderedDict([
    ('bool', _bool_dtype),
    ('bytes', np.dtype(bytes)),
    ('complex', _complex_dtype),
    ('datetime', _datetime_dtype),
    ('float', np.dtype(float)),
    ('integer', np.dtype(int)),
    ('text', np.dtype(str)),
    ('timedelta', _timedelta_dtype)])

_DESCRIPTIONS = collections.OrderedDict([
    ('bool', 'Boolean'),
    ('bytes', 'Bytes'),
    ('complex', 'Complex'),
    ('datetime', 'Date & time'),
    ('float', 'Floating point'),
    ('integer', 'Integer'),
    ('text', 'Text'),
    ('timedelta', 'Time delta')])


def typename_from_kind(kind):
    """Return typename assocated with kind."""
    return _KINDS[kind]


def dtype(name):
    """
    Return dtype from name.

    Supports typenames, our special interpretation for some numpy.dtype.kinds,
    as well as regular numpy.dtype strings.
    """
    if name in _KINDS:
        return _DTYPES[_KINDS[name]]
    elif name in _DTYPES:
        return _DTYPES[name]
    else:
        return np.dtype(name)


def desc(name):
    return _DESCRIPTIONS[name]


def typenames():
    """Return list of all handled typenames."""
    return list(_DTYPES.keys())


_str_to_bool = {}
_str_to_bool.update(dict.fromkeys(['True', 'true', '1'], True))
_str_to_bool.update(dict.fromkeys(['False', 'false', '0'], False))

_timedelta_amount_unit = (
    '(?P<amount>[0-9]+(?:.[0-9])?) *'
    '(?P<unit>days?|d|hours?|h|minutes?|m|seconds?|s)')
_timedelta_amount_unit_re = re.compile(_timedelta_amount_unit,
                                       flags=re.IGNORECASE)
_timedelta_amount_unit_match_re = re.compile(
    '^(?:[ \t]*{})+$'.format(_timedelta_amount_unit),
    flags=re.IGNORECASE)
_str_to_timedelta_amount = {
    'd': 'days', 'h': 'hours', 'm': 'minutes', 's': 'seconds'}


def _str_to_timedelta(value):
    if _timedelta_amount_unit_match_re.match(value) is not None:
        kwargs = {}
        for v, k in _timedelta_amount_unit_re.findall(value):
            kwargs[_str_to_timedelta_amount[k[:1].lower()]] = float(v)
        return datetime.timedelta(**kwargs)


def numpy_dtype_factory_for_dtype(dtype):
    """Return dtype constructor for input dtype."""
    kind = dtype.kind
    if kind in ['U', 'S']:
        # Special case handling for string types, when using the type to build
        # new strings, being constrained to the original length can be
        # problematic.
        dtype = np.dtype(kind)
    return dtype


def _same_kind(*dtypes):
    kinds = [d.kind for d in dtypes]
    len_kinds = len(kinds)
    return len_kinds == 0 or kinds.count(kinds[0]) == len_kinds


def numpy_dtype_factory_for_dtypes(dtype1, dtype2):
    """
    Return maximum dtype constructor for input dtypes.

    Parameters
    ----------
    dtype1: dtype or dtype specifier.
        First type.

    dtype2: dtype or dtype specifier
        Second type, should be of the same kind as `dtype`.

    Examples
    --------
    >>> numpy_dtype_factory_for_dtypes('U1', 'U2')
    dtype('U2')
    >>> numpy_dtype_factory_for_dtypes('int32', 'int16')
    dtype('int32')
    """
    res = np.promote_types(dtype1, dtype2)
    if not _same_kind(dtype1, dtype2, res):
        raise ValueError('Requires the same kind of dtypes.')
    return res


def numpy_value_from_dtype_str(dtype, value):
    """
    Return numpy scalar parsed from string.
    """
    new_value = None
    if dtype == _bool_dtype:
        # Special case handling for building bool from string.
        new_value = _str_to_bool.get(value)
    elif dtype == _timedelta_dtype:
        new_value = _str_to_timedelta(value)
    elif dtype == _complex_dtype:
        new_value = complex(value.replace(' ', ''))
    else:
        new_value = value

    if new_value is None:
        raise ValueError('"{}" is not a suitable literal for {}'.format(
            value, _KINDS[dtype.kind]))
    try:
        return dtype.type(new_value)
    except Exception:
        raise ValueError('"{}" is not a suitable literal for {}'.format(
            value, _KINDS[dtype.kind]))


def python_value_from_numpy_value(value):
    """Return python scalar from numpy scalar."""
    return value.tolist()


def numpy_value_from_python_value(value):
    """Return numpy scalar from python scalar."""
    res = None
    if isinstance(value, datetime.datetime):
        # Datetime.
        res = _datetime_dtype.type(value)
    elif isinstance(value, datetime.date):
        # Date.
        res = _date_dtype.type(value)
    elif isinstance(value, datetime.timedelta):
        # Timedelta.
        return _timedelta_dtype.type(value)
    else:
        res = np.dtype(type(value)).type(value)
    return res
