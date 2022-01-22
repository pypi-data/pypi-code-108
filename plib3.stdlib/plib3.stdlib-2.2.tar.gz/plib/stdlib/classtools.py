#!/usr/bin/env python3
"""
Module CLASSTOOLS -- Utilities for Python Classes
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains some helpful utilities for working
with Python classes. It currently provides:

first_subclass -- returns first attribute of an object that
    is a subclass of a given class

first_instance -- returns first attribute of an object that
    is an instance of a given class

    >>> class Test(object):
    ...     pass
    ...
    >>> class Test1(Test):
    ...     pass
    ...
    >>> t = Test()
    >>> t1 = Test1()
    >>> t.test = Test
    >>> first_subclass(t, Test) is None
    True
    >>> first_subclass(t, Test, allow_cls=True) is Test
    True
    >>> first_subclass(t, Test1) is None
    True
    >>> first_subclass(t, Test1, allow_cls=True) is None
    True
    >>> t.test1 = Test1
    >>> first_subclass(t, Test) is Test1
    True
    >>> first_subclass(t, Test, allow_cls=True, key=lambda x: x.__name__) is Test
    True
    >>> t.t = t
    >>> first_instance(t, Test) is t
    True
    >>> first_instance(t, Test1) is None
    True
    >>> t.t1 = t1
    >>> first_instance(t, Test1) is t1
    True
    >>> first_instance(t, Test, key=lambda x: x.__class__.__name__) is t
    True

These are fun illustrations of how Python's new-style object system bootstraps itself...

    >>> t2 = Test()
    >>> t2.o = object
    >>> t2.t = type
    >>> first_subclass(t2, object) is type
    True
    >>> first_subclass(t2, object, allow_cls=True, key=lambda x: x.__name__) is object
    True
    >>> first_subclass(t2, type) is None
    True
    >>> first_subclass(t2, type, allow_cls=True) is type
    True
    >>> first_instance(t2, object) is type
    True
    >>> first_instance(t2, object, allow_obj=True, key=lambda x: x.__name__) is object
    True
    >>> first_instance(t2, type) is object
    True
    >>> first_instance(t2, type, allow_obj=True, key=lambda x: x.__name__, reverse=True) is type
    True

recurselist, recursedict -- when you have a class field that's
    a container, these functions provide a way of combining all
    the values in your class's MRO, so you don't have to repeat
    them in derived classes.

Singleton -- class that only allows a single instance.
"""

import types

from plib.stdlib.builtins import first


def _vars(o, key, reverse):
    v = vars(o).values()
    if key is not None:
        return sorted(v, key=key, reverse=reverse)
    return v


def first_subclass(o, c, allow_cls=False, key=None, reverse=False):
    """Return first object in ``o`` that is a subclass of ``c``.
    
    If ``allow_cls`` is true, ``c`` counts as a subclass of
    itself (this is the normal Python behavior, but for most
    use cases of this function it is not desired, so it is
    not the default here).
    
    If ``key`` is not None, it must be a one-argument callable
    that is used as a sort key for the search. (By default the
    search is not sorted; for many use cases, only one matching
    item is expected anyway, so the search order is immaterial.)
    The ``reverse`` keyword reverses the sort order.
    """
    return first(
        obj for obj in _vars(o, key, reverse)
        if (allow_cls or (obj is not c))
        and isinstance(obj, type)
        and issubclass(obj, c)
    )


def first_instance(o, c, allow_obj=False, key=None, reverse=False):
    """Return first object in ``o`` that is an instance of ``c``.
    
    If ``allow_obj`` is true, ``c`` can be an instance of
    itself (this is only true for a few specialized objects in
    Python as shipped, but there may be funky use cases where
    other objects could satisfy it).
    
    If ``key`` is not None, it must be a one-argument callable
    that is used as a sort key for the search. (By default the
    search is not sorted; for many use cases, only one matching
    item is expected anyway, so the search order is immaterial.)
    The ``reverse`` keyword reverses the sort order.
    """
    return first(
        obj for obj in _vars(o, key, reverse)
        if (allow_obj or (obj is not c))
        and isinstance(obj, c)
    )


def _recurse(klass, name, result, methodname):
    method = getattr(result, methodname)
    for c in klass.__mro__:
        if name in c.__dict__:
            obj = c.__dict__[name]
            if obj:
                method(obj)
    return result


def recurselist(klass, name):
    """
    Recurses through mro of klass, assuming that where
    the class attribute name is found, it is a list;
    returns a list concatenating all of them.
    """
    return _recurse(klass, name, [], 'extend')


def recursedict(klass, name):
    """
    Recurses through mro of klass, assuming that where
    the class attribute name is found, it is a dict;
    returns a dict combining all of them.
    """
    return _recurse(klass, name, {}, 'update')


class Singleton(object):
    """Each subclass of this class can have only a single instance.
    
    (Taken from Guido's new-style class intro essay.)
    """
    
    def __new__(cls, *args, **kwds):
        """Only create an instance if it isn't already there.
        """
        
        inst = cls.__dict__.get("__inst__")
        if inst is None:
            cls.__inst__ = inst = object.__new__(cls)
            inst._init(*args, **kwds)
        return inst
    
    def _init(self, *args, **kwds):
        """Override this to do customized initialization.
        
        (This method will only be called once, whereas __init__ will
        be called each time the class constructor is called).
        """
        pass


if __name__ == '__main__':
    import doctest
    doctest.testmod()
