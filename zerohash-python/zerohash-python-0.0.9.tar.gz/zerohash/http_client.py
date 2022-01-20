import logging
import textwrap
import threading
import time

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from zerohash import error

logging.basicConfig(level=logging.DEBUG)

try:
    import requests
except ImportError:
    requests = None


def new_default_http_client(*args, **kwargs):
    if requests:
        return RequestsClient(*args, **kwargs)
    else:
        raise Exception(
            "Requests must be installed as it is currently the only option for an HTTP client."
        )


class HttpClient:
    MAX_DELAY = 2  # in seconds
    INITIAL_DELAY = 0.5  # in seconds

    def __init__(self):
        self._thread_local = threading.local()

    def request_with_retries(self, method, url, headers, post_data=None, proxies=None):
        num_retries = 0
        while True:
            try:
                response = self.request(method, url, headers, post_data)
                connection_error = None
            except error.APIConnectionError as e:
                response = None
                connection_error = e

            if self._should_retry(response, connection_error, num_retries):
                num_retries += 1
                sleep_time = self._sleep_time_seconds(num_retries, response)
                time.sleep(sleep_time)
            else:
                if response is not None:
                    return response
                else:
                    raise connection_error

    def request(self, method, url, headers, post_data=None):
        raise NotImplementedError(
            f"HttpClient sublcass must implement `request` method."
        )

    @property
    def _max_network_retries(self):
        from zerohash import max_network_retries

        return max_network_retries

    def _should_retry(self, response, api_connection_error, num_retries):
        if num_retries > self._max_network_retries:
            return False

        if response is None:
            # TODO: we eventually want the subclasses to handle this. for now, default to not retry on connection
            # issues/timeouts.
            return False

        content, status_code, rheaders = response

        if status_code >= 500:
            print("should retry...")
            return True
        return False

    def _sleep_time_seconds(self, num_retries, response=None):
        sleep_seconds = min(
            self.MAX_DELAY, self.INITIAL_DELAY * (2 ** (num_retries - 1))
        )  # Double delay with each retry until we reach the max delay

        return sleep_seconds


class RequestsClient(HttpClient):
    name = "requests"

    def __init__(self, timeout=30):
        self._timeout = timeout
        self._session = None
        super().__init__()

    def request(self, method, url, headers, post_data=None):

        if getattr(self._thread_local, "session", None) is None:
            self._thread_local.session = self._session or requests.Session()
            self._thread_local.session.keep_alive = (
                False  # TODO: remove this for performance improvement
            )

            retry = Retry(
                total=self._max_network_retries, connect=5, backoff_factor=0.1
            )

            adapter = HTTPAdapter(max_retries=retry)

            self._thread_local.session.mount("http://", adapter)
            self._thread_local.session.mount("https://", adapter)

        try:
            res = self._thread_local.session.request(
                method,
                url,
                headers=headers,
                data=post_data,
                timeout=self._timeout,
                verify=True,  # TODO: if all else fails, set this to False
            )
        except Exception as e:
            self._handle_request_error(e)

        return res.content, res.status_code, res.headers

    def _handle_request_error(self, e):
        """"""
        if isinstance(e, requests.exceptions.ConnectionError):
            msg = (
                "Request [Connection Error] detected communicating with [Zero Hash API]"
            )
            err = f"{type(e).__name__}: {str(e)}"
            should_retry = True
        if isinstance(e, requests.Timeout):
            msg = "Request [Timeout] detected communicating with [Zero Hash API]"
            err = f"{type(e).__name__}: {str(e)}"
            should_retry = True
        if isinstance(e, requests.RequestException):
            msg = "Request [Exception] detected communicating with [Zero Hash API]"
            err = f"{type(e).__name__}: {str(e)}"
            should_retry = True
        else:
            msg = (
                "Unexpected connection error communicating with Zero Hash. "
                "There is probably a configuration issue locally."
            )
            err = "A %s was raised" % (type(e).__name__,)
            if str(e):
                err += " with error message %s" % (str(e),)
            else:
                err += " with no error message."
            should_retry = False
        msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
        raise error.APIConnectionError(msg, should_retry=should_retry)
