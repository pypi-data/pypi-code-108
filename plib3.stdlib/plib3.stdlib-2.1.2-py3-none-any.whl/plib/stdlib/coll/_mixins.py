#! /usr/bin/env python3
"""
Module _MIXINS -- Mixin Classes for PLIB3 Collections
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

These mixin classes further specialize the functionality
of the PLIB3 collection ABCs.
"""

from abc import ABCMeta, abstractmethod
from bisect import bisect_left, bisect_right


from ._utils import *

__all__ = [
    "AbstractKeyedMixin",
    "AbstractMappingMixin",
    "AbstractDictMixin",
    "AbstractContainerMixin",
    "AbstractSequenceMixin",
    "AbstractListMixin",
    "SortMixin"
]


class AbstractKeyedMixin(object, metaclass=ABCMeta):
    """Mixin class for immutable abstract key-value mapping.
    
    Implements the standard container methods by assuming that
    the object has a list of its valid keys, and knows how to
    retrieve a value for each key; this knowledge should be
    implemented in derived classes in the private ``_keylist``
    and ``_get_value`` methods. Once these two methods are provided,
    the entire immutable mapping interface will work. (Derived
    classes will most likely also need to implement a constructor
    to initially populate the underlying data structure that the
    ``_keylist`` and ``_get_value`` methods access.)
    """
    
    __slots__ = ()
    
    @abstractmethod
    def _keylist(self):
        """Return immutable container of valid keys for this mapping.
        """
        return ()
    
    @abstractmethod
    def _get_value(self, key):
        """Return value corresponding to key.
        
        This method will only be called for keys that are known to
        be in the mapping.
        """
        return None
    
    def __getitem__(self, key):
        if key in self._keylist():
            return self._get_value(key)
        raise KeyError(repr(key))
    
    def __iter__(self):
        return iter(self._keylist())
    
    # We expect this to be faster than the default implementation
    # because _keylist() should be O(1) for length checks
    
    def __len__(self):
        return len(self._keylist())


class AbstractMappingMixin(AbstractKeyedMixin):
    """Mixin class for mapping with fixed keys but mutable values.
    
    Supports key checking on item assignment, enforcing the
    rule that the mapping's set of keys cannot change.
    """
    
    __slots__ = ()
    
    @abstractmethod
    def _set_value(self, key, value):
        """Set value corresponding to key.
        
        This method will only be called for keys that are known to
        be in the mapping.
        """
        pass
    
    def __setitem__(self, key, value):
        if key in self._keylist():
            self._set_value(key, value)
        else:
            raise KeyError(repr(key))


class AbstractDictMixin(AbstractMappingMixin):
    """Mixin class for fully mutable abstract mapping.
    
    Provides default implementations of all mutable mapping methods
    based on the core key/value get/set/add/delete methods.
    """
    
    __slots__ = ()
    
    @abstractmethod
    def _add_key(self, key, value):
        """Add key and value to the mapping.
        
        Will only be called if key is not currently in the mapping.
        """
        pass
    
    @abstractmethod
    def _del_key(self, key):
        """Remove key and its corresponding value from the mapping.
        
        Will only be called if key is currently in the mapping.
        """
        pass
    
    def __setitem__(self, key, value):
        if key in self._keylist():
            self._set_value(key, value)
        else:
            self._add_key(key, value)
    
    def __delitem__(self, key):
        if key in self._keylist():
            self._del_key(key)
        else:
            raise KeyError(repr(key))


