"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""

import time


class AutoRateLimiter(object):
    """
    A safety feature to ensure users don't accidentally rate-limit themselves.

    This ensures that if less than (1 / max requests per second) time has passed
    since the last request, ensure at least this much time as passed before
    completing the request.

    This is specifically to protect users that are using this functionality
    asynchronously, as everything is serial by default.
    """

    ONE_BILLION = 1e9

    def __init__(self, max_requests_per_second: int = 45):
        """
        Note: DataRobot API allows max 50/s

        Parameters
        ----------
        max_requests_per_second: int
            Number of requests per second to allow

        """
        self.enforce_rate_limitation = max_requests_per_second > 0
        self.max_requests_per_second = max_requests_per_second
        self.safety_delay_ns = (
            1.0 / max_requests_per_second if self.enforce_rate_limitation else 0
        ) * self.ONE_BILLION

        self.last_request = time.time_ns()

    def __enter__(self):
        if not self.enforce_rate_limitation:
            return
        now = time.time_ns()
        since_last = now - self.last_request
        if since_last < self.safety_delay_ns:
            delay_ns = self.safety_delay_ns - since_last
            time.sleep(delay_ns * 1e-9)
            now += delay_ns
        self.last_request = now

    def __exit__(self, type, value, traceback):
        pass
