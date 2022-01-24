from getpass import getpass

from requests import Response
from seclea_utils.core import Transmission

from seclea_ai.exceptions import AuthenticationError

from .storage import Storage

try:
    import google.colab  # noqa F401

    IN_COLAB = True
except ImportError:
    IN_COLAB = False


def handle_response(res: Response, msg):
    if not res.ok:
        print(f"{msg}: {res.status_code} - {res.reason} - {res.text}")


class AuthenticationService:
    def __init__(self, transmission: Transmission):
        self._transmission = transmission
        self._db = Storage(db_name="auth_service", root="." if IN_COLAB else None)
        self._path_token_obtain = "/api/token/obtain/"
        self._path_token_refresh = "/api/token/refresh/"
        self._path_token_verify = "/api/token/verify/"
        self._key_token_access = "access_token"
        self._key_token_refresh = "refresh_token"

    def authenticate(self, transmission: Transmission = None, username=None, password=None):
        """
        Attempts to authenticate with server and then passes credential to specified transmission

        :param transmission: transmission service we wish to authenticate
        :return:
        """
        if not self.refresh_token():
            self._obtain_initial_tokens(username=username, password=password)
        if not self.verify_token():
            raise AuthenticationError("Failed to verify token")
        transmission.cookies = self._transmission.cookies

    def verify_token(self) -> bool:
        """
        Verifies if access token in database is valid
        :return: bool valid
        """
        self._transmission.cookies = {self._key_token_access: self._db.get(self._key_token_access)}

        response = self._transmission.send_json(url_path=self._path_token_verify, obj={})
        return response.status_code == 200

    def refresh_token(self) -> bool:
        """
        Refreshes the access token by posting the refresh token.
        :return: bool success
        """
        if not self._db.get(self._key_token_refresh):
            return False
        self._transmission.cookies = {
            self._key_token_refresh: self._db.get(self._key_token_refresh)
        }
        response = self._transmission.send_json(url_path=self._path_token_refresh, obj={})
        self._save_response_tokens(response)
        return response.status_code == 200

    def _request_user_credentials(self) -> dict:
        """
        Gets user credentials manually
        :return:
        """
        return {"username": input("Username: "), "password": getpass("Password: ")}

    def _save_response_tokens(self, response) -> None:
        """
        Saves refresh and access tokens into db
        :param response:
        :return:
        """
        if self._key_token_refresh in response.cookies:
            self._db.write(self._key_token_refresh, response.cookies[self._key_token_refresh])
        if self._key_token_access in response.cookies:
            self._db.write(self._key_token_access, response.cookies[self._key_token_access])

    def _obtain_initial_tokens(self, username=None, password=None):
        if username is None or password is None:
            credentials = self._request_user_credentials()
        else:
            credentials = {"username": username, "password": password}
        response = self._transmission.send_json(url_path=self._path_token_obtain, obj=credentials)
        if response.status_code != 200:
            raise AuthenticationError(f"status:{response.status_code}, content:{response.content}")
        self._save_response_tokens(response)
