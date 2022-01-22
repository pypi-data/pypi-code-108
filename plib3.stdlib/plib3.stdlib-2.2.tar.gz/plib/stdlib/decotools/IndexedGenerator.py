#! /usr/bin/env python3
"""
Module IndexedGenerator
Sub-Package STDLIB.DECOTOOLS of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A wrapper class for generators that makes them indexable
like sequences, without requiring all the terms to be
realized immediately. Since doing this requires caching the
objects yielded by the generator (so that retrieving an item at
an index that's already been retrieved once doesn't re-realize
the generator), this class is derived from ``MemoizedGenerator``,
so that for multiple realizations of the generator with the same
arguments, the terms are only computed once.

The possibility was considered of making indexing orthogonal
to memoization of generators, i.e., not inheriting this class
from ``MemoizedGenerator`` but implementing it independently
(and then just combining the two decorators if both types of
functionality are desired). Doing this would probably make the
implementations of both decorators more complicated, since
they would still have to allow for being combined without
duplicating the memoization code, and there didn't seem to be
any obvious use case, since memoization is only done for multiple
calls to the generator with the exact same arguments, which
should all represent requests for the same sequence of objects.
The only thing left out on the second and subsequent calls is
any side effects of computing each generator term, but you
shouldn't be relying on those anyway, as the functional
programming types will be happy to tell you. :-)
"""

from plib.stdlib.coll import AbstractContainerMixin

from .MemoizedGenerator import MemoizedGenerator

# Cheat so we don't have to import this explicitly, which would
# be somewhat clumsy because of how plib's imports are set up

_memohelper = MemoizedGenerator.helper_class


class indexediterator(AbstractContainerMixin):
    # Helper class to be returned as the actual generator with
    # indexing; wraps the generator in an iterator that also
    # supports item retrieval by index.
    
    def __init__(self, helper):
        self.__helper = helper
        # Realizes the generator; this is what will be returned by
        # a call to the indexed generator function
        self.__iter = helper._iterable()
    
    def __iter__(self):
        # Return the generator function; note that we return
        # the same one each time, which matches the semantics
        # of actual generators (i.e., once the generator function
        # is called, iter(gen) returns the same iterator and does
        # not reset the state)
        return self.__iter
    
    def __next__(self):
        # Return next item from generator
        term = next(self.__iter)
        if term == self.__helper.sentinel:
            raise StopIteration
        return term
    
    def _indexlen(self):
        # If the generator is exhausted, we know its length, so
        # we can use that information; if not, we raise TypeError,
        # just like any other object with no length
        result = self.__helper._itemcount()
        if result is None:
            raise TypeError("object of type {} has no len()".format(self.__class__.__name__))
        return result
    
    # We inherit from AbstractContainerMixin so that we get slice
    # handling "for free"; the only wrinkle is that we don't have
    # a known length so negative indexes can't be normalized, the
    # slice handling code detects that by seeing that we don't
    # have a __len__ method and raising IndexError for negative
    # indexes.
    
    def _get_data(self, i):
        result = self.__helper._retrieve(i)
        if result is self.__helper.sentinel:
            raise IndexError("sequence index out of range")
        return result


class _indexhelper(_memohelper):
    # Helper class that wraps the generator for indexing
    
    def _realize(self):
        # This realizes the generator and adds indexing as well
        return indexediterator(self)


class IndexedGenerator(MemoizedGenerator):
    """Make a generator indexable like a sequence.
    
    A side benefit is that the generator is memoized as well,
    since we have to keep a cache of already generated elements
    so we don't have to re-realize the generator if the element
    at a given index is accessed more than once.
    
    Note that the sequence is not mutable. Also note that, while
    it behaves like a sequence for indexing, it behaves like a
    generator with regard to iteration; repeated calls to ``next``
    (or something like a ``for`` loop) will eventually exhaust
    it and ``StopIteration`` will be raised, even though indexing
    into it will still retrieve items already yielded.
    
    Like ``MemoizedGenerator``, this class can only be used
    directly to decorate an ordinary function. It is recommended
    that the ``indexable_generator`` decorator be used instead
    since it works on methods as well.
    """
    
    helper_class = _indexhelper
