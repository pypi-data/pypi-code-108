from dataclasses import dataclass
from typing import Optional, List

from seeq import spy
from seeq.sdk import *
from seeq.sdk.configuration import ClientConfiguration
from seeq.spy import _url
from seeq.spy._config import Options


@dataclass(repr=False)
class Session:
    """
    Used to segregate Seeq Server logins and allows for multi-server /
    multi-user concurrent logins. This object encapsulates all server-
    specific state, SPy options and API client configuration.

    Examples
    --------
    Log in to two different servers at the same time:

    >>> session1 = Session()
    >>> session2 = Session()
    >>> spy.login(url='https://server1.seeq.site', username='mark', password='markpassword', session=session1)
    >>> spy.login(url='https://server2.seeq.site', username='alex', password='alexpassword', session=session2)
    """
    options: Options = None
    client_configuration: ClientConfiguration = None
    _client: Optional[ApiClient] = None
    _user: Optional[UserOutputV1] = None
    _public_url: Optional[str] = None
    _private_url: Optional[str] = None
    _server_version: Optional[str] = None
    supported_units: Optional[set] = None
    corporate_folder: Optional[FolderOutputV1] = None
    auth_providers: Optional[List[DatasourceOutputV1]] = None
    https_verify_ssl: bool = True
    https_key_file: Optional[str] = None
    https_cert_file: Optional[str] = None

    def __init__(self, options: Options = None, client_configuration: ClientConfiguration = None):
        self.client_configuration = client_configuration if client_configuration is not None else ClientConfiguration()
        self.options = options if options is not None else Options(self.client_configuration)

    def __repr__(self):
        if not self.client:
            return 'Not logged in'
        url_part = self.public_url
        if self.private_url != self.public_url:
            url_part += f' ({self.private_url})'
        return f'{url_part} as {self.user.name} ({self.user.username})'

    def __getstate__(self):
        # We can only pickle certain members. This has to mirror __setstate__().
        return self.options

    def __setstate__(self, state):
        self.options = state

    @staticmethod
    def validate(session):
        return spy.session if session is None else session

    def clear(self):
        """
        Re-initializes the object to a "logged out" state. Note that this
        function does NOT reset API client configuration or SPy options.
        """
        self.client = None
        self.user = None
        self.public_url = None
        self.private_url = None
        self.server_version = None
        self.supported_units = None
        self.corporate_folder = None
        self.auth_providers = None
        self.https_verify_ssl = True
        self.https_key_file = None
        self.https_cert_file = None

    # Prior to the advent of Session objects, the spy.client, spy.user and spy.server_version module-level variables
    # were exposed to end-users as a convenience. The setters below copy those (now) Session variables to those
    # legacy module-level locations for backward compatibility purposes. (Only if this Session object is the default
    # Session.)
    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value
        if self is spy.session:
            spy.client = self._client

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value
        if self is spy.session:
            spy.user = self._user

    @property
    def server_version(self):
        return self._server_version

    @server_version.setter
    def server_version(self, value):
        self._server_version = value
        if self is spy.session:
            spy.server_version = self._server_version

    @property
    def public_url(self):
        return self._public_url

    @public_url.setter
    def public_url(self, value):
        self._public_url = _url.cleanse_url(value)

    @property
    def private_url(self):
        return self._private_url

    @private_url.setter
    def private_url(self, value):
        self._private_url = _url.cleanse_url(value)

    def get_api_url(self):
        """
        Returns the URL to use for API calls, which ends up being the
        private URL (if specified) or the public URL.
        """
        return f'{self.private_url}/api'
