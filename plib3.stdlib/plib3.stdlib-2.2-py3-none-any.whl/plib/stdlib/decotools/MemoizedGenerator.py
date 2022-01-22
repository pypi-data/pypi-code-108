#! /usr/bin/env python3
"""
Module MemoizedGenerator
Sub-Package STDLIB.DECOTOOLS of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A wrapper class for generators that "memoizes" them, so that even
if the generator is realized multiple times, each term only gets
computed once (after that the result is simply returned from a
cache).

Functional programming types will note that this implementation
is done using a class, not a function. Doing it as a function in
Python would require some inelegant hacks with mutable containers
since Python does not allow a closure's inner function to mutate
variables in the closure's outer function. (Python 2.7 adds the
``nonlocal`` keyword to allow such behavior, but I didn't want to
require 2.7 for this since many Linux distributions are still at
2.6 as of this writing.) Lisp hackers will of course make smug
comments on this limitation of Python's, but I don't care. :-)
"""

import sys

from plib.stdlib.decotools import cached_function


class _memohelper(object):
    # Helper class to handle memoization info for each individual
    # generator realization
    
    sentinel = object()  # used internally to signal empty generator
    
    def __init__(self, it, cachelimit):
        self.__cache = []
        self.__empty = False
        self.__iter = it
        self.__limit = cachelimit
    
    def _retrieve(self, n):
        # Retrieve the nth item from the generator. Advance
        # the generator as necessary. Return a sentinel object
        # if the desired index cannot be retrieved. Note that
        # this only works up to the cache size limit; past that
        # items cannot be retrieved by index, only iterated over
        if n >= self.__limit:
            return self.sentinel
        while (not self.__empty) and (n >= len(self.__cache)):
            try:
                term = next(self.__iter)
            except StopIteration:
                self.__empty = True
            else:
                self.__cache.append(term)
        if n < len(self.__cache):
            return self.__cache[n]
        return self.sentinel
    
    def _iterable(self):
        # Iterate over the generator; first in the cache range
        for n in range(self.__limit):
            term = self._retrieve(n)
            if term is self.sentinel:
                break
            yield term
        # Now, if still terms left, iterate without caching; note
        # that once we have done this once, the elements beyond
        # what the cache can hold are *not* retrievable again
        if not self.__empty:
            while True:
                try:
                    term = next(self.__iter)
                except StopIteration:
                    break
                yield term
    
    def _realize(self):
        # Realize the generator; factored out so that this can be
        # customized in subclasses (e.g., _indexhelper for the
        # indexed generator decorator)
        return self._iterable()
    
    def _itemcount(self):
        # Provided so that an exhausted generator can tell how
        # many items it generated; not used here but it accesses
        # private fields so we implement it here for use by
        # subclasses (e.g., _indexhelper)
        if self.__empty:
            return len(self.__cache)
        return None


class MemoizedGenerator(object):
    """Memoize a generator to avoid computing any term more than once.
    
    Generic implementation of a "memoized" generator for cases where each
    term of the generator is expensive to compute, but it is known that
    every realization of the generator will compute the same terms. This
    class allows multiple realizations of the generator to share a
    single computation of each term.
    
    This class can be used to wrap a generator directly, but it only
    works for ordinary functions (i.e., not methods). For ease of use
    and flexibility, it is recommended that the ``memoize_generator``
    decorator be used instead, since that automatically handles both
    ordinary functions and methods.
    
    Note that, to handle the case of generators with arguments, we
    memoize separately for each distinct set of arguments; we assume
    that each distinct argument set represents a distinct realization
    of the generator with potentially different terms, but that if the
    generator is called multiple times with the same arguments, the
    terms will be the same each time.
    
    Note also that this class is *not* thread-safe; it assumes that all
    realizations of the memoized generator run in the same thread,
    so that it is guaranteed that no more than one realization will
    be mutating the memoization fields at a time.
    """
    
    helper_class = _memohelper  # allows customizing the helper
    
    def __init__(self, gen, cachelimit=None):
        # The underlying generator
        self.__gen = gen
        # The maximum size of the cache
        self.__limit = cachelimit or sys.maxsize
    
    @cached_function
    def _get_helper(self, *args, **kwds):
        # The cached_function decorator ensures that we return the
        # same helper object for a given set of arguments. We factor
        # this method out because we don't want to apply cached_function
        # directly to the __call__ method, since we want to explicitly
        # call _realize on the helper object every time the generator
        # function is called, but only construct the object once
        return self.helper_class(self.__gen(*args, **kwds), self.__limit)
    
    def __call__(self, *args, **kwds):
        """Make instances of this class callable.
        
        This method must be present, and must return a generator
        object, so that class instances work the same as their
        underlying generators.
        """
        
        helper = self._get_helper(*args, **kwds)
        # This is what actually realizes this copy of the generator;
        # the helper object takes care of the memoization
        return helper._realize()
