from __future__ import annotations
from typing import Iterator, Optional

from .ngram import Ngram

__all__ = [
    'NgramCollection',
]


class NgramCollection:
    tokens: list[str]
    _collection: dict[Ngram, tuple[int, ...]]

    def __init__(self, tokens: list[str], min_n: int, max_n: int) -> None:
        self.tokens = tokens
        self._collection = {}
        for start in range(len(tokens) - min_n + 1):
            ngram = Ngram()
            for offset in range(min(max_n, len(tokens) - start)):
                ngram = ngram.add(tokens[start + offset])
                if offset + 1 >= min_n:
                    self._collection[ngram] = self._collection.get(ngram, ()) + (start,)

    def __iter__(self) -> Iterator[Ngram]:
        return iter(self._collection.keys())

    def count_common_tokens(self, other: NgramCollection, excluded: set[Ngram]) -> int:
        markers = [0] * len(self.tokens)
        for ngram, positions in self._collection.items():
            if ngram not in excluded and ngram in other._collection.keys():
                for position in positions:
                    markers[position] = max(markers[position], ngram.length)
        common = 0
        remaining = 0
        for marker in markers:
            remaining = max(remaining, marker)
            if remaining > 0:
                common += 1
                remaining -= 1
        return common

    def longest_common(self, other: NgramCollection, excluded: set[Ngram]) -> Optional[list[str]]:
        common = set(self._collection.keys()).intersection(other._collection.keys()) - excluded
        if common:
            longest = max(common, key=lambda ngram: ngram.length)
            start = self._collection[longest][0]
            return self.tokens[start:start + longest.length]
        else:
            return None
