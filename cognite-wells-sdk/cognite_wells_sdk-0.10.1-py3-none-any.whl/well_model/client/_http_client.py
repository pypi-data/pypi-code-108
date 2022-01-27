import random
import socket
import time
from dataclasses import dataclass
from typing import Callable, Optional, Set, Tuple, Type, Union

import requests
import urllib3

from cognite.well_model.client.utils import _client_config
from cognite.well_model.client.utils.exceptions import (
    CogniteConnectionError,
    CogniteConnectionRefused,
    CogniteReadTimeout,
)


def _init_requests_session() -> requests.Session:
    """
    A Session object can persist cookies and some parameters across requests and reuses the underlying
    HTTP connection for the requests. It uses a urllib3 PoolManager, which will significantly
    increase performance of HTTP requests to the same host.

    Returns:
        requests.Session: a configured Session object
    """
    session = requests.Session()
    cognite_config = _client_config._DefaultConfig()
    adapter = requests.adapters.HTTPAdapter(
        pool_maxsize=cognite_config.max_connection_pool_size, max_retries=urllib3.Retry(False)
    )

    # increase the number of allowed retries by mounting a custom adapter to a given schema
    session.mount("https://", adapter)
    if cognite_config.disable_ssl:
        urllib3.disable_warnings()
        session.verify = False
    return session


GLOBAL_REQUEST_SESSION = _init_requests_session()


@dataclass
class HTTPClientConfig:
    """Contains the configurations for the http client """

    status_codes_to_retry: Set[int]
    backoff_factor: float
    max_backoff_seconds: int
    max_retries_total: int
    max_retries_status: int
    max_retries_read: int
    max_retries_connect: int


class _RetryTracker:
    """Keep track of http client retry attempts

    for more info on the topic:
    https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
    """

    def __init__(self, config: HTTPClientConfig):
        self.config = config
        self.status = 0
        self.read = 0
        self.connect = 0

    @property
    def total(self) -> int:
        return self.status + self.read + self.connect

    def _max_backoff_and_jitter(self, t: int) -> int:
        """A host which has experienced a collision on a network waits for a amount of
        time before attempting to retransmit. A random backoff minimises the
        probability that the same nodes will collide again

        Args:
            t (int): input backoff seconds
        Returns:
            minimum of max input backoff seconds and max backoff seconds
        """
        return int(min(t, self.config.max_backoff_seconds) * random.uniform(0, 1.0))

    def get_backoff_time(self) -> int:
        """
        An exponential backoff algorithm retries requests exponentially,
        increasing the waiting time between retries up to a maximum backoff
        time. To avoid retrying for too long we cap the backoff to a maximum
        value

        Returns:
            the minimum of a calculated exponential backoff time and a maximum
                backoff time
        """
        exp_backoff_time = self.config.backoff_factor * (2 ** self.total)
        backoff_time_adjusted = self._max_backoff_and_jitter(exp_backoff_time)
        return backoff_time_adjusted

    def should_retry(self, status_code: Optional[int]) -> bool:
        """check whether the request should be retried or not

        Args:
            status_code: the status code that we get from the API
        Returns:
            True if status code qualifies for retry, else False
        """
        if self.total >= self.config.max_retries_total:
            return False
        if self.status > 0 and self.status >= self.config.max_retries_status:
            return False
        if self.read > 0 and self.read >= self.config.max_retries_read:
            return False
        if self.connect > 0 and self.connect >= self.config.max_retries_connect:
            return False
        if status_code and status_code not in self.config.status_codes_to_retry:
            return False
        return True


class HTTPClient:
    """Initializes a client with http config, session config, http retry policy
    and appropriate networking exceptions
    """

    def __init__(
        self,
        config: HTTPClientConfig,
        session: requests.Session = GLOBAL_REQUEST_SESSION,
        retry_tracker_factory: Callable[[HTTPClientConfig], _RetryTracker] = _RetryTracker,
    ):
        self.session = session
        self.config = config
        self.retry_tracker_factory = retry_tracker_factory

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """http request with retry policy and exception handling

        Args:
            method: http method: GET, PUT, POST, DELETE etc.
            url: target url for the http request
            kwargs: request arguments as dictionary
        Returns:
            server's response to an HTTP request
        """
        retry_tracker = self.retry_tracker_factory(self.config)
        last_status = None
        while True:
            try:
                res = self._do_request(method=method, url=url, **kwargs)
                last_status = res.status_code
                retry_tracker.status += 1
                if not retry_tracker.should_retry(status_code=last_status):
                    return res
            except CogniteReadTimeout as e:
                retry_tracker.read += 1
                if not retry_tracker.should_retry(status_code=last_status):
                    raise e
            except CogniteConnectionError as e:
                retry_tracker.connect += 1
                if isinstance(e, CogniteConnectionRefused) or not retry_tracker.should_retry(status_code=last_status):
                    raise e
            time.sleep(retry_tracker.get_backoff_time())

    def _do_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Sometimes the appropriate networking exception is not in the context, so we need to
        check for the appropriate built-in exceptions, urllib3 exceptions, and requets exceptions

        requests/urllib3 adds 2 or 3 layers of exceptions on top of built-in networking exceptions.

        Args:
            method: http method: GET, PUT, POST, DELETE etc.
            url: target url for the http request
            kwargs: request arguments as dictionary
        Returns:
            server's response to an HTTP request
        """
        try:
            res = self.session.request(method=method, url=url, **kwargs)
            return res
        except Exception as e:
            if self._any_exception_in_context_isinstance(
                e, (socket.timeout, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout)
            ):
                raise CogniteReadTimeout from e
            if self._any_exception_in_context_isinstance(
                e,
                (
                    ConnectionError,
                    urllib3.exceptions.ConnectionError,
                    urllib3.exceptions.ConnectTimeoutError,
                    requests.exceptions.ConnectionError,
                ),
            ):
                if self._any_exception_in_context_isinstance(
                    e, (ConnectionRefusedError, urllib3.exceptions.NewConnectionError)
                ):
                    raise CogniteConnectionRefused from e
                raise CogniteConnectionError from e
            raise e

    @classmethod
    def _any_exception_in_context_isinstance(
        cls, exc: BaseException, T: Union[Tuple[Type[BaseException], ...], Type[BaseException]]
    ) -> bool:
        """requests does not use the "raise ... from ..." syntax, so we need to access the underlying exceptions using
        the __context__ attribute.

        Args:
            exc: exception we want to check type for (base class for all built-in exceptions)
            T: collection of exceptions we want to compare 'exc' with.
        Returns:
            True if thrown exception belong to collection T, else False
        """
        if isinstance(exc, T):
            return True
        if exc.__context__ is None:
            return False
        return cls._any_exception_in_context_isinstance(exc.__context__, T)
