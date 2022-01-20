MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def get_number(month_name: str):
    """
    Gets gregorian month number by its name.
    """
    try:
        return MONTHS[month_name.capitalize()]
    except AttributeError:
        raise TypeError("month_name must be from type str") from None
    except KeyError:
        raise ValueError(f"{month_name} is not a gregorian month.") from None
