"""
Constants having to do with date or time

.. data:: MINUTE_IN_SECONDS

.. data:: HOUR_IN_SECONDS

.. data:: DAY_IN_SECONDS

.. data:: WEEK_IN_SECONDS

.. data:: MONTH_IN_SECONDS

.. data:: YEAR_IN_SECONDS

"""

MINUTE_IN_SECONDS: int = 60

HOUR_IN_SECONDS: int = MINUTE_IN_SECONDS * 60

DAY_IN_SECONDS: int = HOUR_IN_SECONDS * 24

WEEK_IN_SECONDS: int = DAY_IN_SECONDS * 7

MONTH_IN_SECONDS: int = WEEK_IN_SECONDS * 4

YEAR_IN_SECONDS: int = WEEK_IN_SECONDS * 52
