from bisect import bisect
from copy import deepcopy
from typing import (Callable, Dict, Generic, Optional, Sequence, Tuple,
                    TypeVar,
                    Union)

from .rng import RNG

ITEM = TypeVar('ITEM')

ITEMS = Union[Sequence[Tuple[ITEM, float]], Dict[ITEM, float]]


class WeightedCollection(Generic[ITEM]):
    """
    A collection of weighted items.  A random item can be chosen from this
    collection.  The probability of chosing an item is w/total, where w is
    the item's weight, and total is the sum of all weights in the collection.
    """

    def __init__(self, items: Optional[ITEMS] = None,
                 rng: Optional[RNG] = None):
        """
        A collection of weighted items.
        :param items: a list of (item, weight) pairs or a dictionary of
        item->weight pairs
        :param rng: the random number generator to use.  If None, an RNG
        must be passed as an argument to the choose member function.
        """
        self._rng = rng
        self._items = list()
        self._weights = list()
        self._iweights = None
        if items is not None:
            if isinstance(items, Dict):
                for i, w in items.items():
                    self.add(i, w)
            elif isinstance(items, Sequence):
                for i, w in items:
                    self.add(i, w)
            else:
                raise TypeError(f"items must be a sequence of (item, float) "
                                f"tuples or a dict of item->float.  "
                                f"Type of items = {type(items)}")

    def add(self, item: ITEM, weight: float):
        """
        Add an item with an associated weight to the collection
        :param item: item to add to the collection.
        :param weight: the weight associated with this item.  if weight<=0,
        the item will not be added to the collection.
        """

        self._items.append(deepcopy(item))
        self._weights.append(weight)
        self._iweights = None

    def choose(self, rng: Optional[RNG] = None) -> ITEM:
        """
        Return a random item from this collection
        :param rng: the random number generator to use.  If this argument
        is None, the rng passed to the constructor is used.  It is an error
        to invoke this member function with rng=None if an rng was not
        passed to the constructor.
        :return: a random item from the collection.
        """
        if len(self._items) == 0:
            raise ValueError("This collection is Empty.")
        if rng is None:
            rng = self._rng
        if self._iweights is None:
            self._recalc_iweights()
        p = rng.fr(0, self._iweights[-1])
        idx = bisect(self._iweights, p)
        return self._items[idx]

    def reweight_items(self, weight_func: Callable[[ITEM, float], float]) -> \
            'WeightedCollection[ITEM]':
        """
        Reassign weights to items in this collection, and return a new
        collection with the associated weights.
        :param weight_func: a function that assigns a new weight to each
        item in the collection.  The function must take (item, weight) as
        arguments.
        :return: new weighted collection
        """
        result = []
        for i in range(len(self._items)):
            item = self._items[i]
            old_weight = self._weights[i]
            w = weight_func(item, old_weight)
            if w > 0:
                item = deepcopy(item)
                result.append((item, w))
        return WeightedCollection[ITEM](result, self._rng)

    def _recalc_iweights(self):
        """
        Rebuilds the internal _iweights field.  This must be done whenever
        the collection is altered.
        """
        t = 0.0
        self._iweights = list()
        for w in self._weights:
            t += w
            self._iweights.append(t)

    def __len__(self):
        return len(self._items)
