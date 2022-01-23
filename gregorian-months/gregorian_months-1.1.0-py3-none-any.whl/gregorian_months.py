MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def get_number(month_name: str):
    """
    Gets month number by its name.
    Args:
        month_name: Given month.
    Returns:
        Number of the given month if valid.
    Raises:
        TypeError if the month_name is not a string.
        ValueError if the given month does not exist.
    """
    try:
        return MONTHS.index(month_name.capitalize()) + 1
    except AttributeError:
        raise TypeError("month_name must be from type str") from None
    except ValueError:
        raise ValueError(f"There is no month named '{month_name}'!") from None
