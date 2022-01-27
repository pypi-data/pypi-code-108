"""Module for collections helpers."""
from collections.abc import Sequence
from typing import Optional, Callable, List, Tuple, Any


def batch(seq: Sequence, size: int) -> Sequence:
    """Yield sequence in batches by specified size.

    Args:
        seq: sequence to split into batches.
        size: size of a single batch.

    Returns:
        sequence batches

    """
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def to_intervals(
    sequence: Sequence,
    no_dupes: bool = False,
    sort: bool = False,
    key: Optional[Callable] = None,
        reverse: bool = False) -> List[Tuple[Any, Any]]:
    """Convert items into intervals.

    Example: [1, 51, 101] -> [(1, 51), (51, 101)].

    Args:
        sequence: sequence to convert into intervals.
        no_dupes: whether to remove duplicate items.
        sort: whether to sort sequence before converting to intervals.
        key: optional sort function (used only if sort=True).
        reverse: whether to sort in reverse (used only if sort=True).

    """
    intervals = []
    if no_dupes:
        # Since Python 3.6, dict preserves order, so we can make
        # advantage of it.
        sequence = list(dict.fromkeys(sequence))
    if sort:
        sequence = sorted(sequence, key=key, reverse=reverse)
    for index, item in enumerate(sequence):
        try:
            next_item = sequence[index + 1]
        except IndexError:
            break
        intervals.append((item, next_item))
    return intervals
