from __future__ import annotations

from typing import Iterable
import heapq

class MergeSortedIterators:
    def __init__(self, iterables: Iterable[Iterable[int]]) -> None:
        self.iterators = [iter(it) for it in iterables]
        self.heap = []

        for idx, iterator in enumerate(self.iterators):
            try:
                value = next(iterator)
                self.heap.append((value, idx))
            except StopIteration:
                pass

        heapq.heapify(self.heap)
        
    def _take_next_from_iterator(self, idx: int) -> None:
        assert 0 <= idx < len(self.iterators)

        try:
            value = next(self.iterators[idx])
            heapq.heappush(self.heap, (value, idx))
        except StopIteration:
            pass

    def __iter__(self) -> MergeSortedIterators:
        return self

    def __next__(self) -> int:
        if not self.heap:
            raise StopIteration

        value, idx = heapq.heappop(self.heap)
        self._take_next_from_iterator(idx)
        return value
