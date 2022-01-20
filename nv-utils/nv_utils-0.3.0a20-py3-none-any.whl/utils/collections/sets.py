import sys
from collections.abc import MutableSet, Set, Sequence
from collections import OrderedDict
from itertools import repeat
from typing import TypeVar, Iterable, Iterator


__ALL__ = ['OrderedSet']


_KEY_ONLY = object()

V = TypeVar('V')


class OrderedSet(MutableSet[V]):
    """
    Since CPython 3.6, dictionaries are ordered at implementation and tend to be much faster than any pure
    Python implementation. For versions older than 3.6, OrderedDict is used instead.

    OrderedSet is a wrapper over an ordered dict. Set values are stored as keys. All values point to the same
    dummy object (_KEY_ONLY).
    """

    OrderedMapping = dict if sys.version_info >= (3, 6) else OrderedDict

    def __init__(self, items: Iterable[V] | None = None):
        self.__mapping = self.OrderedMapping(zip(items, repeat(_KEY_ONLY))) if items else self.OrderedMapping()

    def add(self, value: V):
        self.__mapping.update({value: _KEY_ONLY})

    def discard(self, value: V):
        del self.__mapping[value]

    def __contains__(self, x: object) -> bool:
        return x in self.__mapping

    def __len__(self) -> int:
        return len(self.__mapping)

    def __iter__(self) -> Iterator[V]:
        return iter(self.__mapping)

    def __eq__(self, other):
        if isinstance(other, OrderedSet | Sequence):
            return len(self) == len(other) and list(self) == list(other)
        elif isinstance(other, Set):
            return set(self) == other
        else:
            return NotImplemented

    def __repr__(self):
        return f'{self.__class__.__name__}({list(self)!r})'
