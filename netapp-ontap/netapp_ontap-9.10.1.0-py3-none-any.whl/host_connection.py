# pylint: disable=line-too-long
"""
Copyright &copy; 2021 NetApp Inc.
All rights reserved.

This module defines a host connection object which is used to communicate with
the API host.
"""
from contextlib import contextmanager
import copy
from http.client import responses
import logging
from typing import Generator, Optional, Tuple
import urllib.parse


import requests
from requests.adapters import HTTPAdapter
from urllib3.util import retry  # type: ignore


# prevent "No handlers" message if consumer application doesn't configure logging at all
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

_HOST_CONTEXT = None  # type: Optional[HostConnection]
_DEFAULT_CONNECTION_TIMEOUT = 6 # seconds
_DEFAULT_READ_TIMEOUT = 45 # seconds

class WrappedSession(requests.Session):
    """A wrapper for requests.Session to allow the 'verify' the property
    to override the REQUESTS_CA_BUNDLE environment variable.
    """
    #pylint: disable=too-many-arguments
    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        if self.verify is False:
            verify = False

        return super(WrappedSession, self).merge_environment_settings(url, proxies, stream, verify, cert)


class HostConnection:  # pylint: disable=too-many-instance-attributes
    """The HostConnection allows the client application to store their credentials
    and reuse them for each operation. There are three ways to use a connection
    object:

    * The first is to use the connection object as a context manager. Any operations
      on a resource that are called within the scope of the block will use that
      connection.
    * The second is to call set_connection() on a resource object. This
      will then be the connection used for all actions for that object only.
    * The third way is to call netapp_ontap.config.CONNECTION = connection. This
      connection instance will now be used for all actions on all resource
      objects (that do not otherwise set their own connection). This reduces
      the need to pass the connection around the application.

    Connections will be searched for in this order when executing an action.
    """

    # pylint: disable=bad-continuation,too-many-arguments
    def __init__(
        self,
        host,
        username: str = None,
        password: str = None,
        cert: str = None,
        key: str = None,
        verify: bool = True,
        poll_timeout: int = 30,
        poll_interval: int = 5,
        headers: dict = None,
    ):
        """Store information needed to contact the API host

        Either username and password must be provided or certificate and key must
        be provided.

        If verify is set to False, urllib3's InsecureRequestWarnings will also be
        silenced in the logs.

        Args:
            host: The API host that the library should talk to
            username: The user identifier known to the host
            password: The secret for the user
            cert: The file path to the users public certificate. The common
                name in the certificate must match the account name.
            key: A private key in PEM format
            verify: If an SSL connection is made to the host, this parameter
                controls how the validity of the trust chain of the certificate
                is handled. See the documentation for the requests library for more information:
                https://2.python-requests.org/en/master/user/advanced/#ssl-cert-verification
            poll_timeout: Time in seconds to poll on a job. This setting applies to all polling
                that uses this connection unless overridden as a parameter to poll(). Defaults
                to 30 seconds.
            poll_interval: Time in seconds to wait between polls on a job. This setting applies
                to all polling that uses this connection unless overridden as a parameter to
                poll(). Defaults to 5 seconds.
            headers: Any custom headers to be passed to each request using this connection object.
        """

        argument_error = False
        if not username:
            argument_error = not cert or not key
        elif not cert:
            argument_error = not username or not password
        else:
            argument_error = username is not None and cert is not None

        if argument_error:
            from netapp_ontap.error import NetAppRestError  # pylint: disable=cyclic-import

            raise NetAppRestError(
                "Either username and password must be provided or a cert and a"
                " key must be provided. You may not provide both."
            )

        self.scheme = "https"
        self.host = host
        self.port = 443
        self.username = username
        self.password = password
        self.cert = cert
        self.key = key
        self.verify = verify
        self.poll_timeout = poll_timeout
        self.poll_interval = poll_interval
        self.headers = headers
        self.protocol_timeouts = None
        self._old_context = None  # type: Optional[HostConnection]
        self._request_session = None  # type: Optional[requests.Session]

        if not self.verify:
            import urllib3  # type: ignore
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @staticmethod
    def get_host_context() -> "Optional[HostConnection]":
        """Get the current host context, if any.

        Returns:
            A HostConnection object or None if not in a host connection context.
        """

        return _HOST_CONTEXT

    @property
    def basic_auth(self) -> Optional[Tuple[str, str]]:
        """Pulls the credentials out of the connection object.

        Returns:
            A tuple of username and password sufficient for passing to the requests library. Returns None if this connection is not configured for basic auth with a username and password.
        """

        if self.username and self.password:
            return (self.username, self.password)
        return None

    @property
    def cert_auth(self) -> Optional[Tuple[str, str]]:
        """Pulls the certificate details out of the connection object.

        Returns:
            A tuple of cert and key sufficient for passing to the requests library. Returns None if this connection is not configured for cert auth with a cert and key.
        """

        if self.cert and self.key:
            return (self.cert, self.key)
        return None

    @property
    def origin(self) -> str:
        """The beginning of any REST endpoint.

        Returns:
            The origin part of the URL. For example, `http://1.2.3.4:8080`.
        """

        return f"{self.scheme}://{self.host}:{self.port}"

    @property
    def request_headers(self) -> Optional[dict]:
        """Retrieves the headers set out of the connection object

        Returns:
            A dictionary consisting of header names and values for passing to the requests library. Returns None if no headers are configured.
        """

        if self.headers:
            return self.headers
        return None

    @request_headers.setter
    def request_headers(self, headers):
        """Set the request headers for the connection object"""
        if isinstance(headers, dict):
            self.headers = headers
        else:
            raise TypeError("Request headers must be specified as a 'dict' type")

    @contextmanager
    def with_headers(self, headers: dict) -> Generator["HostConnection", None, None]:
        """ Manually set the headers field of the connection object """
        old_headers = copy.deepcopy(self.request_headers)
        self.headers = headers
        yield self
        self.headers = old_headers
        self._request_session = None

    def __enter__(self):
        global _HOST_CONTEXT  # pylint: disable=global-statement
        self._old_context = _HOST_CONTEXT
        _HOST_CONTEXT = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        global _HOST_CONTEXT  # pylint: disable=global-statement
        _HOST_CONTEXT = self._old_context

    @property
    def session(self) -> requests.Session:
        """A `requests.Session` object which is used for all API calls.

        This session is reused for each API call made with this connection. Multiple
        requests may therefore be sent through the same TCP connection assuming
        the host supports keep-alive.

        Returns:
            A `requests.Session` object which is used for all API calls.
        """

        current_session = getattr(self, "_request_session", None)
        if not current_session:
            current_session = WrappedSession()

        if self.origin not in current_session.adapters:
            from netapp_ontap import config
            if config.RETRY_API_ON_ERROR:
                retry_strategy = retry.Retry(
                    total=config.RETRY_API_ATTEMPTS,
                    status_forcelist=config.RETRY_API_ERROR_CODES,
                    method_whitelist=config.RETRY_API_HTTP_METHODS,
                    backoff_factor=config.RETRY_API_BACKOFF_FACTOR,
                )
            else:
                retry_strategy = 5
            current_session.mount(
                self.origin,
                LoggingAdapter(self, max_retries=retry_strategy, timeout=self.protocol_timeouts)
            )
        if self.basic_auth:
            current_session.auth = self.basic_auth
        else:
            current_session.cert = self.cert_auth
        if self.request_headers:
            current_session.headers.update(self.request_headers)
        current_session.verify = self.verify

        import netapp_ontap  # pylint: disable=cyclic-import
        current_session.headers.update(
            {"X-Dot-Client-App": f"netapp-ontap-python-{netapp_ontap.__version__}"}
        )

        self._request_session = current_session
        return current_session


