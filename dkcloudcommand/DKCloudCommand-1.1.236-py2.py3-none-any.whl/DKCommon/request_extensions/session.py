import logging
import time

from typing import Optional

from requests import Session

from DKCommon.request_extensions.utils import parse_rate_limit
from DKCommon.request_extensions.settings import RETRIES, RATE_LIMIT_HEADERS

LOG = logging.getLogger(__name__)


class ExtendedSession(Session):

    @staticmethod
    def _has_retry_text(value: Optional[str]) -> bool:
        try:
            return "please try again in a bit" in value
        except (TypeError, ValueError):
            return False

    def request(self, method: str, url: str, **kwargs):
        """
        Dispatch requests with special handling for rate-limited auth endpoints.

        For 401 errors, sometimes rate-limiting is at play. If rate-limit headers are present, honor their
        wait times. For other endpoints response text is sometimes used to indicate rate limiting, in known
        cases, fallback to a retry strategy for the request.
        """
        if method.upper() != "POST":
            return super().request(method, url, **kwargs)

        response = super().request(method, url, **kwargs)
        if response.status_code != 401:
            return response

        # If there were any rate-limit headers, parse them and wait the appropriate time then try again.
        rate_gen = (response.get(x) for x in RATE_LIMIT_HEADERS)
        rate_limit: Optional[int] = next((x for x in rate_gen if x), None)

        if rate_limit:
            wait = parse_rate_limit(rate_limit[0])
            LOG.debug("Sleeping for %s seconds to honor Rate-Limit headers", wait)
            time.sleep(wait)
            return super().request(method, url, **kwargs)

        if self._has_retry_text(response.text):
            for i in range(RETRIES):
                wait = 0.5 * (2 ** (i - 1))
                time.sleep(wait)
                LOG.debug("Sleeping for %s seconds to retry authentication.", wait)
                response = super().request(method, url, **kwargs)
                if response.status_code != 401:
                    return response
                else:
                    if self._has_retry_text(response.text):
                        continue
                    else:
                        return response
        else:
            return super().request(method, url, **kwargs)
