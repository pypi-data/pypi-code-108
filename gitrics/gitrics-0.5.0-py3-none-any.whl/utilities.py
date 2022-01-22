import datetime
import math

import scipy.stats as st

def ci_lower_bound(ratings: int, total: int, confidence: float = 0.95) -> float:
    """
    Calculate the lower bound on the proportion of the rating, i.e. balance the proportion of ratings with the uncertainty of a small number of observations.

    Reference: https://www.evanmiller.org/how-not-to-sort-by-average-rating.html

    Args:
        confidence (float): statistical confidence level that the lower bound is correct
        ratings (integer): count of ratings to score by
        total (integer): total count of all ratings

    Returns:
        A float representing the score for of an item relative to all items where all items have the potential to be rated via an ordinal scale toward an action.
    """

    result = 0

    # check for totals
    if total > 0:

        # get standard deviation multipler for percentage value
        z = st.norm.ppf(1 - (1 - confidence) / 2)
        phat = 1.0 * ratings / total

        # update result
        result = (phat + z * z / (2 * total) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)) / (1 + z * z / total)

    return result

def configure_date_range(date_start, date_end):
    """
    Determine start/end dates based on user input.

    Args:
        date_end (string): iso 8601 date value
        date_start (string): iso 8601 date value

    Returns:
        A tuple of start, end dateimte values.
    """

    # convert time
    dt_end = datetime.datetime.strptime(date_end, "%Y-%m-%d")
    dt_start = datetime.datetime.strptime(date_start, "%Y-%m-%d") if date_start and date_end and date_start != date_end else dt_end - datetime.timedelta(3)

    return (dt_start, dt_end)

def parse_multi_parameters(value):
    """
    Parse a string of comma-delimetered values into a native python list.

    Args:
        value (string): comma-delimetered value

    Returns:
        A list of strings where each is a discrete value in the set.
    """

    return value.split(",") if value else list()
