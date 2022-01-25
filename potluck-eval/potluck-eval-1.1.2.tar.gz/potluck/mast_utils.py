"""
Utils from codder which are necessary for the mast module.

mast_utils.py
"""

# Attempts at 2/3 dual compatibility:
from __future__ import print_function

try: # Python 3
    from collections.abc import Iterable
except Exception: # Python 2
    from collections import Iterable


class Some(object):
    """
    An ML-inspired option for Python.  Pair with None.
    """
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def dump(self, dumper):
        return 'Some({})'.format(dumper(self.value))

    def __repr__(self):
        return 'Some({})'.format(self.value)


# pure dictionary ops

def dict_bind(d, binding):
    """Return a copy of d with binding added."""
    di = d.copy()
    key, val = binding
    di[key] = val
    return di


def dict_unbind(d, remove_key):
    """Return a copy of d with remove_key unbound."""
    di = d.copy()
    del di[remove_key]
    return di
    # return {k: v for k, v in d.items() if k != remove_key}


# generator/iterator convenience functions

def takeone(it):
    """Return Some(first value yielded by gen) or None if no values yielded."""
    for x in it:
        assert x is not None
        return Some(x)
    return None


def iterone(elem):
    """Produce an iterator over a single element with printable contents"""
    # return iter([elem])
    return FiniteIterator([elem])


def iterempty():
    """Produce an empty iterator with printable contents"""
    # return iter([])
    return FiniteIterator([])


class FiniteIterator(Iterable):
    '''An iterator with a finite number of elements left to iterate.'''

    def __init__(self, elts):
        self.elts = elts
        self.nextIndex = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.nextIndex >= len(self.elts):
            raise StopIteration
        else:
            self.nextIndex += 1
            return self.elts[self.nextIndex - 1]

    def __len__(self):
        return len(self.elts - (self.nextIndex + 1))

    def dump(self, dumper):
        return '<FiniteIterator({})>'.format(
            ','.join(dumper(elt) for elt in self.elts))

    def __repr__(self):
        return '<FiniteIterator({})>'.format(
            ','.join(str(elt) for elt in self.elts))