class AbstractContainerMixin(object, metaclass=ABCMeta):
    """Mixin class for immutable abstract container.
    
    Support slice operations and normalization of indexes. This class is
    immutable; increasing levels of mutability are provided by
    ``AbstractSequenceMixin`` and ``AbstractListMixin``.
    
    Note that, because this class is immutable and we can't provide a
    constructor without knowing the underlying data storage implementation,
    the slice_class field is provided to allow derived classes to specify
    which class to use when returning slices (e.g., x = s[i:j]). This means
    that these abstract containers are not guaranteed to return slices that
    are of the same type as themselves, although the slice_class should be
    chosen to make them completely compatible functionally.
    """
    
    __slots__ = ()
    
    slice_class = tuple
    
    @abstractmethod
    def _indexlen(self):
        """Return the number of valid indexes into the sequence.
        """
        return 0
    
    @abstractmethod
    def _get_data(self, index):
        """Return a single item by index.
        
        (Slice arguments to ``__getitem__`` may result in multiple calls
        to this method).
        """
        return None
    
    def _index_ok(self, index):
        """Validate, and if necessary normalize, index.
        
        If ``index`` is an int, it must be within the valid sequence
        range (0 to len - 1), after correcting negative indexes relative
        to the end of the sequence. If so, return it; otherwise raise
        ``IndexError``. (The ``normalize`` function is used to accomplish
        this.)
        
        If index is a slice, normalize it (by calling ``normalize_slice``)
        and return a 2-tuple of (slice length, normalize_slice result).
        No exceptions are thrown here for slices; that is left up to
        the caller (since here we don't know whether zero-length slices
        are allowed or not).
        
        Sequences that do not have a known length (e.g., instances of
        the ``IndexedGenerator`` decorator class) will raise ``IndexError``
        if any negative indexes are given, either as single indexes or
        slice elements.
        """
        
        try:
            normlen = self._indexlen()
        except TypeError:
            normlen = None
        if isinstance(index, int):
            if normlen is None:
                if index < 0:
                    raise IndexError("sequence index out of range")
                return index
            return normalize(normlen, index)
        elif isinstance(index, slice):
            n = normalize_slice(normlen, index)
            if isinstance(n, int):
                return (0, n)
            return (len(n), n)
        else:
            raise TypeError("sequence index must be an integer or a slice")
    
    def __getitem__(self, index):
        index = self._index_ok(index)
        if isinstance(index, tuple):
            length, indexes = index
            if length > 0:
                return self.slice_class(self._get_data(i) for i in indexes)
            return self.slice_class()
        return self._get_data(index)
    
    def __len__(self):
        return self._indexlen()


class AbstractSequenceMixin(AbstractContainerMixin):
    """Mixin class for fixed-length abstract sequence.
    
    Supports argument checking on item assignment, enforcing the
    rule that the sequence's length cannot change.
    """
    
    __slots__ = ()
    
    @abstractmethod
    def _set_data(self, index, value):
        """Store a single item by index.
        
        (Slice arguments to ``__setitem__`` may result in multiple calls
        to this method).
        """
        pass
    
    def __setitem__(self, index, value):
        # NOTE: the treatment of extended slices matches Python 2.6
        # list semantics; that means that, unlike in 2.5 and earlier,
        # extended slices with step == 1 are treated exactly the same
        # as non-extended slices
        extended = (
            isinstance(index, slice)
            and (index.step is not None)
            and (index.step != 1)
        )
        index = self._index_ok(index)
        if isinstance(index, tuple):
            if value is self:
                # protect against a[::-1] = a
                value = tuple(value)
            try:
                vlength = len(value)
            except TypeError:
                try:
                    # NOTE: no way to avoid realizing generators/iterators
                    # here; we use tuple because it's faster to construct
                    # than list. As far as I can tell, the Python interpreter
                    # does the same thing for comparing the lengths of values
                    # and slices; the difference is that the interpreter only
                    # does it for extended slices, but we have to do it here
                    # even for a standard slice. This means, of course, that
                    # for fully mutable sequences (like AbstractMixin) and
                    # standard slices, we make an extra copy of the value when
                    # we don't really have to. For the use cases I've had thus
                    # far, this is not a major issue, because I've almost
                    # never had to use slicing, and when I do it's always
                    # small slices; also, typically the overhead of the
                    # individual item inserts (e.g., if each item is a row
                    # in a GUI table or a node in a GUI tree view) is much
                    # higher than the overhead of copying the object pointer
                    # into a tuple. Your mileage may vary.
                    value = tuple(value)
                    vlength = len(value)
                except TypeError:
                    raise TypeError("can only assign an iterable")
            length, index = index
            if (length < 1) and not extended:
                if vlength != 0:
                    self._add_items(index, value)
            elif length != vlength:
                if extended:
                    raise ValueError(
                        "attempt to assign sequence of length %i "
                        "to extended slice of length %i" %
                        (vlength, length))
                self._rep_items(index, value)
            else:
                for i, v in zip(index, value):
                    self._set_data(i, v)
        else:
            self._set_data(index, value)
    
    # These methods allow easy factoring out of the differences
    # between fixed-length and fully mutable sequences
    
    def _add_items(self, index, value):
        raise TypeError("object does not support item insert/append")
    
    def _rep_items(self, indexes, value):
        raise ValueError("object length cannot be changed")
    
    # Alternate implementation of reverse using extended slicing (should
    # be faster than the explicit for loop in abstractsequence.reverse)
    
    def reverse(self):
        l = len(self)
        c = l // 2
        d = l - c
        self[0:c:1], self[l - 1:d - 1:-1] = self[l - 1:d - 1:-1], self[0:c:1]


