from typing import Any, NamedTuple

from typing_extensions import Protocol, runtime_checkable

from freiner.limits import RateLimitItem


class WindowStats(NamedTuple):
    reset_time: float
    remaining_count: int


@runtime_checkable
class RateLimiter(Protocol):
    def hit(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        Creates a hit on the rate limit and returns ``True`` if successful.

        # noqa: DAR202

        :param item: A :class:`freiner.limits.RateLimitItem` instance.
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: ``True`` if the request was successful, or ``False`` if the rate limit had been exceeded.
        """

    def test(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        Checks the rate limit and returns ``True`` if it is not currently exceeded.

        # noqa: DAR202

        :param item: A :class:`freiner.limits.RateLimitItem` instance.
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: ``True`` if the rate limit has not yet been exceeded, or ``False`` if it has.
        """

    def get_window_stats(self, item: RateLimitItem, *identifiers: Any) -> WindowStats:
        """
        Retrieve statistics about the number of requests remaining within the given limit.

        # noqa: DAR202

        :param item: A :class:`freiner.limits.RateLimitItem` instance.
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: tuple (reset time (float), remaining (int))
        """

    def clear(self, item: RateLimitItem, *identifiers: Any) -> None:
        """
        Resets the request counter for a given limit to zero.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        """


__all__ = [
    "RateLimiter",
    "WindowStats",
]
