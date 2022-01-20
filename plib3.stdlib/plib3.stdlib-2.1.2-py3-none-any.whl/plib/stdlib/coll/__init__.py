#!/usr/bin/env python3
"""
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains abstract base classes for
sequences and mappings that are built on the standard
Python collection ABCs, but with some additional features.

This sub-package also contains additional collection classes
with method names redefined for greater convenience. The
key desire here is to have the method names 'append' and
'next' refer to the methods that you *want* to call for
each collection to add and retrieve an item from the
"right" place (i.e., the "next" item for the given
collection). Thus:

``fifo`` -- a ``deque``; ``append`` adds to the end of the queue,
    ``nextitem`` retrieves from the start (i.e., ``popleft``).

``stack`` -- a ``list``; ``append`` adds to the end of the list,
    ``nextitem`` retrieves from the end as well (i.e., ``pop``).

Another collection class, ``frozendict``, is provided as a
dict-like equivalent to ``frozenset``.

There is also an alternate implementation of ``namedtuple``
provided, which does not use a class template. In addition,
an enhanced ``typed_namedtuple`` factory function is provided,
which adds specification of the types of each argument.

Finally, two "utility" collection classes are provided,
``AttrDict`` and ``AttrList``; these allow mapping values
or sequence items to be accessed via attribute names as
well as by the normal subscripting syntax.
"""

from collections import deque, OrderedDict
from collections.abc import MutableSequence, MutableMapping, MutableSet

from ._utils import *
from ._abc import *
from ._mixins import *
from ._bases import *
from ._tuples import *
from ._seq import *


def merge_dict(target, source):
    """Merges source into target
    
    Only updates keys not already in target.
    """
    
    merges = dict((key, value) for key, value in source.items()
                  if key not in target)
    target.update(merges)


def canonicalize_keys(mapping, keymap):
    """Force keys in mapping to canonical versions.
    
    ``keymap`` is a mapping of keys to their canonical versions.
    
    >>> test = {'a': 1, 'b': 2}
    >>> keymap = dict((key, key.upper()) for key in test)
    >>> sorted(canonicalize_keys(test, keymap).items())
    [('A', 1), ('B', 2)]
    
    """
    change_keys = mapping.keys() & keymap.keys()
    return type(mapping)(
        (keymap[key] if key in change_keys else key, mapping[key])
        for key in mapping
    )


class frozendict(basekeyed):
    """Dict equivalent of ``frozenset``.
    
    Constructor takes argument of dict or iterable of key-value pairs.
    
    >>> unfrozen = {'a': 1, 'b': 2}
    >>> f = frozendict(unfrozen)
    >>> f['a']
    1
    >>> f['a'] = 0
    Traceback (most recent call last):
    ...
    TypeError: 'frozendict' object does not support item assignment
    >>> sorted(f)
    ['a', 'b']
    >>> sorted(f.keys())
    ['a', 'b']
    >>> sorted(f.values())
    [1, 2]
    >>> sorted(f.items())
    [('a', 1), ('b', 2)]
    >>> f.get('b')
    2
    >>> f.get('c')
    >>> g = frozendict(f.items())
    >>> sorted(g)
    ['a', 'b']
    >>> sorted(g.keys())
    ['a', 'b']
    >>> sorted(g.values())
    [1, 2]
    >>> sorted(g.items())
    [('a', 1), ('b', 2)]
    >>> f == g
    True
    >>> d = {'f': f, 'g': g}
    >>> d['f'] == d['g']
    True
    >>> c = f.copy()
    >>> c == f
    True
    >>> sorted(c.items())
    [('a', 1), ('b', 2)]
    >>> k = f.fromkeys(f.keys())
    >>> sorted(k.items())
    [('a', None), ('b', None)]
    >>> kv = f.fromkeys(f.keys(), 0)
    >>> sorted(kv.items())
    [('a', 0), ('b', 0)]
    >>> g = frozendict({'c': 3, 'd': 4})
    >>> h = frozendict(f, g, e=5, f=6)
    >>> sorted(h.items())
    [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6)]
    >>> g = frozendict({'a': 3, 'b': 4})
    >>> h = frozendict(f, g, e=5, f=6)
    >>> sorted(h.items())
    [('a', 3), ('b', 4), ('e', 5), ('f', 6)]
    >>> g = frozendict({'e': 3, 'f': 4})
    >>> h = frozendict(f, g, e=5, f=6)
    >>> sorted(h.items())
    [('a', 1), ('b', 2), ('e', 5), ('f', 6)]
    """
    
    __slots__ = ('__dict', '__keys', '__repr', '__hash')
    
    def __init__(self, *args, **kwargs):
        self.__dict = OrderedDict()  # ensure that we preserve the ordering of keys
        for arg in args:
            self.__dict.update(arg)
        self.__dict.update(**kwargs)
        self.__keys = tuple(self.__dict)
        self.__repr = None
        self.__hash = None
    
    def __repr__(self):
        if not self.__repr:
            self.__repr = "frozendict({})".format(repr(list(self.__dict.items())))
        return self.__repr
    
    def __hash__(self):
        if not self.__hash:
            self.__hash = hash(tuple(self.__dict.items()))
        return self.__hash
    
    def _keylist(self):
        return self.__keys
    
    def _get_value(self, key):
        return self.__dict[key]
    
    def copy(self):
        return self.__class__(self.__dict)
    
    @classmethod
    def fromkeys(cls, seq, value=None):
        return cls((k, value) for k in seq)