class AbstractListMixin(AbstractSequenceMixin):
    """Mixin class for fully mutable abstract sequence.
    
    Provides default implementations of all mutable sequence methods
    based on the core data get/set/add/delete methods.
    """
    
    __slots__ = ()
    
    slice_class = list
    
    @abstractmethod
    def _add_data(self, index, value):
        """Insert a single item at index.
        
        (Zero-length slice arguments to ``__setitem__`` will result in
        one call to this method for each item in the value being set).
        If index == self.__len__(), this method should append value to
        the sequence.
        """
        pass
    
    @abstractmethod
    def _del_data(self, index):
        """Delete a single item by index.
        
        (Slice arguments to ``__delitem__`` may result in multiple
        calls to this method).
        """
        pass
    
    def _add_items(self, index, value):
        for j, v in enumerate(value):
            self._add_data(index + j, v)
    
    def _del_items(self, indexes):
        # Delete in inverse order to minimize movement of items higher in list
        for i in reversed(indexes):
            self._del_data(i)
    
    def _rep_items(self, indexes, value):
        self._del_items(indexes)
        self._add_items(indexes[0], value)
    
    def __delitem__(self, index):
        index = self._index_ok(index)
        if isinstance(index, tuple):
            length, index = index
            if length > 0:
                self._del_items(index)
        else:
            self._del_data(index)
    
    def insert(self, index, value):
        if not isinstance(index, int):
            raise TypeError("an integer is required")
        # list.insert is very permissive with index values, match that behavior
        index = min(index, len(self))
        if index < 0:
            index = max(0, len(self) + index)
        self._add_data(index, value)


