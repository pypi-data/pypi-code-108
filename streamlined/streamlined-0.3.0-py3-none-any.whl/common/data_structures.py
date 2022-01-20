from __future__ import annotations

from collections import UserDict, defaultdict
from typing import (
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Set,
    Type,
    TypeVar,
    Union,
)

K = TypeVar("K")
V = TypeVar("V")


class Bag(UserDict, Generic[K, V]):
    """
    A bag is essentially a wrapper of `defaultdict(set)` with the following additional functionality:

    `self[key] = item` is equivalent to `self[key].add(item)`
    """

    data: Dict[K, Set[V]]

    def __init__(self) -> None:
        self.data = defaultdict(set)

    def bag(self) -> Dict[K, Set[V]]:
        return self.data

    def __setitem__(self, key: K, item: V) -> None:
        return self.data[key].add(item)


IndexFactory = Callable[[], Mapping[K, Iterable[V]]]


class BidirectionalIndex(UserDict, Generic[K, V]):
    """
    BidirectionalIndex has two indexing system: forward index and inverted index.

    For example, consider a list of documents. Forward index means finding the set of words from a document while inverted index means finding the set of documents containing that word.

    Notes
    --------
    Only __getitem__ and __setitem__ are implemented in this base class.
    Additional functionalities should be provided by subclasses.

    See Also
    --------
    [Inverted Index](https://en.wikipedia.org/wiki/Inverted_index)
    """

    DEFAULT_FORWARD_INDEX_FACTORY: ClassVar[Type[Bag[K, V]]] = Bag
    DEFAULT_INVERTED_INDEX_FACTORY: ClassVar[Type[Bag[K, V]]] = Bag

    def __init__(
        self,
        forward_index_factory: Optional[IndexFactory[K, V]] = None,
        inverted_index_factory: Optional[IndexFactory[V, K]] = None,
    ) -> None:
        self.__init_index(forward_index_factory, inverted_index_factory)

    def __init_index(
        self,
        forward_index_factory: Optional[IndexFactory[K, V]] = None,
        inverted_index_factory: Optional[IndexFactory[V, K]] = None,
    ) -> None:
        if forward_index_factory is None:
            forward_index_factory = self.DEFAULT_FORWARD_INDEX_FACTORY
        if inverted_index_factory is None:
            inverted_index_factory = self.DEFAULT_INVERTED_INDEX_FACTORY

        self.data = forward_index_factory()
        self.inverted_index = inverted_index_factory()

    @property
    def forward_index(self) -> Mapping[K, V]:
        return self.data

    def __getitem__(self, key: Union[K, V]) -> Union[Sequence[V], Sequence[K]]:
        try:
            return self.forward_index[key]
        except KeyError:
            return self.inverted_index[key]

    def __setitem__(self, key: K, item: V) -> None:
        super().__setitem__(key, item)
        self.inverted_index[item] = key
