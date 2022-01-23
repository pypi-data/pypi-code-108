import re
from typing import Sequence, Type, cast

from .limits import GRANULARITIES, RateLimitItem


SEPARATORS = re.compile(r"[,;|]")
SINGLE_EXPR = re.compile(
    r"""
    \s*([0-9]+)
    \s*(?:/|\s*per\s*)
    \s*([0-9]+)
    *\s*(hour|minute|second|day|month|year)s?\s*""",
    re.IGNORECASE | re.VERBOSE,
)
EXPR = re.compile(
    r"^{SINGLE}(?:{SEPARATORS}{SINGLE})*$".format(
        SINGLE=SINGLE_EXPR.pattern, SEPARATORS=SEPARATORS.pattern
    ),
    re.IGNORECASE | re.VERBOSE,
)


def parse_many(limit_string: str) -> Sequence[RateLimitItem]:
    """
    Parses rate limits in string notation containing multiple rate limits
    (e.g. '1/second; 5/minute').

    :param limit_string: The rate limit string. using :ref:`ratelimit-string`.
    :raises TypeError: If something other than a string was supplied.
    :raises ValueError: If the string notation is invalid.
    :return: A sequence of :class:`freiner.limits.RateLimitItem` instances.
    """

    if not isinstance(limit_string, str):
        raise TypeError("Invalid rate limit string supplied.")

    if not EXPR.match(limit_string):
        raise ValueError(f"Failed to parse rate limit string: {limit_string}")

    limits = []
    for limit in SEPARATORS.split(limit_string):
        # This cast is fine because we already verified that it will match
        # in the EXPR.match check above.
        limit_match = cast(re.Match, SINGLE_EXPR.match(limit))
        amount, multiples, granularity_string = limit_match.groups()
        granularity = granularity_from_string(granularity_string)
        limits.append(granularity(amount, multiples))

    return tuple(limits)


def parse(limit_string: str) -> RateLimitItem:
    """
    Parses a single rate limit in string notation (e.g. '1/second' or '1 per second').

    # noqa: DAR402

    :param limit_string: The rate limit string. using :ref:`ratelimit-string`.
    :raises TypeError: If something other than a string was supplied.
    :raises ValueError: If the string notation is invalid.
    :return: An instance of :class:`freiner.limits.RateLimitItem`.
    """

    return parse_many(limit_string)[0]


def granularity_from_string(granularity_string: str) -> Type[RateLimitItem]:
    """
    :param granularity_string: A representation of the granularity (eg. "second", "minute").
    :raises ValueError: If the supplied granularity is unknown.
    :return: A subclass of :class:`freiner.limits.RateLimitItem`.
    """

    for granularity in GRANULARITIES.values():
        if granularity.check_granularity_string(granularity_string):
            return granularity

    raise ValueError(f"No granularity matched for: {granularity_string}")
