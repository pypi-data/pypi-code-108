import logging

from DKCommon.dt_utils import utcnow
from DKCommon.request_extensions.settings import REQUESTS_TIMEOUT

LOG = logging.getLogger(__name__)


def parse_rate_limit(value: float) -> float:
    """Parse a rate limit value if it is a timestamp. Never longer than default timeout."""
    # Since this value can either be a duration until reset or a timestamp representing the reset,
    # if the value is large (more than a day's worth of seconds) then it's probably a timestamp.
    if value > 86400:
        limit = int(value - utcnow().timestamp())
    else:
        limit = value
    if limit > REQUESTS_TIMEOUT:
        LOG.warning("Rate limit value %s is longer than the requests timeout setting.", limit)
        return float(REQUESTS_TIMEOUT)
    else:
        return limit
