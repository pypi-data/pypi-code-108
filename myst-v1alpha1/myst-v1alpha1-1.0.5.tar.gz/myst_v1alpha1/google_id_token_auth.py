import google.auth.credentials
import google.oauth2.credentials
import google.oauth2.service_account
from google.auth.transport.requests import Request
from requests.auth import AuthBase

from myst_v1alpha1.utils.auth_utils import create_bearer_authorization_header


class GoogleIDTokenAuth(AuthBase):
    """Google ID Token authentication for use with a `requests` session."""

    def __init__(self, credentials):
        self._credentials = credentials

    @property
    def id_token(self):
        """Returns the Google ID Token.

        To be able to support both user account and service account authentication, we actually use two slightly
        different looking Google `Credentials` classes.

        For service accounts, we use `google.oauth2.service_account.IDTokenCredentials` which stores its Google ID token
        in the `token` attribute.

        For user accounts, we use `google.oauth2.Credentials` which stores its Google ID token in the `id_token`.

        This also supports using anonymous credentials for making unauthenticated requests, however, we mainly reserve
        this use case for testing. If you do use anonymous credentials to send requests, note that you'll just see
        authentication errors returned by the Myst API.
        """
        if isinstance(self._credentials, google.oauth2.service_account.IDTokenCredentials):
            id_token = self._credentials.token
        elif isinstance(self._credentials, google.oauth2.credentials.Credentials):
            id_token = self._credentials.id_token
        elif isinstance(self._credentials, google.auth.credentials.AnonymousCredentials):
            id_token = None
        else:
            raise TypeError("Invalid credentials type.")
        return id_token

    def refresh(self):
        """Refreshes the authorization credentials."""
        # Note that anonymous credentials cannot be refreshed.
        if not isinstance(self._credentials, google.auth.credentials.AnonymousCredentials):
            if self._credentials.valid is False:
                self._credentials.refresh(request=Request())

    def __call__(self, request):
        """Adds a "Bearer" Authorization header to the request with the Google ID Token and returns the request.

        Args:
            request (requests.Request): request

        Args:
            request (requests.Request): request with authorization header
        """
        if self.id_token:
            bearer_authorization_header = create_bearer_authorization_header(token=self.id_token)
            request.headers.update(bearer_authorization_header)
        return request
