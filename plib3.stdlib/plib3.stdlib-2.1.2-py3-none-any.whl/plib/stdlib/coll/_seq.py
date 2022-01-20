#!/usr/bin/env python3
"""
Module _SEQ -- Enhanced sequence classes
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``namedsequence`` and ``typed_namedsequence``
classes, which are similar to their ``namedtuple`` counterparts
but have writable fields.
"""

import sys

from plib.stdlib.coll import abstractsequence

from ._names import process_names, process_specs

__all__ = [
    'namedsequence',
    'typed_namedsequence'
]


class _seq(abstractsequence):
    
    __slots__ = ('_items',)
    
    _fields = None
    
    def __init__(self, *items):
        # Storage for actual values; fill in with defaults so the
        # __setitem__ code will work when we populate from items
        # below (uses __getitem__ to validate indexes)
        self._items = ["" for f in self._fields]
        
        # Now we can populate from the given items
        if items:
            for index, item in enumerate(items):
                self[index] = item
    
    def __len__(self):
        return len(self._fields)
    
    def __getitem__(self, index):
        return self._items[index]
    
    def set_index(self, index, value):
        self._items[index] = value


def _make_prop(i, conv=None):
    def _get(self):
        return self._items[i]
    if conv:
        def _set(self, value):
            self._items[i] = conv(value)
    else:
        def _set(self, value):
            self._items[i] = value
    _doc = "Alias for field number {:d}".format(i)
    return property(_get, _set, doc=_doc)


def _make_seq(typename, attrs, _doc, cls):
    
    attrs.update({
        '__slots__': (),
        '__doc__': _doc
    })
    
    result = type(cls)(typename, (cls,), attrs)
    try:
        result.__module__ = sys._getframe(2).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass
    return result


def namedsequence(typename, field_names, rename=False):
    field_names, _doc = process_names(typename, field_names, rename)
    attrs = {
        '_fields': field_names
    }
    
    for i, field_name in enumerate(field_names):
        attrs.update({
            field_name: _make_prop(i)
        })
    
    return _make_seq(typename, attrs, _doc, _seq)


class _tseq(_seq):
    
    __slots__ = ()
    
    def set_index(self, index, value):
        # This ensures that we do type conversion
        setattr(self, self._fields[index], value)


def typed_namedsequence(typename, fieldspecs, rename=False):
    fieldspecs, field_names, field_types, field_specs, _doc = process_specs(typename, fieldspecs, rename)
    attrs = {
        '_fields': field_names,
        '_fieldtypes': field_types,
        '_fieldspecs': field_specs
    }
    
    for i, (field_name, field_type) in enumerate(field_specs):
        attrs.update({
            field_name: _make_prop(i, field_type)
        })
    
    return _make_seq(typename, attrs, _doc, _tseq)
