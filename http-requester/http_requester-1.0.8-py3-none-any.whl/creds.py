import datetime
from functools import partial
from typing import Callable


class UserCreds:
    email: str
    password: str

    def __init__(
            self,
            email: str,
            password: str,
            key: Callable[[str], str] = None
    ):
        self.email = key(email) if key else email
        self.password = key(password) if key else password

    @property
    def creds(self):
        return (self.email, self.password)


class Credentials:
    def __init__(
            self,
            token=None,
            api_key=None,
            refresh_token=None,
            client_id=None,
            client_secret=None,
            expiration=None,
            token_url=None,
            format_matrix=None,
            refresh_func=None
    ):
        self._token = token
        self._api_key = api_key
        self._refresh_token = refresh_token
        self._client_id = client_id
        self._client_secret = client_secret
        self._expiration = expiration
        self._token_url = token_url
        self._format_matrix = format_matrix
        self.refresh = partial(refresh_func, self) if refresh_func else None

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token

    @property
    def refresh_token(self):
        return self._refresh_token

    @property
    def api_key(self):
        return self._api_key

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @property
    def expiration(self):
        return self._expiration

    def format(self):
        if self.expired and self.refresh_token:
            self.refresh()
        return {
            cred_key: format_string.format(getattr(self, attr))
            for cred_key, (format_string, attr) in self._format_matrix
        }

    @property
    def valid(self):
        return (
                self._token is not None
                and not self.expired
        )

    @property
    def expired(self):
        if self._expiration is not None:
            return datetime.datetime.today() > self._expiration