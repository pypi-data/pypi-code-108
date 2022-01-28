import logging

import requests
import http.client
import json
from datetime import datetime
from drb.exceptions import DrbException

logger = logging.getLogger("OAuth2.0")


class OAuth20ConnectionError (DrbException):
    pass


class OAuth20:
    """
    OAuth class manages OAuth token management, including renewal of expired
    token. Proposed methods allows generating tokens, and to performing remote
    service connection.
    The initialization of this class requires the token service information.
    The access token-based HTTP protocol used for authentication is Bearer.
    """
    def __init__(self, token_url, user, password, client_id,
                 client_secret=None):
        self.token_url = token_url
        self.user = user
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret

        self.token = None
        self.expire = None
        self.token_date = None

        self.refresh_token = None
        self.refresh_expire = None
        self.refresh_token_date = None

    def reset(self):
        self.token = None
        self.expire = None
        self.token_date = None

    @staticmethod
    def _expired(date: datetime, expire_time_s):
        """ check if the expired period is over """
        if expire_time_s is None or date is None:
            return True
        now = datetime.now()
        return (now - date).total_seconds() > expire_time_s

    def _init_token(self):
        # Case of refresh token expired: reset the token.
        if self._expired(self.refresh_token_date, self.refresh_expire):
            self.reset()
        # Case of token not expired (includes refresh expired
        if not self._expired(self.token_date, self.expire):
            return

        now = datetime.now()
        # token already exists: just try to refresh
        if self.token and self.refresh_token:
            logger.debug("Refreshing token.")
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
        else:
            logger.debug("Creating new token.")
            data = {
                'grant_type': 'password',
                'username': self.user,
                'password': self.password
            }
        self.refresh_token_date = now
        self.token_date = now

        access_token_response = requests.post(
            self.token_url, data=data, verify=True, allow_redirects=False,
            auth=(self.client_id, self.client_secret))

        if access_token_response.status_code >= 400:
            raise OAuth20ConnectionError(
                "Connection to fails with code " +
                f"{access_token_response.status_code}: " +
                f"{http.client.responses[access_token_response.status_code]}")

        tokens = json.loads(access_token_response.text)
        self.expire = int(tokens.get('expires_in', tokens.get('expires', 200)))
        self.token = tokens.get('access_token')
        self.refresh_token = tokens.get('refresh_token')
        self.refresh_expire = tokens.get('refresh_expires_in',
                                         tokens.get('refresh_expires', None))
        if not self.token:
            raise OAuth20ConnectionError("No token found.")

    def get_token(self):
        self._init_token()
        return self.token

    def get(self, url, session=None):
        self._init_token()
        caller = requests
        if session:
            caller = session
        api_call_headers = {'Authorization': 'Bearer ' + self.token}
        return caller.get(url, headers=api_call_headers)
