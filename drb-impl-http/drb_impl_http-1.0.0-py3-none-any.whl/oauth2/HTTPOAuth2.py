from requests.auth import AuthBase
from .oauth2 import OAuth20


class HTTPOAuth2(AuthBase):
    """Attaches HTTP OAuth 2.0 Authentication to the given Request object.
    The token is automatically renewed when expired thanks to
    :class:`~oauth2.OAuth20` class implementation.
    """

    def __init__(self, username, password, token_url, client_id,
                 client_secret=None):
        self.username = username
        self.password = password
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.oauth = OAuth20(
            user=self.username, password=self.password,
            token_url=self.token_url, client_id=self.client_id,
            client_secret=self.client_secret)

    def __eq__(self, other):
        return all([
            self.username == getattr(other, 'username', None),
            self.password == getattr(other, 'password', None),
            self.token_url == getattr(other, 'token_url', None),
            self.client_id == getattr(other, 'client_id', None),
            self.client_secret == getattr(other, 'client_secret', None)
        ])

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers = {'Authorization': 'Bearer ' + self.get_token()}
        return r

    def get_token(self):
        return self.oauth.get_token()
