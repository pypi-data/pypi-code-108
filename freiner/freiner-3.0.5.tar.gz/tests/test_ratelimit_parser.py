import re

import pytest

from freiner import limits
from freiner.util import granularity_from_string, parse, parse_many


def _test_single_rate(rl_string: str, limit: limits.RateLimitItem) -> None:
    assert parse(rl_string) == limit

    many = parse_many(rl_string)
    assert len(many) == 1
    assert many[0] == limit


@pytest.mark.parametrize("rl_string", ("1 per second", "1/SECOND", "1 / Second"))
def test_single_seconds(rl_string: str):
    _test_single_rate(rl_string, limits.RateLimitItemPerSecond(1))


@pytest.mark.parametrize("rl_string", ("1 per minute", "1/MINUTE", "1/Minute"))
def test_single_minutes(rl_string: str):
    _test_single_rate(rl_string, limits.RateLimitItemPerMinute(1))


@pytest.mark.parametrize("rl_string", ("1 per hour", "1/HOUR", "1/Hour"))
def test_single_hours(rl_string: str):
    _test_single_rate(rl_string, limits.RateLimitItemPerHour(1))


@pytest.mark.parametrize("rl_string", ("1 per day", "1/DAY", "1 / Day"))
def test_single_days(rl_string: str):
    _test_single_rate(rl_string, limits.RateLimitItemPerDay(1))


@pytest.mark.parametrize("rl_string", ("1 per month", "1/MONTH", "1 / Month"))
def test_single_months(rl_string: str):
    _test_single_rate(rl_string, limits.RateLimitItemPerMonth(1))


@pytest.mark.parametrize("rl_string", ("1 per year", "1/Year", "1 / year"))
def test_single_years(rl_string: str):
    _test_single_rate(rl_string, limits.RateLimitItemPerYear(1))


@pytest.mark.parametrize(
    ("rl_string", "expiry"),
    (
        ("2 per 6 second", 6),
        ("10 per 5 minute", 5 * 60),
        ("1 per 3 hour", 3 * 60 * 60),
        ("400 per 3 day", 3 * 24 * 60 * 60),
        ("10000 per 6 month", 6 * 30 * 24 * 60 * 60),
        ("100000 per 2 year", 2 * 12 * 30 * 24 * 60 * 60),
    ),
)
def test_multiples(rl_string: str, expiry: int):
    assert parse(rl_string).get_expiry() == expiry
    assert parse(rl_string + "s").get_expiry() == expiry
    assert parse(rl_string.replace("per", "/")).get_expiry() == expiry
    assert parse(rl_string.replace(" per ", "/")).get_expiry() == expiry
    assert parse(rl_string.replace("per", "/") + "s").get_expiry() == expiry
    assert parse(rl_string.replace(" per ", "/") + "s").get_expiry() == expiry


@pytest.mark.parametrize("sep", (",", ";", "|"))
def test_parse_two_limits(sep: str):
    def _run(limit_string: str) -> None:
        parsed = parse_many(limit_string)

        assert len(parsed) == 2

        assert parsed[0].amount == 5
        assert parsed[0].get_expiry() == 3 * 60 * 60

        assert parsed[1].amount == 2
        assert parsed[1].get_expiry() == 1

        single_parsed = parse(limit_string)
        assert single_parsed == parsed[0]

    inputs = ("5 per 3 hour", "2 per second")
    for i in range(3):
        whitespace = " " * i
        full_sep = whitespace + sep + whitespace
        inputs_string = full_sep.join(inputs)
        _run(inputs_string)


@pytest.mark.parametrize("sep", (",", ";", "|"))
def test_parse_three_limits(sep):
    def _run(limit_string: str) -> None:
        parsed = parse_many(limit_string)

        assert len(parsed) == 3

        assert parsed[0].amount == 1000
        assert parsed[0].get_expiry() == 1 * 30 * 24 * 60 * 60

        assert parsed[1].amount == 200
        assert parsed[1].get_expiry() == 4 * 24 * 60 * 60

        assert parsed[2].amount == 5
        assert parsed[2].get_expiry() == 2 * 60

        single_parsed = parse(limit_string)
        assert single_parsed == parsed[0]

    inputs = ("1000 per month", "200 per 4 days", "5 per 2 minutes")
    for i in range(3):
        whitespace = " " * i
        full_sep = whitespace + sep + whitespace
        inputs_string = full_sep.join(inputs)
        _run(inputs_string)


def test_invalid_input():
    errmsg = re.escape("Invalid rate limit string supplied.")

    with pytest.raises(TypeError, match=errmsg):
        parse(None)  # type: ignore

    with pytest.raises(TypeError, match=errmsg):
        parse_many(None)  # type: ignore


def test_invalid_string():
    errmsg = "^" + re.escape("Failed to parse rate limit string: ")

    with pytest.raises(ValueError, match=errmsg):
        parse("")

    with pytest.raises(ValueError, match=errmsg):
        parse("1 per millenium")

    with pytest.raises(ValueError, match=errmsg):
        parse_many("30 per month1 per day")

    with pytest.raises(ValueError, match=errmsg):
        parse_many("30 per month 1 per day")

    with pytest.raises(ValueError, match=errmsg):
        parse_many("1 per year; 2 per decade")

    with pytest.raises(ValueError, match=errmsg):
        parse("this won't match")


@pytest.mark.parametrize("sep", (",", ";", "|"))
def test_two_limits_with_multiple_consecutive_separators(sep: str):
    errmsg = "^" + re.escape("Failed to parse rate limit string: ")
    inputs = ("200 per day", "10 per hour")

    for i in range(3):
        for j in range(2, 5):
            whitespace = " " * i
            full_sep = whitespace + (sep * j) + whitespace
            inputs_string = full_sep.join(inputs)
            with pytest.raises(ValueError, match=errmsg):
                parse_many(inputs_string)


@pytest.mark.parametrize("sep", (",", ";", "|"))
def test_three_limits_with_multiple_consecutive_separators(sep: str):
    errmsg = "^" + re.escape("Failed to parse rate limit string: ")
    inputs = ("1200 per day", "50 per hour", "1 per minute")

    for i in range(3):
        for j in range(2, 5):
            whitespace = " " * i
            full_sep = whitespace + (sep * j) + whitespace
            inputs_string = full_sep.join(inputs)
            with pytest.raises(ValueError, match=errmsg):
                parse_many(inputs_string)


def test_unknown_granularity():
    errmsg = "^" + re.escape("No granularity matched for: ")

    with pytest.raises(ValueError, match=errmsg):
        granularity_from_string("millenium")
