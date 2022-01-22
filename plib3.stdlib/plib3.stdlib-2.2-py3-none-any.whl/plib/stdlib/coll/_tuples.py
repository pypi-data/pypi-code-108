#! /usr/bin/env python3
"""
Module _TUPLES -- Alternate named tuple implementations
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

An alternate ``namedtuple`` implementation that does not
use a template and so is not vulnerable to template
injection attacks, and an enhanced ``typed_namedtuple``
that coerces arguments to specified types.
"""

import sys
from collections import OrderedDict
from operator import itemgetter

from ._names import process_names, process_specs

__all__ = [
    'namedtuple',
    'typed_namedtuple'
]


def _make_attrs(typename, field_names, rename):
    
    def _make(cls, iterable):
        result = tuple.__new__(cls, iterable)
        if len(result) != len(cls._fields):
            raise TypeError("Expected {:d} arguments, got {:d}".format(len(cls._fields), len(result)))
        return result
    
    _make.__doc__ = "Make a new {typename} object from a sequence or iterable".format(**locals())
    
    def _repr(self):
        """Return a nicely formatted representation string"""
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join('{}={!r}'.format(*args) for args in zip(self._fields, self))
        )
    
    _repr.__name__ = '__repr__'
    
    def _asdict(self):
        """Return a new OrderedDict which maps field names to their values"""
        return OrderedDict(zip(self._fields, self))
    
    def _fromdict(cls, d, plain=False):
        args = (d[f] for f in cls._fields)
        return tuple(args) if plain else cls(*args)
    
    def _replace(self, **kwds):
        result = self._make(map(kwds.pop, self._fields, self))
        if kwds:
            raise ValueError('Got unexpected field names: {!r}'.format(list(kwds)))
        return result
    
    _replace.__doc__ = "Return a new {typename} object replacing specified fields with new values".format(**locals())
    
    def _getnewargs(self):
        """Return self as a plain tuple. Used by copy and pickle."""
        return tuple(self)
    
    _getnewargs.__name__ = '__getnewargs__'
    
    attrs = {
        '__slots__': (),
        '_fields': tuple(field_names),
        '_make': classmethod(_make),
        'from_iterable': classmethod(_make),
        'from_dict': classmethod(_fromdict),
        '__repr__': _repr,
        '_asdict': _asdict,
        '__dict__': property(_asdict),
        '_replace': _replace,
        '__getnewargs__': _getnewargs
    }
    
    for i, field_name in enumerate(field_names):
        attrs.update({
            field_name: property(itemgetter(i), doc="Alias for field number {:d}".format(i))
        })
    
    return attrs


def _check_args(cls, args, kwds):
    sentinel = object()
    args = args + tuple(kwds.pop(key, sentinel) for key in cls._fields[len(args):])
    assert sentinel not in args
    assert not kwds
    assert len(args) == len(cls._fields)
    return args


def _make_tuple(typename, attrs, _doc, _new):
    
    _new.__name__ = '__new__'
    _new.__doc__ = "Create new instance of {}".format(_doc)
    
    attrs.update({
        '__new__': _new,
        '__doc__': _doc
    })
    
    result = type(tuple)(typename, (tuple,), attrs)
    try:
        result.__module__ = sys._getframe(2).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass
    return result


def namedtuple(typename, field_names, rename=False):
    """Returns a new subclass of tuple with named fields.

    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessable by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> p1 = Point.from_dict(d)
    >>> p1 == p
    True
    >>> type(p1)
    <class 'plib.stdlib.coll._tuples.Point'>
    >>> p2 = Point.from_dict(d, plain=True)
    >>> p2 == p
    True
    >>> type(p2)
    <class 'tuple'>
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # like str.replace() but targets named fields
    Point(x=100, y=22)
    >>> Test = namedtuple('if', "ok")
    Traceback (most recent call last):
     ...
    ValueError: Type names and field names cannot be a keyword: 'if'
    >>> Test = namedtuple('Test', "ok if")
    Traceback (most recent call last):
     ...
    ValueError: Type names and field names cannot be a keyword: 'if'
    >>> Test = namedtuple('Test', "ok if", rename=True)
    >>> Test._fields
    ('ok', '_1')
    """
    
    field_names, _doc = process_names(typename, field_names, rename)
    
    attrs = _make_attrs(typename, field_names, rename)
    
    def _new(cls, *args, **kwds):
        args = _check_args(cls, args, kwds)
        return tuple.__new__(cls, args)
    
    return _make_tuple(typename, attrs, _doc, _new)


