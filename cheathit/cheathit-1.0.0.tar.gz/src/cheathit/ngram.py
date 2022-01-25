from __future__ import annotations

__all__ = [
    'Ngram',
]


class Ngram:
    _hash: int
    _length: int

    @property
    def length(self) -> int:
        return self._length

    def __init__(self) -> None:
        self._hash = hash('')
        self._length = 0

    def add(self, token: str) -> Ngram:
        ngram = Ngram.__new__(Ngram)
        ngram._hash = hash(str(self._hash) + token)
        ngram._length = self._length + 1
        return ngram

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: Ngram) -> bool:
        return self._hash == other._hash
