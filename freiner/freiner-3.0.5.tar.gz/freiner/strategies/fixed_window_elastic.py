from typing import Any

from freiner.limits import RateLimitItem

from .fixed_window import FixedWindowRateLimiter


class FixedWindowElasticExpiryRateLimiter(FixedWindowRateLimiter):
    """
    Reference: :ref:`fixed-window-elastic`
    """

    def hit(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        Creates a hit on the rate limit and returns ``True`` if successful.

        :param item: A :class:`freiner.limits.RateLimitItem` instance.
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: ``True`` if the request was successful, or ``False`` if the rate limit had been exceeded.
        """

        counter = self.storage.incr(
            item.key_for(*identifiers), item.get_expiry(), elastic_expiry=True
        )
        return counter <= item.amount


__all__ = [
    "FixedWindowElasticExpiryRateLimiter",
]
