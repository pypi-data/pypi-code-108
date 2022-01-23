from functools import total_ordering
from typing import Any, Dict, Type, cast


def safe_string(value: Any) -> str:
    """
    Consistently converts a value to a string.

    :param value: The value to stringify.
    """

    if isinstance(value, bytes):
        return value.decode()
    return str(value)


TIME_TYPES = {
    "year": (60 * 60 * 24 * 30 * 12, "year"),
    "month": (60 * 60 * 24 * 30, "month"),
    "day": (60 * 60 * 24, "day"),
    "hour": (60 * 60, "hour"),
    "minute": (60, "minute"),
    "second": (1, "second"),
}

GRANULARITIES: Dict[str, Type["RateLimitItem"]] = {}


class RateLimitItemMeta(type):
    def __new__(cls, name, parents, dct):
        granularity = cast(
            Type["RateLimitItem"], super(RateLimitItemMeta, cls).__new__(cls, name, parents, dct)
        )
        if "granularity" in dct:
            GRANULARITIES[dct["granularity"][1]] = granularity
        return granularity


@total_ordering
class RateLimitItem(metaclass=RateLimitItemMeta):
    """
    defines a Rate limited resource which contains the characteristic
    namespace, amount and granularity multiples of the rate limiting window.

    :param amount: The amount of hits that can be sustained within the given period (e.g. X in 'x per y seconds').
    :param multiples: Multiple of the 'per' granularity (e.g. Y in 'x per y seconds').
    :param namespace: An arbitrary namespace for this rate limit.
    """

    granularity = (0, "")

    def __init__(self, amount: int, multiples: int = 1, namespace: str = "LIMITER") -> None:
        self.namespace = namespace
        self.amount = int(amount)
        self.multiples = int(multiples or 1)

    @classmethod
    def check_granularity_string(cls, granularity_string: str) -> bool:
        """
        Check if this class matches a granularity string of type 'N per hour' etc.

        :param granularity_string: The granularity to match against.
        :return: Does the supplied granularity identifier match this class' granularity?
        """

        return granularity_string.lower() in cls.granularity[1:]

    def get_expiry(self) -> int:
        """
        :return: The length of the expiry window in seconds.
        """

        return self.granularity[0] * self.multiples

    def key_for(self, *identifiers: Any) -> str:
        """
        :param identifiers: A list of arbitrary strings to append to the key.
        :return: A string key identifying this resource with each identifier appended with a '/' delimiter.
        """

        identifier_strings = [safe_string(k) for k in identifiers]
        limit_strings = [safe_string(self.amount), safe_string(self.multiples), self.granularity[1]]

        remainder = "/".join(identifier_strings + limit_strings)
        return "{}/{}".format(self.namespace, remainder)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, RateLimitItem)
            and self.amount == other.amount
            and self.granularity == other.granularity
        )

    def __str__(self) -> str:
        return "{} per {} {}".format(self.amount, self.multiples, self.granularity[1])

    def __repr__(self) -> str:
        return "{}<{}>".format(self.__class__.__name__, str(self))

    def __lt__(self, other) -> bool:
        return isinstance(other, RateLimitItem) and self.granularity[0] < other.granularity[0]


class RateLimitItemPerYear(RateLimitItem):
    """
    Per year rate limited resource.
    """

    granularity = TIME_TYPES["year"]


class RateLimitItemPerMonth(RateLimitItem):
    """
    Per month rate limited resource.
    """

    granularity = TIME_TYPES["month"]


class RateLimitItemPerDay(RateLimitItem):
    """
    Per day rate limited resource.
    """

    granularity = TIME_TYPES["day"]


class RateLimitItemPerHour(RateLimitItem):
    """
    Per hour rate limited resource.
    """

    granularity = TIME_TYPES["hour"]


class RateLimitItemPerMinute(RateLimitItem):
    """
    Per minute rate limited resource.
    """

    granularity = TIME_TYPES["minute"]


class RateLimitItemPerSecond(RateLimitItem):
    """
    Per second rate limited resource.
    """

    granularity = TIME_TYPES["second"]
