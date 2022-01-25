import json
import logging
import warnings

from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    ClientError,
    ConflictError,
    ConnectionError,
    InputDataError,
    NotFoundError,
    RetryError,
    TransportError,
    UnknownError,
)
from .topic import TopicApiMixin
from .user import UserApiMixin

log = logging.getLogger(__name__)
# SQ-7983: lower the log level of retry module to give some feedback
# see bug report for details
logging.getLogger("urllib3.util.retry").setLevel(logging.DEBUG)

warnings.filterwarnings("ignore", category=ImportWarning)
# Disable `ResourceWarning` for python 3 due to unclosed request sessions
warnings.filterwarnings("ignore", category=ResourceWarning)


#: Default headers for all requests.
HEADERS = {"Accept": "application/json"}

#: Default endpoint URLs for the Squirro platform.
ENDPOINT = {
    "user": "https://user-api.squirro.com",
    "topic": "https://topic-api.squirro.com",
}

#: Version of the Squirro API to be used.
API_VERSION = "v0"

#: Format for datetime values.
ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

#: Default timeout option.
TIMEOUT_SECS = 55

#: Default retry options.
RETRY = {
    "total": 10,
    "connect": 5,
    "read": 3,
    "redirect": 5,
    "allowed_methods": frozenset(
        ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
    ),
    "status_forcelist": frozenset([502, 503, 504]),
    "backoff_factor": 1,
}