class LoggingAdapter(HTTPAdapter):
    """A custom HTTPAdapter which logs API calls if logging is enabled"""

    def __init__(self, host_connection, *args, **kwargs):
        self.timeout = kwargs.pop("timeout", None)
        if self.timeout is None:
            self.timeout = (_DEFAULT_CONNECTION_TIMEOUT, _DEFAULT_READ_TIMEOUT)
        self.host_connection = host_connection
        super().__init__(*args, **kwargs)

    # pylint: disable=bad-continuation
    def send(  # pylint: disable=too-many-arguments
        self,
        request,
        stream=False,
        timeout=None,
        verify=True,
        cert=None,
        proxies=None,
    ) -> requests.Response:
        timeout = timeout if timeout else self.timeout
        request.url = _percent_encode_spaces(request.url)
        from netapp_ontap import utils  # pylint: disable=cyclic-import
        if utils.LOG_ALL_API_CALLS:
            pretty_print_request(request)
        response = super().send(
            request, stream=stream, timeout=timeout, verify=verify,
            cert=cert, proxies=proxies,
        )
        if cert and response.status_code == 401:
            del self.host_connection._request_session
        if utils.LOG_ALL_API_CALLS:
            pretty_print_response(response)
        elif response.status_code >= 400 and utils.DEBUG:
            pretty_print_request(request)
            pretty_print_response(response)
        return response


def pretty_print_request(request: requests.PreparedRequest) -> None:
    """Prints the complete request in a pretty way."""

    result = "\n-----------REQUEST-----------"
    result += f"\n{request.method} {request.url}\n"
    result += "\n".join(f"{k}: {v}" for k, v in request.headers.items())
    result += "\n" + str(request.body)
    result += "\n-----------------------------"

    LOGGER.debug(result)


def pretty_print_response(response: requests.Response) -> None:
    """Prints the complete response in a pretty way."""

    result = "\n-----------RESPONSE-----------"
    result += f"\n{response.status_code} {responses[response.status_code]}\n"
    result += "\n".join(f"{k}: {v}" for k, v in response.headers.items())
    result += "\n" + response.text
    result += "\n------------------------------"

    LOGGER.debug(result)


def _percent_encode_spaces(url: str) -> str:
    """ONTAP likes spaces in query parameters to be space encoded, but the requests
    library encodes them as + by default. Here, we will fix that up so that ONTAP
    will return correct responses.
    """

    parse_result = urllib.parse.urlparse(url)
    query_data = dict(urllib.parse.parse_qsl(parse_result.query))
    query_data_str = urllib.parse.urlencode(query_data, quote_via=urllib.parse.quote)
    return urllib.parse.urlunparse(parse_result._replace(query=query_data_str))
