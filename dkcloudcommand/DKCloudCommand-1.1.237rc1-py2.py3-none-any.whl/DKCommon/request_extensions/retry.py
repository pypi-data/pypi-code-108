import logging
import time

from typing import Optional

from requests.packages.urllib3.util.retry import Retry
from urllib3.response import HTTPResponse

from DKCommon.request_extensions.settings import RATE_LIMIT_HEADERS
from DKCommon.request_extensions.utils import parse_rate_limit

LOG = logging.getLogger(__name__)


class RateLimitRetry(Retry):
    """A retry strategy that honors rate-limit headers if present."""

    def get_rate_limit_header(self, response: HTTPResponse) -> Optional[str]:
        """Parse a response and get the rate limit header if it exists."""
        for header in RATE_LIMIT_HEADERS:
            if header in response.headers:
                return header
        else:
            return None

    def get_rate_limit_wait(self, response: HTTPResponse) -> Optional[float]:
        """
        Get the value of RateLimit header in seconds.

        RateLimit-Reset can either be a timestamp representing a point in the future when the rate limit
        resets--OR--it can be the number of seconds until the reset. There are several semi-standard rate-limiting
        headers to check for.
        """
        header = self.get_rate_limit_header(response)
        if header:
            limit_value = response.getheader(header)
            if limit_value:
                try:
                    limit_float = float(limit_value)
                except ValueError:
                    LOG.error("Header `%s` value `%s` is not a valid number", header, limit_value)
                    return None
                return parse_rate_limit(limit_float)
        else:
            return None

    def sleep_for_ratelimit(self, response: HTTPResponse) -> bool:
        wait = self.get_rate_limit_wait(response)
        if wait:
            LOG.debug("Sleeping for %s seconds as requested by Rate-Limit header")
            time.sleep(wait)
            return True
        return False

    def sleep(self, response: Optional[HTTPResponse] = None) -> None:
        """
        Sleep between retry attempts.

        If there are rate-limit headers present then these are honored.
        """
        if response:
            if self.get_rate_limit_header(response):
                slept = self.sleep_for_ratelimit(response)
                if slept:
                    return
        super().sleep(response=response)
