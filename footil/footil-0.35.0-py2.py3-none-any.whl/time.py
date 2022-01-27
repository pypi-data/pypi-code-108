"""Helpers for time calculations."""

HOUR_MINUTES = 60
DAY_HOURS = 24


def __convert_unit(amount: int, unit: int) -> tuple:
    return (amount // unit, amount % unit)


def minutes_to_hours(minutes: int) -> tuple:
    """Convert minutes into hours and remaining part as minutes."""
    if minutes >= HOUR_MINUTES:
        return __convert_unit(minutes, HOUR_MINUTES)
    return (0, minutes)


def hours_to_days(hours: int) -> tuple:
    """Convert hours into days and remaining part as hours."""
    if hours >= DAY_HOURS:
        return __convert_unit(hours, DAY_HOURS)
    return (0, hours)

# TODO: implement generic conversion from one time unit to another.
