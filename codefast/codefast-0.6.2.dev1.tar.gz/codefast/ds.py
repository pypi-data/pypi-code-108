import heapq
import random
import re
from collections.abc import Iterable
from typing import Any, List


class fplist(list):
    '''List support more functionnal programming methods.'''
    @property
    def last(self):
        return self[-1]

    @property
    def first(self):
        return self[0]

    @property
    def second(self):
        return self[1]

    @property
    def size(self):
        return len(self)

    @property
    def len(self):
        return len(self)

    @property
    def length(self):
        return len(self)

    def chunks(self, n: int) -> List[List]:
        '''Yield successive n-sized chunks from self'''
        for i in range(0, len(self), n):
            yield self[i:i + n]


class PriorityQueue:
    def __init__(self):
        self._ds = []

    def push(self, item: Any) -> bool:
        heapq.heappush(self._ds, item)
        return True

    def pop(self) -> Any:
        return heapq.heappop(self._ds)

    def is_empty(self) -> bool:
        return len(self._ds) == 0

    @property
    def size(self) -> int:
        return len(self._ds)

    @property
    def length(self) -> int:
        return len(self._ds)

    def nsmallest(self, count: int) -> list:
        return heapq.nsmallest(count, self._ds)

    def nlargest(self, count: int) -> list:
        return heapq.nlargest(count, self._ds)

    @property
    def first(self) -> Any:
        return heapq.nsmallest(1, self._ds)[0]

    @property
    def last(self) -> Any:
        return heapq.nlargest(1, self._ds)[0]

    def __getitem__(self, idx: int):
        return self._ds[idx]

    def __repr__(self):
        _str = ''
        for item in self._ds:
            _str += ', '.join(repr(e) for e in item) + '\n'
        return _str


class nstr(str):
    @property
    def last(self):
        return self[-1]

    @property
    def first(self):
        return self[0]

    @property
    def size(self):
        return len(self)

    @property
    def length(self):
        return len(self)

    def __add__(self, s: str) -> str:
        return nstr(super().__add__(s))

    def __mul__(self, n: int) -> str:
        return nstr(super().__mul__(n))

    def is_cn(self) -> bool:
        return True if re.search(u'[\u4e00-\u9fff]', self) else False

    def is_cn_or_punc(self) -> bool:
        if self.is_cn():
            return True
        punctuations = '，。？！；：、【】（）《》——'
        return self in punctuations


def pair_sample(la: list, lb: list, ratio: float, stable: bool = False):
    '''set stable = True to ensure same result
    '''
    assert len(la) == len(lb), 'size of two list is different.'
    if stable:
        random.seed(63)
    m = int(len(la) * ratio) if ratio <= 1 else min(int(ratio), len(la))
    _pair = zip(*random.sample(list(zip(la, lb)), m))
    random.seed(None)
    return _pair


def flatten(l: List) -> List:
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el
