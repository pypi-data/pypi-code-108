from requests import Session

from myst_v1alpha1.exceptions import UnAuthenticatedError
from myst_v1alpha1.google_id_token_auth import GoogleIDTokenAuth
from myst_v1alpha1.utils.core_utils import get_user_agent
from myst_v1alpha1.utils.requests_utils import fetch_json_content


class Client(object):
    """HTTP client for interacting with the Myst API."""

    def __init__(self, credentials=None):
        """A `Client` instance is initialize with credentials and session configuration parameters.

        Args:
            credentials (
                google.oauth2.credentials.Credentials or
                google.oauth2.service_account.IDTokenCredentials or
                google.auth.credentials.AnonymousCredentials, optional
            ): user or service account credentials to authenticate the client using
        """
        self._credentials = credentials
        self._auth = None

        # Initialize the `requests` session.
        self._session = self._init_session(session=Session())

        # If credentials were provided, initialize authorization and authorize session.
        if self._credentials is not None:
            self.authenticate(credentials=self._credentials)

    def _init_session(self, session):
        """Initializes a `requests` session.

        Args:
            session (requests.Session): session to initialize

        Returns:
            session (requests.Session): initialized session
        """
        # Add error handling and custom headers.
        session.headers.update({"User-Agent": get_user_agent()})

        return session

    @property
    def session(self):
        """The `requests` session to use to make authenticated requests to the Myst API.

        Returns:
            session (requests.Session): session to make authenticated requests to the Myst API with

        Raises:
            ValueError: You need to authenticate first before using the session.
        """
        if self._auth is None:
            raise UnAuthenticatedError("You need to authenticate first using `myst_v1alpha1.authenticate(...)`.")
        return self._session

    def authenticate(self, credentials):
        """Authenticates this client using the given credentials.

        Note that this also adds the appropriate `Authorization` header to the session.

        Args:
            credentials (
                google.oauth2.credentials.Credentials,
                google.oauth2.service_account.IDTokenCredentials, or
                google.auth.credentials.AnonymousCredentials
            ): user or service account credentials to authenticate the client using
        """
        self._credentials = credentials
        self._auth = GoogleIDTokenAuth(credentials=credentials)
        self._auth.refresh()
        self._session.auth = self._auth

    def get(self, url):
        """Makes an authorized HTTP 'GET` request to the given Myst API endpoint.

        Args:
            url (str): Myst API endpoint to make request to

        Returns:
            json_response (dict): json response
        """
        json_response = fetch_json_content(session=self.session, request_url=url)
        return json_response
