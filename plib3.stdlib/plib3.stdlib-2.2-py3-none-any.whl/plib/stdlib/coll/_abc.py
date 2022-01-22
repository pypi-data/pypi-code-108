#! /usr/bin/env python3
"""
Module _ABC -- Abstract Base Classes for PLIB3 Collections
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

These abstract base classes overlay some PLIB3-specific
features on the standard collection ABCs.
"""

from abc import abstractmethod
from collections.abc import Mapping, MutableMapping, Sequence, MutableSequence
from itertools import zip_longest
from operator import lt, gt

from plib.stdlib.builtins import first

__all__ = [
    "abstractkeyed",
    "abstractmapping",
    "abstractdict",
    "abstractcontainer",
    "abstractsequence",
    "abstractlist"
]


class _MapMixin(object):
    # Mixin class for common mapping functionality
    
    __slots__ = ()
    
    def __len__(self):
        return sum(1 for _ in self)
    
    def has_key(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True


class abstractkeyed(_MapMixin, Mapping):
    """Immutable abstract key-value mapping. Adds the ``has_key``
    method to the standard ``Mapping`` class. Also adds a default
    implementation for ``__len__``, based on ``__iter__``, and
    a ``has_key`` method as an alias for ``__contains__``.
    
    The intent of this class, like its counterpart for sequences,
    ``abstractcontainer``, is to minimize the amount of work needed
    to make a data structure support the Python mapping interface.
    Derived classes only need to implement the ``__iter__`` and
    ``__getitem__`` methods (they may also override the ``__len__``
    and ``__contains__`` methods if faster implementations are
    available). This mapping is immutable; increasing levels of
    mutability are provided by ``abstractmapping`` and
    ``abstractdict``.
    """
    
    __slots__ = ()


class abstractmapping(abstractkeyed):
    """Abstract mapping with fixed keys but mutable values. Adds
    the ``__setitem__`` and ``update`` methods to ``abstractkeyed``,
    allowing existing keys to be bound to new values.
    
    This class can be used to provide a mapping-like view of data
    structures whose set of keys cannot be changed, but which can
    have keys re-bound to new values.
    
    Note: this class does not implement any mechanism to initialize
    the mapping from another one (i.e., to be able to call the
    constructor with another mapping as an argument, or with keyword
    arguments, as a dict can be). Subclasses that desire such a
    mechanism must implement it with an overridden constructor, and
    must ensure that the mechanism is compatible with the ``__contains__``
    and ``__setitem__`` methods (so that those methods will not raise
    a KeyError during the initialization process).
    """
    
    __slots__ = ()
    
    @abstractmethod
    def set_key(self, key, value):
        raise KeyError
    
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            raise
        else:
            self.set_key(key, value)
    
    def update(*args, **kwds):
        # Duplicates MutableMapping.update, but depends on ``__setitem__``
        # to guarantee that only existing keys get updated
        if len(args) > 2:
            raise TypeError("update() takes at most 2 positional "
                            "arguments ({} given)".format(len(args)))
        elif not args:
            raise TypeError("update() takes at least 1 argument (0 given)")
        self = args[0]
        other = args[1] if len(args) >= 2 else ()
        
        if isinstance(other, Mapping):
            for key in other:
                self[key] = other[key]
        elif hasattr(other, "keys"):
            for key in other.keys():
                self[key] = other[key]
        else:
            for key, value in other:
                self[key] = value
        for key, value in kwds.items():
            self[key] = value


class abstractdict(_MapMixin, MutableMapping):
    """Fully mutable abstract dictionary. Adds public construction
    methods to ``MutableMapping``, based on the standard ``dict``
    constructor signature and methods. Also adds default ``__len__``
    implementation, ``__cmp__``, and ``has_key`` as with ``abstractkeyed``.
    
    The only methods which *must* be implemented are ``__iter__``,
    ``__getitem__``, ``__setitem__``, and ``__delitem__``. Also, it
    will almost always be necessary to override ``__init__`` to initialize
    the underlying data structure *before* calling up to this class's
    ``__init__`` (which will populate the data structure if a mapping or
    keyword arguments are passed to the constructor). It may also be
    advantageous to reimplement ``__contains__`` and/or ``__len__`` if more
    efficient algorithms specific to the underlying data structure can be
    used.
    """
    
    __slots__ = ()
    
    def __init__(self, mapping=None, **kwargs):
        """Initialize the data structure from mapping.
        
        Subclasses should set up the underlying data structure *before*
        calling up to this method.
        """
        
        if mapping or kwargs:
            self.update(mapping or {}, **kwargs)
    
    def copy(self):
        return self.__class__(self)
    
    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d


class _MiniMe(object):
    # Helper class, instances are guaranteed to be less than anything
    # and greater than nothing (no other comparisons are implemented
    # since this is only for use by _SeqMixin below; the default object
    # implementation for equality guarantees that an instance of this
    # class will not be equal to anything, so the ``_diff`` method below
    # will work without any additional code here)
    
    __slots__ = ()
    
    def __lt__(self, other):
        return True
    
    def __gt__(self, other):
        return False


class _SeqMixin(object):
    # Mixin class for common sequence functionality
    
    __slots__ = ()
    
    def __len__(self):
        return sum(1 for _ in self)
    
    def has_index(self, index):
        try:
            self[index]
        except IndexError:
            return False
        else:
            return True
    
    __mini = _MiniMe()
    
    def _diff(self, other):
        return first((x, y) for x, y in zip_longest(self, other, fillvalue=self.__mini)
                     if x != y)
    
    def __ne__(self, other):
        return (len(other) != len(self)) or self._diff(other)
    
    def __eq__(self, other):
        return not self.__ne__(other)
    
    def _comp(self, other, op, eq):
        d = self._diff(other)
        if d:
            return op(d[0], d[1])
        return eq
    
    def __lt__(self, other):
        return self._comp(other, lt, False)
    
    def __gt__(self, other):
        return self._comp(other, gt, False)
    
    def __le__(self, other):
        return self._comp(other, lt, True)
    
    def __ge__(self, other):
        return self._comp(other, gt, True)


class abstractcontainer(_SeqMixin, Sequence):
    """Immutable abstract container. Adds comparison operators to
    the standard ``Sequence`` class. Also adds a default implementation
    for ``__len__`` (not sure why the standard class doesn't do that),
    and a convenience method, ``has_index``, which implements a crude
    test for index validity (it works for integer indexes, but is not
    reliable for slice indexes).
    
    An abstract class to provide the minimal possible support of the
    Python container protocol. Subclasses only need to implement the
    ``__getitem__`` method to allow the class to be used in the standard
    Python container idioms like for item in container, etc. This
    container is immutable, so its length and its items cannot be
    changed (increasing levels of mutability are provided by the
    abstractsequence and abstractlist classes); note that this does
    *not* mean the underlying data structure must be immutable, only
    that the view of it provided by this container class is.
    """
    
    __slots__ = ()


class abstractsequence(abstractcontainer):
    """Fixed-length abstract sequence. Adds the ``set_index``
    and ``reverse`` methods to ``abstractcontainer``, allowing new
    values to be put into existing sequence index locations. The
    ``__setitem__`` method is given a default implementation that
    depends on ``__getitem__`` to determine if an index is valid;
    however, the check made here is not perfect for slice arguments,
    and the ``set_index`` implementation should not assume that
    slice indexes are automatically valid.
    
    This class can be used to provide a sequence-like view of data
    structures whose length should not be mutable, but whose elements
    can be re-bound to new objects (unlike a tuple, whose elements
    can't be changed, although if the element objects themselves are
    mutable, they can be mutated in-place).
    
    Note: this class does not implement any mechanism to initialize
    the sequence from another one (i.e., to be able to call the
    constructor with another sequence as an argument, as the tuple
    constructor can be called). Subclasses that desire such a
    mechanism must implement it with an overridden constructor, and
    must ensure that the mechanism is compatible with the ``__len__``
    and ``__setitem__`` methods (so that those methods will not return
    an index out of range error during the initialization process).
    """
    
    __slots__ = ()
    
    @abstractmethod
    def set_index(self, index, value):
        raise IndexError
    
    def __setitem__(self, index, value):
        try:
            self[index]
        except IndexError:
            raise
        else:
            self.set_index(index, value)
    
    def reverse(self):
        # Duplicates MutableSequence.reverse
        n = len(self)
        for i in range(n // 2):
            self[i], self[n - i - 1] = self[n - i - 1], self[i]


class abstractlist(_SeqMixin, MutableSequence):
    """Fully mutable abstract sequence. Adds public constructor to match
    standard ``list`` signature. Also adds default ``__len__`` implementation,
    as with ``abstractcontainer``, and a ``clear`` method similar to that of
    mappings, for convenience.
    
    The only methods which *must* be implemented in subclasses are ``__getitem__``,
    ``__setitem__``, ``__delitem__``, and ``insert``. Also, it will almost always
    be necessary to override ``__init__`` to initialize the underlying data
    structure *before* calling up to this class's ``__init__`` (which will
    populate the data structure if a sequence is passed to the constructor).
    It may also be advantageous to reimplement ``__iter__`` if a more efficient
    method of iterating through the underlying data structure exists (this will
    depend on how expensive the ``__getitem__`` call is vs. the reimplemented
    iterator), ``__contains__`` if a more efficient membership test exists, and
    ``__len__`` if a more efficient way of obtaining the sequence length exists.
    Finally, note that ``sort`` is not implemented in this class, since duplicating
    the built-in ``list.sort`` is highly problematic without knowledge of the
    underlying data structure; therefore sort functionality must be implemented
    as well if desired.
    """
    
    __slots__ = ()
    
    def __init__(self, iterable=None):
        """Initialize the data structure from iterable.
        
        Subclasses should set up the underlying data structure *before*
        calling up to this method.
        """
        
        if iterable:
            self.extend(iterable)
    
    # We add this one method here for convenience although normally only
    # mappings have it, not sequences
    
    def clear(self):
        while len(self):
            self.pop()
