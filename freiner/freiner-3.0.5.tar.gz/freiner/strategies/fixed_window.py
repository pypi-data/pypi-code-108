from typing import Any

from freiner.limits import RateLimitItem
from freiner.storage import FixedWindowStorage

from . import WindowStats


class FixedWindowRateLimiter:
    """
    Reference: :ref:`fixed-window`
    """

    def __init__(self, storage: FixedWindowStorage) -> None:
        if not isinstance(storage, FixedWindowStorage):
            msg = f"Fixed Window rate limiting is not implemented for storage of type {storage.__class__.__name__}"
            raise TypeError(msg)

        self.storage: FixedWindowStorage = storage

    def hit(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        Creates a hit on the rate limit and returns ``True`` if successful.

        :param item: A :class:`freiner.limits.RateLimitItem` instance.
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: ``True`` if the request was successful, or ``False`` if the rate limit had been exceeded.
        """

        return self.storage.incr(item.key_for(*identifiers), item.get_expiry()) <= item.amount

    def test(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        Checks the rate limit and returns ``True`` if it is not currently exceeded.

        :param item: A :class:`freiner.limits.RateLimitItem` instance.
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: ``True`` if the rate limit has not yet been exceeded, or ``False`` if it has.
        """

        return self.storage.get(item.key_for(*identifiers)) < item.amount

    def get_window_stats(self, item: RateLimitItem, *identifiers: Any) -> WindowStats:
        """
        Returns the number of requests remaining within this limit.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: tuple (reset time (float), remaining (int))
        """

        remaining = max(0, item.amount - self.storage.get(item.key_for(*identifiers)))
        reset = self.storage.get_expiry(item.key_for(*identifiers))
        return WindowStats(reset, remaining)

    def clear(self, item: RateLimitItem, *identifiers: Any) -> None:
        """
        Resets the request counter for a given limit to zero.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        """

        self.storage.clear(item.key_for(*identifiers))


__all__ = [
    "FixedWindowRateLimiter",
]