class fifo(deque):
    """A first-in, first-out data queue.
    """
    
    def __init__(self, *args, **kwargs):
        self.nextitem = self.popleft
        deque.__init__(self, *args, **kwargs)


class stack(list):
    """A last-in, first-out data queue.
    """
    
    def __init__(self, *args, **kwargs):
        self.nextitem = self.pop
        list.__init__(self, *args, **kwargs)


class AttrDelegate(object):
    """Delegate attribute access to an underlying object.
    """
    
    def __init__(self, obj):
        self._o = obj
    
    def __getattr__(self, name):
        # Delegate to the underlying object
        return getattr(self._o, name)


class AttrDict(AttrDelegate, basekeyed):
    """Make an object with attributes support a mapping interface.
    
    Only attributes defined in the attribute list passed to this
    class will appear as allowed keys in the mapping. The
    mapping is immutable (since it is only supposed to be
    "assigned" to during initialization).
    """
    
    def __init__(self, keylist, obj):
        AttrDelegate.__init__(self, obj)
        self._keys = keylist
    
    def _keylist(self):
        return self._keys
    
    def _get_value(self, key):
        return getattr(self, key)


class AttrList(AttrDelegate, basecontainer):
    """Make an object with attributes support a sequence interface.
    
    Only indexes in a valid range for the list of attribute names
    passed in will be valid indexes into the sequence (each index
    will access the attribute with the corresponding name in the
    list of names passed in). The sequence is immutable.
    """
    
    def __init__(self, names, obj):
        AttrDelegate.__init__(self, obj)
        self._names = names
    
    def _indexlen(self):
        return len(self._names)
    
    def _get_data(self, index):
        return getattr(self, self._names[index])


def immutable(o):
    """Return immutable copy of object.
    
    Includes making immutable copies of objects inside containers.
    
    >>> all(immutable(o) is o for o in (None, False, True, 0, 1, -1, "", "a", (), ("a",), frozenset(), frozenset(["a"])))
    True
    >>> all(immutable(o) is not o for o in ({}, {"a": 1}, [], ["a"], set(), set(["a"])))
    True
    
    Can't include lists in this next test since they won't compare equal to tuples
    even if the elements are all the same.
    
    >>> all(immutable(o) == o for o in ({}, {"a": 1}, set(), set(["a"])))
    True
    >>> immutable([])
    ()
    >>> immutable(["a"])
    ('a',)
    >>> immutable([[1], [2]])
    ((1,), (2,))
    >>> type(immutable({"a": [1], "b": [2]}))
    <class 'plib.stdlib.coll.frozendict'>
    >>> sorted(immutable({"a": [1], "b": [2]}).items())
    [('a', (1,)), ('b', (2,))]
    >>> type(immutable({"a"}))
    <class 'frozenset'>
    """
    
    if isinstance(o, MutableSequence):
        return tuple(immutable(item) for item in o)
    if isinstance(o, MutableMapping):
        return frozendict((key, immutable(value)) for key, value in o.items())
    if isinstance(o, MutableSet):
        return frozenset(o)
    return o


if __name__ == '__main__':
    import doctest
    doctest.testmod()