class SortMixin(object):
    """Sequence mixin class to enforce sort order.
    
    Mixin class to allow insertion of objects into sequences
    in proper sorted order. Will work with any class that
    implements the standard sequence interface. The general
    method is the same as the SortedCollection ActiveState
    recipe at
    
    http://code.activestate.com/recipes/577197-sortedcollection/
    
    but it uses super calls to the base sequence class to
    implement the actual data storage.
    
    Note that we do not implement an ``__init__`` method because
    its signature and code will depend on what kind of sequence
    class we are mixing in. See the doctest txt file in the
    ``plib.test`` sub-package for an example of how to implement
    a basic constructor when using this class as a mixin.
    """
    
    # NOTE: we would like to use __slots__ here, but we can't if
    # we want to be able to use this mixin with built-in types
    # like list (as is done in the doctest corresponding to this
    # module); Python doesn't support non-empty __slots__ with
    # "variable-length" built-in types.
    
    def _init_key(self, key):
        # Initialize sort key
        return (lambda x: x) if key is None else key
    
    def _init_seq(self, iterable, key):
        # Fill up sequence from iterable in correct sorted order;
        # this should be called from the constructor of any class
        # using this mixin, to properly initialize the sequence;
        # assumes that the sequence is empty
        self._given_key = key
        self._key = self._init_key(key)
        self._populate(iterable)
    
    def _populate(self, iterable):
        # Populate underlying sequence from iterable; assumes
        # sequence is currently empty
        key = self.key
        decorated = sorted((key(item), item) for item in (iterable or ()))
        self._keys = []
        for i, (k, item) in enumerate(decorated):
            self._keys.append(k)
            # This hack is needed to avoid relying on the underlying
            # implementation of any methods other than insert, since
            # we are overriding most of them
            super(SortMixin, self).insert(i, item)
    
    def _getkey(self):
        return self._key
    
    def _setkey(self, key):
        if key is not self._key:
            # This is the safest way to re-construct the underlying
            # data structure in the new sorted order; many sequence
            # classes can be re-initialized by calling the constructor
            # again (e.g., the list built-in), but we can't assume
            # that this will always work
            data = self[:]
            self.clear()
            self._init_seq(data, key)
    
    def _delkey(self):
        self._setkey(None)
    
    key = property(_getkey, _setkey, _delkey, "key function")
    
    def __repr__(self):
        return '{}({}, key={})'.format(
            self.__class__.__name__,
            super(SortMixin, self).__repr__(),
            getattr(self._given_key, '__name__', repr(self._given_key))
        )
    
    # __len__, __iter__, and __getitem__ can be inherited safely
    # from the base class since they don't mutate the sequence
    
    def __setitem__(self, index, value):
        raise TypeError("can't set item by index on sorted sequence; use insert instead.")
    
    def __delitem__(self, index):
        """Delete item at index"""
        del self._keys[index]
        super(SortMixin, self).__delitem__(index)
    
    def copy(self):
        return self.__class__(self, self._key)
    
    def _searchindexes(self, item, keyindex=None):
        # Return indexes delimiting the part of self that could contain item;
        # keyindex=0 or 1 to substitute item key for one index
        k = self._key(item)
        i = k if (keyindex is 0) else bisect_left(self._keys, k)
        j = k if (keyindex is 1) else bisect_right(self._keys, k)
        return i, j
    
    def _searchspace(self, item):
        # Return subsequence of self that could contain item
        i, j = self._searchindexes(item)
        return self[i:j]
    
    def __contains__(self, item):
        # This should be faster than the base class implementation,
        # O(log n) instead of O(n)
        return item in self._searchspace(item)
    
    def index(self, item):
        """Find the position of an item. Raise ValueError if not found."""
        i, j = self._searchindexes(item)
        return self[i:j].index(item) + i
    
    def count(self, item):
        """Return number of occurrences of item"""
        return self._searchspace(item).count(item)
    
    def insert(self, item):
        """Insert a new item. If equal keys are found, add to the left"""
        i, k = self._searchindexes(item, 1)
        self._keys.insert(i, k)
        super(SortMixin, self).insert(i, item)
    
    def insert_right(self, item):
        """Insert a new item. If equal keys are found, add to the right"""
        k, i = self._searchindexes(item, 0)
        self._keys.insert(i, k)
        super(SortMixin, self).insert(i, item)
    
    append = insert_right  # seems like a useful redefinition
    
    def extend(self, iterable):
        if len(self) > 0:
            # Have to do it the long way if we already have items
            for item in iterable:
                self.append(item)
        else:
            # Shortcut when initializing
            self._populate(iterable)
    
    def remove(self, item):
        """Remove first occurence of item. Raise ValueError if not found"""
        i = self.index(item)
        del self[i]
    
    def pop(self, index=-1):
        """Pop an item off the sequence.
        
        Note that we don't use the inherited pop method because it might
        depend on other methods we override; instead we do it all by hand.
        """
        v = self[index]
        self._keys.pop(index)
        super(SortMixin, self).__delitem__(index)
        return v
    
    def clear(self):
        try:
            super(SortMixin, self).clear()
        except AttributeError:
            # Base class doesn't have a clear method, mock it up
            for _ in range(len(self)):
                super(SortMixin, self).pop()
        self._keys = []
    
    def sort(self, *args):
        raise TypeError("can't manually sort a sorted sequence.")
    
    def reverse(self):
        raise TypeError("can't reverse a sorted sequence.")