def typed_namedtuple(typename, fieldspecs, rename=False):
    """Returns a new subclass of tuple with named, typed fields.
    
    >>> Point = typed_namedtuple('Point', 'x int, y int')
    >>> Point.__doc__        # docstring for the new class
    'Point(x <int>, y <int>)'
    >>> p = Point(11, y=22)  # instantiate with positional args or keywords
    >>> p[0] + p[1]          # indexable like a plain tuple
    33
    >>> x, y = p             # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y            # fields also accessible by name
    33
    >>> d = p._asdict()      # convert to a dictionary
    >>> d['x']
    11
    >>> p1 = Point.from_dict(d)
    >>> p1 == p
    True
    >>> type(p1)
    <class 'plib.stdlib.coll._tuples.Point'>
    >>> p2 = Point.from_dict(d, plain=True)
    >>> p2 == p
    True
    >>> type(p2)
    <class 'tuple'>
    >>> Point(**d)           # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)    # like str.replace() but targets named fields
    Point(x=100, y=22)
    >>> p = Point(11, '22')  # type conversion done on arguments
    >>> all(isinstance(p[i], int) for i in range(len(p)))
    True
    >>> x, y = p
    >>> x, y
    (11, 22)
    >>> p = Point(11, 'x')   # invalid arguments raise exception
    Traceback (most recent call last):
     ...
    ValueError: invalid literal for int() with base 10: 'x'
    >>> Test = typed_namedtuple('if', "ok int")
    Traceback (most recent call last):
     ...
    ValueError: Type names and field names cannot be a keyword: 'if'
    >>> Test = typed_namedtuple('Test', "ok int if int")
    Traceback (most recent call last):
     ...
    ValueError: Type names and field names cannot be a keyword: 'if'
    >>> Test = typed_namedtuple('Test', "ok int if int", rename=True)
    >>> Test._fields
    ('ok', '_1')
    >>> Test._fieldtypes
    (<class 'int'>, <class 'int'>)
    >>> Test._fieldspecs
    (('ok', <class 'int'>), ('_1', <class 'int'>))
    >>> Test = typed_namedtuple('Test', [('f1', int), ('f2', int)])
    >>> Test._fieldspecs
    (('f1', <class 'int'>), ('f2', <class 'int'>))
    >>> Test = typed_namedtuple('Test', ['f1', int, 'f2', int])
    >>> Test._fieldspecs
    (('f1', <class 'int'>), ('f2', <class 'int'>))
    >>> Test = typed_namedtuple('Test', ['f1 int', 'f2 int'])
    >>> Test._fieldspecs
    (('f1', <class 'int'>), ('f2', <class 'int'>))
    """
    
    fieldspecs, field_names, field_types, field_specs, _doc = process_specs(typename, fieldspecs, rename)
    
    attrs = _make_attrs(typename, field_names, rename)
    attrs.update({
        '_fieldtypes': tuple(field_types),
        '_fieldspecs': tuple(field_specs)
    })
    
    def _new(cls, *args, **kwds):
        args = _check_args(cls, args, kwds)
        return tuple.__new__(cls, tuple(cls._fieldtypes[i](item) for i, item in enumerate(args)))
    
    return _make_tuple(typename, attrs, _doc, _new)


if __name__ == '__main__':
    ### DOCTESTS
    
    __name__ = 'plib.stdlib.coll._tuples'  # hack to emulate how doctests are run from master test suite
    
    import doctest
    results = doctest.testmod()
    if verbose:
        TestResults = typed_namedtuple('TestResults', 'failed int attempted int')
        print(TestResults(*results))
