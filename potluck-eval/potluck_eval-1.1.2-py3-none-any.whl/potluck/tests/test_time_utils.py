"""
Tests of the time_utils module.

test_time_utils.py
"""

import datetime

from .. import time_utils


def test_time_strings():
    """
    Very basic test of time strings conversion.
    """
    now = time_utils.timestring()
    conv = time_utils.time_from_timestring(now)
    conv2 = time_utils.timestring(conv)
    assert now == conv2

    when = datetime.datetime(year=1998, month=8, day=3)
    ts = time_utils.timestring(when)
    conv = time_utils.time_from_timestring(ts)
    conv2 = time_utils.timestring(conv)
    assert ts == conv2
