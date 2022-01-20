#! /usr/bin/env python3
"""
Module _BASES -- Specialized Base Classes for PLIB3 Collections
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

These classes combine the standard PLIB3 collection ABCs
with the mixins that provide more specialized functionality.
"""

from plib.stdlib.coll import (
    AbstractKeyedMixin, abstractkeyed,
    AbstractMappingMixin, abstractmapping,
    AbstractDictMixin, abstractdict,
    AbstractContainerMixin, abstractcontainer,
    AbstractSequenceMixin, abstractsequence,
    AbstractListMixin, abstractlist
)

__all__ = [
    "basekeyed",
    "basemapping",
    "basedict",
    "basecontainer",
    "basesequence",
    "baselist"
]


class basekeyed(AbstractKeyedMixin, abstractkeyed):
    """Base class for immutable key-value mapping.
    
    The intent of this class, like its counterpart for sequences,
    ``basecontainer``, is to minimize the amount of work needed
    to make a data structure support the Python mapping interface.
    Derived classes only need to implement the ``_keylist`` and
    ``_get_value`` methods. This mapping is immutable; increasing
    levels of mutability are provided by ``basemapping`` and
    ``basedict``.
    """
    
    __slots__ = ()


class basemapping(AbstractMappingMixin, abstractmapping):
    """Base class for mapping with fixed keys but mutable values.
    
    An abstract mapping whose keys cannot be changed. Implements
    key checking on item assignment to enforce this restriction.
    
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
    ``KeyError`` during the initialization process).
    """
    
    __slots__ = ()
    
    # Slight wart due to the default implementation of abstractmapping
    
    def set_key(self, key, value):
        # We know key is in the mapping so just set it directly
        self._set_value(key, value)


class basedict(AbstractDictMixin, abstractdict):
    """Base class for fully mutable dictionary.
    
    Base dict class that partially implements the necessary abstract methods.
    
    This class reduces the amount of work required to make a data structure
    look like a Python dict. It implements the ``__getitem__``, ``__setitem__``,
    and ``__delitem__`` methods to provide the following:
    
    - checking of keys for ``__getitem__`` and ``__delitem__``;
    
    - distinguishing in ``__setitem__`` between setting the value of an existing
      key, and adding a new key with its value.
    
    The work needed to fully implement a dict-emulator is thus reduced to the
    following: implement ``_keylist`` to return the current list of allowed keys,
    ``_get_value`` to retrieve one value by key, ``_set_value`` to store one
    value by key, ``_add_key`` to add a new key with its value, and ``_del_key``
    to remove one key with its value. Implementing these methods is sufficient
    to overlay full dict functionality on the underlying data structure. Also,
    as the ``abstractdict`` docstring states, ``__init__`` will almost always
    need to be overridden to initialize the underlying data structure prior
    to this class's constructor (which populates the data) being called.
    
    Note that if no or limited mutability is desired, the ``basemapping`` and
    ``basekeyed`` classes are designed on the same principles as above, but
    with all mutability (for ``basekeyed``) or all changes to the set of allowed
    keys (for ``basemapping``) disabled.
    """
    
    __slots__ = ()


class basecontainer(AbstractContainerMixin, abstractcontainer):
    """Base class for immutable container.
    
    An abstract class to provide the minimal possible support of the
    Python container protocol. Subclasses can implement just the ``_indexlen``
    and ``_get_data`` methods to allow the class to be used in the standard
    Python container idioms like ``for item in container``, etc. This
    container is immutable, so its length and its items cannot be
    changed (increasing levels of mutability are provided by the
    ``basesequence`` and ``baselist`` classes); note that this does
    *not* mean the underlying data structure must be immutable, only
    that the view of it provided by this container class is.
    """
    
    __slots__ = ()


class basesequence(AbstractSequenceMixin, abstractsequence):
    """Base class for fixed-length abstract sequence.
    
    An abstract sequence whose length cannot be changed. Implements
    argument checking on item assignment to enforce this restriction.
    
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
    must ensure that the mechanism is compatible with the ``_indexlen``
    and ``_set_data`` methods (so that those methods will not return
    an index out of range error during the initialization process).
    """
    
    __slots__ = ()
    
    # Slight wart due to the default implementation of abstractsequence
    
    def set_index(self, index, value):
        # This reverses the dependency order in abstractsequence,
        # because __setitem__ now breaks down slice indexes into
        # multiple calls to the underlying _set_data
        self.__setitem__(index, value)


class baselist(AbstractListMixin, abstractlist):
    """Base class for fully mutable abstract list.
    
    Base list class that partially implements the necessary abstract methods.
    
    This class reduces the amount of work required to make a data structure
    look like a Python list. It implements the ``__getitem__``, ``__setitem__``,
    and ``__delitem__`` methods to provide the following:
    
    - normalization of indexes (negative indexes relative to end of list and
      out of range exceptions);
    
    - support for slices as arguments.
    
    The work needed to fully implement a list-emulator is thus reduced to the
    following: implement ``_indexlen`` to return the current number of valid
    indexes, ``_get_data`` to retrieve one item by index, ``_set_data``
    to store one item by index, _add_data to add/insert one item by index,
    and _del_data to remove one item by index. Implementing these methods is
    sufficient to overlay full list functionality on the underlying data
    structure; operations which add, set, or remove multiple items will
    result in multiple calls to _set, _add, or _del as appropriate. Other
    methods can be overridden if needed for efficiency (e.g., to increase
    speed for multi-item operations), per the abstractlist class docstring
    (note that, as that docstring states, ``__init__`` will almost always need
    to be overridden to initialize the underlying data structure, and ``sort``
    must be implemented if sorting functionality is desired).
    
    Note that if no or limited mutability is desired, the ``basecontainer`` and
    ``basesequence`` classes are designed on the same principles as above, but
    with all mutability (for ``basecontainer``) or all changes in sequence length
    (for ``basesequence``) disabled.
    """
    
    __slots__ = ()
