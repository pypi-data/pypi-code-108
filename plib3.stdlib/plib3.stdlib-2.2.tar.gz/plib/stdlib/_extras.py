#!/usr/bin/env python3
"""
Module _EXTRAS -- Enhancing the builtin namespace
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from operator import mul as _mul
from functools import reduce
from collections import deque as _deque


def first(iterable, default=None):
    """Return first item in iterable, or default if empty.
    """
    for item in iterable:
        return item
    return default


def inverted(mapping, keylist=None):
    """Return a mapping that is the inverse of the given mapping.
    
    The optional argument ``keylist`` limits the keys that are inverted.
    """
    if keylist is not None:
        return mapping.__class__((mapping[key], key)
                                 for key in keylist)
    return mapping.__class__((value, key)
                             for key, value in mapping.items())


def last(iterable, default=None, deque=_deque):
    """Return last item in iterable, or default if empty.
    """
    q = deque(iterable, maxlen=1)  # consumes iterable at C speed
    return q[0] if q else default


def prod(iterable, mul=_mul):
    """Return the product of all items in iterable.
    """
    return reduce(mul, iterable, 1)


def type_from_name(name):
    """Return type object corresponding to ``name``.
    
    Currently searches only the built-in types. No checking is done to
    make sure the returned object is actually a type.
    """
    import builtins
    try:
        return getattr(builtins, name)
    except AttributeError:
        raise ValueError("no type corresponding to {}".format(name))
