#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
"""This module is not considered part of the public interface. As of 2.3, anything here
may change or be removed without warning."""

import itertools
import time


def wait(timeout, delay=0.1, maxdelay=1.0):
    """Generate a slow loop, with exponential back-off.

    Parameters
    ----------
    timeout : float or int
        Total seconds to wait.
    delay : float or int
        Initial seconds to sleep.
    maxdelay : float or int
        Maximum seconds to sleep.

    Yields
    ----------
    int
        Retry count.

    Examples
    ----------
    >>> for index in retry.wait(10):
        # break if condition is met
    """
    if timeout is None:
        timeout = float("Inf")
    start_time = time.time()
    delay /= 2.0
    for index in itertools.count():
        seconds_waited = time.time() - start_time
        remaining = timeout - seconds_waited
        yield index, seconds_waited
        if remaining < 0:
            break
        delay = min(delay * 2, maxdelay, remaining)
        time.sleep(delay)
