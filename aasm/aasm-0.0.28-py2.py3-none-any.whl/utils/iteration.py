from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, TypeVar

if TYPE_CHECKING:
    T = TypeVar("T")


def zip_consecutive_pairs(iterable: List[T]) -> List[Tuple[T, ...]]:
    if len(iterable) % 2 != 0:
        raise Exception("Iterable must have an even number of elements")
    iterator = iter(iterable)
    double_iterator = [iterator] * 2
    return list(zip(*double_iterator))
