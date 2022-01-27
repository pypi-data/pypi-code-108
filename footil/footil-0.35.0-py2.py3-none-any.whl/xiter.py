"""Some iteration helpers."""
from typing import Iterable


def iterate_limit(iterable: Iterable, limit: int = -1):
    """Iterate items up to specified limit.

    If limit is greater than items in iterable, it will stop gracefully.

    Args:
        iterable: to iterate safely.
        limit: how many items to iterate. -1 means all (default: {-1}).

    Yields:
        next item in iterable

    """
    while limit:
        try:
            item = next(iterable)
            yield item
        except StopIteration:
            break
        limit -= 1
