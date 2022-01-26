"""
Helper for time related functions
"""

# Standard Library
from datetime import datetime


def get_time_delta(then, now=datetime.now(), interval="default"):
    """
    Returns a duration as specified by variable interval
    functions, except total_duration, returns [quotient, remainder]
    :param then:
    :type then:
    :param now:
    :type now:
    :param interval:
    :type interval:
    :return:
    :rtype:
    """

    duration = now.replace(tzinfo=None) - then.replace(tzinfo=None)
    duration_in_seconds = duration.total_seconds()

    def years():
        """
        Return years
        :return:
        :rtype:
        """

        return divmod(duration_in_seconds, 31536000)  # Seconds in a year = 31536000.

    def days(from_seconds=None):
        """
        Return days
        :param from_seconds:
        :type from_seconds:
        :return:
        :rtype:
        """

        return divmod(
            from_seconds if from_seconds is not None else duration_in_seconds, 86400
        )  # Seconds in a day = 86400

    def hours(from_seconds=None):
        """
        Return hours
        :param from_seconds:
        :type from_seconds:
        :return:
        :rtype:
        """

        return divmod(
            from_seconds if from_seconds is not None else duration_in_seconds, 3600
        )  # Seconds in an hour = 3600

    def minutes(from_seconds=None):
        """
        Return minutes
        :param from_seconds:
        :type from_seconds:
        :return:
        :rtype:
        """

        return divmod(
            from_seconds if from_seconds is not None else duration_in_seconds, 60
        )  # Seconds in a minute = 60

    def seconds(from_seconds=None):
        """
        Return seconds
        :param from_seconds:
        :type from_seconds:
        :return:
        :rtype:
        """

        if from_seconds is not None:
            return divmod(from_seconds, 1)
        return duration_in_seconds

    def total_duration():
        """
        Return total time difference
        :return:
        :rtype:
        """

        y = years()
        d = days(y[1])  # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])

        return "{} years, {} days, {} hours, {} minutes and {} seconds".format(
            int(y[0]), int(d[0]), int(h[0]), int(m[0]), int(s[0])
        )

    return {
        "years": int(years()[0]),
        "days": int(days()[0]),
        "hours": int(hours()[0]),
        "minutes": int(minutes()[0]),
        "seconds": int(seconds()),
        "default": total_duration(),
    }[interval]