class SquirroClient(UserApiMixin, TopicApiMixin):
    """Client to access the Squirro API.

    :param client_id: The client id for accessing the API.
    :param client_secret: The client secret for accessing the API.
    :param cluster: The cluster endpoint for accessing the API.
    :param user_api_url: Endpoint URL for the user API service.
    :param topic_api_url: Endpoint URL for the topic API service.
    :param tenant: Tenant domain.
    :param version: API version to use, defaults to 'v0'.
    :param requests: `requests` instance for HTTP calls.
    :param retry_total: Total number of retries to allow. Takes precedence
        over other counts.
    :param retry_connect: How many connection-related errors to retry on.
    :param retry_read: How many times to retry on read errors.
    :param retry_redirect: How many redirects to perform.
    :param retry_method_whitelist: Set of uppercase HTTP method verbs that we
        should retry on.
    :param retry_status_forcelist: A set of integer HTTP status codes that we
        should force a retry on.
    :param retry_backoff_factor: A backoff factor to apply between attempts.
    :param timeout_secs: How many seconds to wait for data before giving up
        (default 55).

    Example::

        >>> from squirro_client import SquirroClient
        >>> client = SquirroClient('client_id', 'client_secret')
        >>> client = SquirroClient(None, None,
        ...                        cluster='http://squirro.example.com')
        >>> client = SquirroClient(None, None,
        ...                        cluster='http://squirro.example.com',
        ...                        retry_total=10)
    """

    def __init__(self, client_id, client_secret, **kwargs):

        # assign authentication class state
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant = kwargs.get("tenant", None)

        self._access_token = None
        self._refresh_token = None

        # endpoint URLs
        self.version = kwargs.get("version", API_VERSION)
        cluster = kwargs.get("cluster")

        if cluster:
            cluster = cluster.rstrip("/")
            base = "%(cluster)s/api/%(api)s"
            self.user_api_url = base % {"cluster": cluster, "api": "user"}
            self.topic_api_url = base % {"cluster": cluster, "api": "topic"}

        else:
            user_api_url = kwargs.get("user_api_url") or ENDPOINT["user"]
            topic_api_url = kwargs.get("topic_api_url") or ENDPOINT["topic"]

            self.user_api_url = user_api_url.rstrip("/")
            self.topic_api_url = topic_api_url.rstrip("/")

        # retry default options, use values provided by the caller to update
        # the default retry options
        self.retry = RETRY
        for k, v in kwargs.items():
            if k.startswith("retry_"):

                # `method_whitelist` has been deprecated
                if k == "retry_method_whitelist":
                    k = "retry_allowed_methods"

                self.retry[k.replace("retry_", "")] = v

        # default timeout
        self.timeout_secs = TIMEOUT_SECS
        kwargs_timeout_secs = kwargs.get("timeout_secs")
        if kwargs_timeout_secs:
            self.timeout_secs = kwargs_timeout_secs

        # either use the user supplied requests instance or the actual
        # requests module
        self._requests = kwargs.get("requests", None)
        if self._requests is None:
            import requests

            self._requests = requests
        self.session = self._new_session()

    @property
    def access_token(self):
        """Property to get or set the access token of the client."""
        return self._access_token

    @access_token.setter
    def access_token(self, new_access_token):
        """Store the received access token and create a new `requests`
        session.
        """
        self._access_token = new_access_token
        self.session = self._new_session(self._access_token)

    @property
    def refresh_token(self):
        """Property to get or set the refresh token of the client."""
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, new_refresh_token):
        """Store the received refresh token."""
        self._refresh_token = new_refresh_token

    def authenticate(
        self,
        tenant=None,
        access_token=None,
        refresh_token=None,
        auth_service=None,
        auth_user=None,
        username=None,
        password=None,
        user_information=None,
    ):
        """Authenticate with the Squirro platform by either using access and
        refresh tokens, username and password, or external service name and
        user identifier.

        :param tenant: The tenant for accessing the Squirro platform.
        :param access_token: User access token.
        :param refresh_token: User refresh token.
        :param auth_service: External authentication service name.
        :param auth_user: External authentication user identifier.
        :param username: User name.
        :param password: User password.
        :param user_information: Additional information about the user for
            internal use.

        :raises: :class:`squirro_client.exceptions.AuthenticationError` if
            authentication fails.

        Example::

            >>> client.authenticate(username='test@test.com',
            ...                     password='test')
            >>> client.authenticate(access_token='token01',
            ...                     refresh_token='token02')
            >>> client.authenticate(auth_service='salesforce',
            ...                     auth_user='sfdc01')

        """

        # set the tenant if it is provided
        if tenant is not None:
            self.tenant = tenant

        # assemble base request data
        base = {}
        if self.client_id is not None:
            base["client_id"] = self.client_id
        if self.client_secret is not None:
            base["client_secret"] = self.client_secret
        if self.tenant is not None:
            base["tenant"] = self.tenant
        if user_information is not None:
            base["user_information"] = json.dumps(user_information)

        # walk through all possible authentication scenarios
        # - access token
        # - refresh token
        # - external id
        # - username / password
        if access_token is not None:
            # login by using the access token
            data = {"grant_type": "access_token", "access_token": access_token}
            self._perform_authentication(dict(base, **data))

        elif refresh_token is not None:
            # login by using the refresh token
            data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
            self._perform_authentication(dict(base, **data))

        elif auth_service is not None and auth_user is not None:
            # by external id
            data = {
                "grant_type": "ext_id",
                "auth_service": auth_service,
                "auth_user": auth_user,
            }
            self._perform_authentication(dict(base, **data))

        elif username is not None and password is not None:
            # by username and password
            data = {
                "grant_type": "password",
                "username": username,
                "password": password,
            }
            self._perform_authentication(dict(base, **data))

        else:
            log.debug("empty authentication credentials")
            raise AuthenticationError(None, "empty authentication credentials")

    def _perform_authentication(self, data):
        """Use the provided parameters to authenticate with the Squirro
        platform.
        """

        # create endpoint url to fetch new tokens
        url = "%(endpoint)s/oauth2/token" % {"endpoint": self.user_api_url}

        session = self._new_session()

        try:
            r = session.post(url, data=data, timeout=self.timeout_secs)
        except self._requests.exceptions.RetryError as ex:
            raise RetryError(None, ex.args[0])
        except Exception as ex:
            log.debug("unable to connect to the Squirro platform: %r", ex)
            raise ConnectionError(None, ex)

        res = {}
        try:
            # decode the JSON response and store tokens
            if r.content:
                res = json.loads(r.content)
        except ValueError as ex:
            log.error("unable to decode JSON: %r", r.content)
            raise TransportError(r.status_code, ex)

        # perform error handling for known cases
        error = res.get("error")
        if r.status_code == 400:
            raise InputDataError(r.status_code, error)
        elif r.status_code in [403, 404, 410]:
            raise AuthenticationError(r.status_code, error)
        elif r.status_code != 200:
            raise UnknownError(r.status_code, error)

        # now we can set the tenant and user identifier as well
        if res.get("tenant"):
            self.tenant = res.get("tenant")
        if res.get("user_id"):
            self.user_id = res.get("user_id")
        self.user_permissions = res.get("role_permissions", [])
        self.token_project_permissions = res.get("project_permissions", None)
        self.user_information = res.get("user_information", {})

        # all is good and we store the new token
        self._on_token_refresh(res.get("access_token"), res.get("refresh_token"))

    def _on_token_refresh(self, access_token, refresh_token):
        """Method to be called if a new access token has been received for the
        user.
        """

        # assign class state and refresh the session
        self.access_token = access_token
        self.refresh_token = refresh_token

    def _new_session(self, access_token=None):
        """Create a `requests` session to use for communicating with the
        Squirro platform.
        """
        # construct headers to be used for all requests
        headers = dict(HEADERS)
        if access_token is not None:
            authorization = "Bearer %(token)s" % {"token": self.access_token}
            headers["Authorization"] = authorization

        session = self._requests.Session()
        session.headers.update(headers)

        # add retry capabilities
        if hasattr(self._requests, "adapters"):
            retries = self._requests.adapters.Retry(**self.retry)
            adapter = self._requests.adapters.HTTPAdapter(max_retries=retries)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

        return session

    def _perform_request(self, method, url, **kwargs):
        """Method to issue a request to the Squirro platform. If the OAuth
        access token has expired a new token is requested and the request
        retried exactly once.
        """

        # make sure that there is an access token and a refresh token,
        # otherwise we cannot continue
        if self.access_token is None and self.refresh_token is None:
            raise InputDataError(None, "missing access and refresh token")

        # make sure that the tenant is set
        if self.tenant is None:
            raise InputDataError(None, "missing tenant")

        # issue request and retry if authorization fails
        for retry_count in range(2):
            func = getattr(self.session, method)

            try:
                res = func(url, timeout=self.timeout_secs, **kwargs)
            except self._requests.exceptions.RetryError as ex:
                raise RetryError(None, ex.args[0])

            # check for failed authorization
            if retry_count == 0 and res.status_code == 401:

                # try to refresh the tokens, if that fails we return the
                # previous response
                successful = self._refresh_tokens()
                if not successful:
                    break

                log.debug("retrying request %r %r", method, url)

            else:
                break

        return res

    def _refresh_tokens(self, **kwargs):
        """Refresh the access token by using the refresh token."""

        # return value is whether we managed to receive a new token
        ret = False

        # first we make sure that we have a refresh token
        if not self.refresh_token:
            log.debug("unable to refresh access token, missing refresh token")
            return ret

        # login via the refresh token
        try:
            # Check that we have actually received a new access token.
            # On multi-node systems we may not get a new one because of
            # time-drift among the servers. Hence the server that we are about
            # to ask to refresh the token may not consider the access token
            # expired in contrast to a different server that has determined
            # the access token has expired and whose response has triggered
            # this `_refresh_tokens` request. Perform a couple of retries
            # in a "best effort" manner until we receive a new access token.
            previous_access_token = self.access_token

            for try_count in range(3):
                self.authenticate(refresh_token=self.refresh_token, **kwargs)

                if self.access_token != previous_access_token:
                    ret = True
                    break

                log.info(
                    "Access token %r not refreshed on behalf of "
                    "refresh token %r. Retry number %d",
                    self.access_token,
                    self.refresh_token,
                    try_count,
                )

        except Exception as ex:
            log.exception("unable to refresh access token: %r", ex)

        return ret

    def _process_response(self, res, expected_status_codes=None):
        """Return the data from the response if the status code matches to what
        is expected. If that is not the case the appropriate exception is
        being raised.
        """

        # work around mutable default arguments
        if expected_status_codes is None:
            expected_status_codes = [200]

        data = {}
        try:
            if res.content:
                data = json.loads(res.content)
        except ValueError as ex:
            log.error("unable to decode JSON: %r", res.content)
            raise TransportError(None, ex)

        # if the status code matches to what is expected we return the data
        if res.status_code in expected_status_codes:
            return data

        # raise the appropriate exception
        error = data.get("error")
        if res.status_code == 400:
            raise ClientError(res.status_code, error, data)

        elif res.status_code in [401, 403]:
            raise AuthorizationError(res.status_code, error)

        elif res.status_code == 404:
            raise NotFoundError(res.status_code, error)

        elif res.status_code == 409:
            raise ConflictError(res.status_code, error)

        else:
            raise UnknownError(res.status_code, error)

    def _format_date(self, d):
        """Converts a datetime object into a string date.

        :param d: :class:`datetime.datetime` instance.
        :returns: Date string with the format as specified in
            :attr:`ISO_DATE_FORMAT` If d is `None` an empty string is returned.
        """
        if d is None:
            return None
        return d.strftime(ISO_DATE_FORMAT)
