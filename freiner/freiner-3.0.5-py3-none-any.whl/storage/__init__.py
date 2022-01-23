from typing import NamedTuple

from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class FixedWindowStorage(Protocol):
    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        Increments the counter for the given rate limit key.

        # noqa: DAR202

        :param key: The key to increment.
        :param expiry: Amount in seconds for the key to expire in.
        :param elastic_expiry: Whether to keep extending the rate limit window every hit.
        :return: The number of hits currently on the rate limit for the given key.
        """

    def get(self, key: str) -> int:
        """
        Retrieve the current request count for the given rate limit key.

        :param key: The key to get the counter value for.
        """

    def get_expiry(self, key: str) -> float:
        """
        Retrieve the expected expiry time for the given rate limit key.

        # noqa: DAR202

        :param key: The key to get the expiry time for.
        :return: The time at which the current rate limit for the given key ends.
        """

    def clear(self, key: str) -> None:
        """
        Resets the rate limit for the given key.

        :param key: The key to clear rate limits for.
        """


class MovingWindow(NamedTuple):
    start_time: float
    acquired_count: int


@runtime_checkable
class MovingWindowStorage(Protocol):
    def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
        """
        :param key: The rate limit key to acquire an entry in.
        :param limit: The total amount of entries allowed before hitting the rate limit.
        :param expiry: Amount in seconds for the acquired entry to expire in.
        :param no_add: If False, an entry is not actually acquired but instead serves as a 'check'.
        """

    def get_moving_window(self, key: str, limit: int, expiry: int) -> MovingWindow:
        """
        Retrieves the starting point and the number of entries in the moving window.

        # noqa: DAR202

        :param key: The rate limit key to retrieve statistics about.
        :param limit: The total amount of entries allowed before hitting the rate limit.
        :param expiry: Amount in seconds for the acquired entry to expire in.
        :return: (start of window, number of acquired entries)
        """

    def clear(self, key: str) -> None:
        """
        Resets the rate limit for the given key.

        :param key: The key to clear rate limits for.
        """


__all__ = [
    "FixedWindowStorage",
    "MovingWindow",
    "MovingWindowStorage",
]
