import logging

from requests.adapters import HTTPAdapter

from DKCommon.request_extensions.settings import REQUESTS_TIMEOUT

LOG = logging.getLogger(__name__)


class TimeoutHTTPAdapter(HTTPAdapter):
    """
    An HTTPAdapter for request sessions that automatically includes a timeout.

    Requests recommends a timeout be set in all production use of request sessions. This adapter adds a timeout by
    default but allows for overriding if desired.
    """

    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.pop("timeout", REQUESTS_TIMEOUT)
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout", None)

        # Apply the default timeout if one was not manually passed
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)
