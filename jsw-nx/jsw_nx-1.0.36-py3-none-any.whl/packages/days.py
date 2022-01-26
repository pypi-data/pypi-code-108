STICK_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def days(year, month):
    """
    Return the number of days in a month.
    """
    if month == 2 and year % 4 == 0:
        return 29
    return STICK_DAYS[month - 1]
