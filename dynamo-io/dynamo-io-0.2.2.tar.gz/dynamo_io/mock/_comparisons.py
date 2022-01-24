import datetime
import fnmatch
import re
import typing

Assertion = typing.Callable[[str, str], None]


def _from_iso(
    iso_value: typing.Union[str, datetime.datetime]
) -> typing.Optional[datetime.datetime]:
    """Converts and ISO string into a Datetime object."""
    if not iso_value:
        return None

    if hasattr(iso_value, "year"):
        return typing.cast(datetime.datetime, iso_value)

    return datetime.datetime.fromisoformat(
        typing.cast(str, iso_value).replace("+00:00", "").rstrip("Z")
    )


def is_iso(
    min_value: datetime.datetime = None,
    max_value: datetime.datetime = None,
    year: int = None,
    month: int = None,
    day: int = None,
    hour: int = None,
    minute: int = None,
    second: int = None,
    nullable: bool = False,
) -> Assertion:
    """
    Checks that the string value is an ISO datetime with the optionally
    specified constraints.
    """

    def assert_is_iso(key: str, value: str):
        if not value and nullable:
            return

        prefix = f'Expected the ISO datetime value of the "{key}"'

        assert value is not None, f"{prefix} not to be None."

        try:
            dt = typing.cast(datetime.datetime, _from_iso(value))
        except Exception:
            raise ValueError(f"{prefix} to be an ISO datetime string.")

        if min_value is not None:
            assert dt >= min_value, f"{prefix} to be a more recent value."
        if max_value is not None:
            assert dt <= max_value, f"{prefix} to be a less recent value."
        if year is not None:
            assert dt.year == year, f"{prefix} to be the year {year}."
        if month is not None:
            assert dt.month == month, f"{prefix} to be the month {month}."
        if day is not None:
            assert dt.day == day, f"{prefix} to be the day {day}."
        if hour is not None:
            assert dt.hour == hour, f"{prefix} to be the hour {hour}."
        if minute is not None:
            assert dt.minute == minute, f"{prefix} to be the minute {minute}."
        if second is not None:
            assert dt.second == second, f"{prefix} to be the second {second}."

    return assert_is_iso


def is_match(regex: str, nullable: bool = False, groups: dict = None) -> Assertion:
    """Determines if the value matches the regular expression."""

    def assert_is_match(key: str, value: str):
        if nullable and value is None:
            return

        prefix = f'Expected the value of the "{key}"'

        match = re.compile(regex).match(value)
        assert match is not None, f'{prefix} to match the pattern "{regex}".'

        for group_key, group_value in (groups or {}).items():
            assert (
                match["group"] == group_value
            ), f"""
                {prefix} to have the matching group "{group_key}" to
                have the value "{group_value}" and not "{match['group']}".
                """

    return assert_is_match


def is_like(
    comparison: str,
    ignore_case: bool = False,
    nullable: bool = True,
) -> Assertion:
    """
    Determines if the value matches the comparison using shell-style
    wildcard patterns.
    """

    def assert_is_like(key: str, value: str):
        if nullable and value is None:
            return

        test = fnmatch.fnmatch if ignore_case else fnmatch.fnmatchcase
        assert test(
            value, comparison
        ), f"""
            Expected the value of the "{key}" to match the specified
            comparison "{comparison}" != "{value}".
            """

    return assert_is_like


def is_optional(comparison: str) -> Assertion:
    """
    Determines if the string value matches the comparison but also allows
    for a None value to be applied.
    """

    def assert_is_optional(key: str, value: str):
        if value is None:
            return

        assert (
            value == comparison
        ), f"""
            Expected the value of "{key}" to match the specified
            value of "{comparison}" instead of "{value}".
            """

    return assert_is_optional


def is_anything() -> Assertion:
    """Allows any value."""

    def assert_is_anything(key: str, value: str):
        return

    return assert_is_anything


def is_in(allowed: typing.List[typing.Any]) -> Assertion:
    """Allows any of the values in the specified list."""

    def assert_id_in(key: str, value: str):
        assert (
            value in allowed
        ), f"""
            Expected the value of "{key}" to be one of the allowed
            values and instead found it to be {value}.
            """

    return assert_id_in


def is_not_null() -> Assertion:
    """Ensures that the value is not None."""

    def assert_is_not_null(key: str, value: typing.Any):
        assert (
            value is not None
        ), f"""
            Expected the value of "{key}" not to be None.
            """

    return assert_is_not_null


def is_not(exclusions: typing.List[typing.Any]) -> Assertion:
    """Ensures that the value is not any of the specified argument values."""

    def assert_is_not(key: str, value: typing.Any):
        assert (
            value not in exclusions
        ), f"""
            Expected the value of "{key}" not to be any of {exclusions},
            but it was "{value}".
            """

    return assert_is_not


def is_instance_of(*args: typing.Any) -> Assertion:
    """Ensures that the value is one of the specified types."""

    def assert_is_instance_of(key: str, value: typing.Any):
        assert isinstance(
            value, args
        ), f"""
            Expected the value of "{key}" to be of one of the types
            {args}, but it was "{type(value)}" instead.
            """

    return assert_is_instance_of
