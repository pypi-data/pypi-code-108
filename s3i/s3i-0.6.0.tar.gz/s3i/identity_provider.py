import requests
import json
from enum import Enum
import time
import threading
from jwt.algorithms import RSAPSSAlgorithm
from jwt import DecodeError, ExpiredSignature, InvalidTokenError
import jwt
from s3i.exception import S3IIdentityProviderError, raise_error_from_response
from s3i.logger import APP_LOGGER

class TokenType(Enum):
    """Enum TokenType covers all available tokens specified in openID connect"""

    # COMPLETE_BUNDLE = 1
    ID_TOKEN = 2
    ACCESS_TOKEN = 3
    REFRESH_TOKEN = 4


class IdentityProvider:
    """ Class IdentityProvider contains functions to communicate with S3I IdentityProvider """

    def __init__(self, grant_type, client_id, client_secret, realm="KWH",
                 identity_provider_url="https://idp.s3i.vswf.dev/", username=None,
                 password=None):
        """
        Constructor

        :param grant_type: grant type to obtain JWT. Here only the types "password" and "client_credentials" are implemented. In subsequent version authorization_code will be implemented 
        :type grant_type: str
        :param client_id: id of registered client in S3I IdentityProvider
        :type client_id: str 
        :param client_secret: credential of registered client in S3I IdentityProvider which must corredspond to client id 
        :type client_secret: str 
        :param realm: registered realm in S3I IdentityProvider 
        :type realm: str
        :param identity_provider_url: url of S3I IdentityProvider 
        :type identity_provider_url: str 
        :param username: username of registered user in S3I IdentityProvider. If grant type is set up as password, this field must be filled 
        :type username: str 
        :param password: password of registered user in S3I IdentityProvider. If grant type is set up as password, this field must be filled 
        :type password: str

        """
        self._grant_type = grant_type
        self._client_id = client_id
        self._client_secret = client_secret
        self._realm = realm
        self._username = username
        self._password = password
        self._identity_provider_url = identity_provider_url
        self._identity_provider_get_token = self.identity_provider_url + \
                                            "auth/realms/" + self.realm + "/protocol/openid-connect/token"
        self._identity_provider_header = {
            "Content-Type": "application/x-www-form-urlencoded"}
        self._token_bundle = None
        self._token_inspector_run = False
        self._last_login = 0
        self._identity_provider_get_pub_key = self.identity_provider_url + \
                                              "auth/realms/" + self.realm + "/protocol/openid-connect/certs"

    @property
    def identity_provider_url(self):
        """Url of S3I IdentityProvider
        """
        return self._identity_provider_url

    @property
    def identity_provider_get_token(self):
        """Url to obtain a token from the S3I IdentityProvider
        """
        return self._identity_provider_get_token

    @property
    def identity_provider_header(self):
        """Header which is sent to the S3I IdentityProvider via HTTP
        """
        return self._identity_provider_header

    @property
    def grand_type(self):
        """OAuth grant type which is used
        """
        return self._grant_type

    @property
    def client_id(self):
        """
        """
        return self._client_id

    @property
    def client_secret(self):
        """
        """
        return self._client_secret

    @property
    def realm(self):
        """
        """
        return self._realm

    @property
    def username(self):
        """
        """
        return self._username

    @property
    def password(self):
        """
        """
        return self._password

    def stop_run_forever(self):
        """ Stops the run forever loop when the next iteration happens """
        self._token_inspector_run = False

    def get_token(self, token_type, request_new=False, scope="openid"):
        """ 
        Returns a token from the S3I IdentityProvider, request a new one if there is no valid token available
        Works only if the IdentityProvider is NOT in the run_forever loop

        :param token_type: type of token, see enum TokenType
        :type token_type: enum
        :param request_new: request a new token in any case
        :type request_new: bool
        :param scope: client scope
        :type scope: str
        :return: token
        :rtype: str
        """
        if self._token_inspector_run:
            return None
        if request_new:
            self._authenticate(scope=scope)
        else:
            if self._token_bundle is None:
                self._authenticate(scope=scope)
            if self._time_until_token_valid() <= 0:
                self._authenticate(scope=scope)
        # all tokens are valid
        if token_type == TokenType.ACCESS_TOKEN:
            return self._token_bundle["access_token"]
        elif token_type == TokenType.ID_TOKEN:
            return self._token_bundle["id_token"]
        elif token_type == TokenType.REFRESH_TOKEN:
            return self._token_bundle["refresh_token"]
        return None

    def get_certs(self):
        """
        Return a certificate of S³I Identity Provider

        """
        certs = requests.get(url=self._identity_provider_get_pub_key,
                             headers={"Authorization": "Bearer {}".format(
                                 self.get_token(token_type=TokenType.ACCESS_TOKEN))})
        return certs.json()

    def verify_token(self, token, aud="rabbitmq"):
        """
        This function verifies if the given jwt token is issued by the S³I Identity Provider
 
        :param token: jwt token
        :type token: str
        :param aud: audience, by default rabbitmq.
        :type aud: str
        :return: True if token is issued by S³I, else False
        :rtype: bool
        """
        keys = self.get_certs().get("keys")
        """search public key"""
        for key in keys:
            if key["alg"] == "RS256" and key["kty"] == "RSA" and key["use"] == "sig":
                public_key = RSAPSSAlgorithm.from_jwk(json.dumps(key))
                break
        try:
            """decode the access token with public key that was searched above"""
            jwt.decode(jwt=token, verify=True, key=public_key, algorithms=['RS256'], audience=aud)
        except (DecodeError, ExpiredSignature, InvalidTokenError):
            return False
        else:
            return True

    def run_forever(self, token_type, on_new_token, sleep_interval=5, scope=""):
        """ 
        Requests tokens from the S³I IdentityProvider and refreshs them if they reach their timeout

        :param token_type: type of token, see enum TokenType (REFRESH_TOKEN is no valid param)
        :type token_type: enum
        :param on_new_token: callback if a new token is available
        :type on_new_token: callback
        :param scope: client scope
        :type scope: str
        """
        if token_type == TokenType.REFRESH_TOKEN:
            return None
        on_new_token(self.get_token(token_type, request_new=True, scope=scope))
        self._token_inspector_run = True
        threading._start_new_thread(
            self._run_forever_loop, (token_type, on_new_token, sleep_interval, scope))

    def _run_forever_loop(self, token_type, on_new_token, slep_interval, scope=""):
        while True and self._token_inspector_run:
            while True:
                if not self._token_inspector_run:
                    return None  # exit
                if self._time_until_token_valid() > slep_interval * 2:
                    time.sleep(slep_interval)
                else:
                    break
            # its time to refresh the tokens
            APP_LOGGER.info("request for new token")
            APP_LOGGER.info("last login: {}, now: {}, expires in: {}".format(self._last_login,
                                                                             time.time(),
                                                                             self._token_bundle["expires_in"]))
            if self._token_bundle["expires_in"] < 60:
                ### keycloak returns an unexpected token expire time
                self._authenticate(scope=scope)
            else:
                self._refresh_token(self._token_bundle["refresh_token"], scope)
            if token_type == TokenType.ACCESS_TOKEN:
                on_new_token(self._token_bundle["access_token"])
            elif token_type == TokenType.ID_TOKEN:
                on_new_token(self._token_bundle["id_token"])

    def _authenticate(self, scope):
        """ Request the token-bundle from the S³I IdentityProvider 
        
            :param scope: client scope
            :type scope: str 
        """

        self._last_login = time.time()
        body = dict()
        body["grant_type"] = self._grant_type
        body["client_id"] = self._client_id
        body["client_secret"] = self._client_secret
        if self.grand_type == "password":
            body["username"] = self._username
            body["password"] = self._password
        if scope:
            body["scope"] = scope
        response = requests.post(url=self._identity_provider_get_token,
                                 data=body, headers=self._identity_provider_header)
        response_json = raise_error_from_response(response, S3IIdentityProviderError, 200)
        self._token_bundle = response_json

    def _refresh_token(self, token, scope=""):
        """ Refreshes the given token

        :param token: type of token, see enum TokenType
        :type token: str
        """
        self._last_login = time.time()
        body = dict()
        body["grant_type"] = "refresh_token"
        body["client_id"] = self._client_id
        body["client_secret"] = self._client_secret
        body["refresh_token"] = token
        if scope:
            body["scope"] = scope
        response = requests.post(url=self._identity_provider_get_token,
                                 data=body, headers=self._identity_provider_header)
        response_json = raise_error_from_response(response, S3IIdentityProviderError, 200)
        self._token_bundle = response_json

    def _time_until_token_valid(self):
        """ Returns the time until the token expires """
        time_token_valid = self._token_bundle["expires_in"]
        time_since_login = time.time() - self._last_login
        return time_token_valid - time_since_login
