from pymasmovil.client import Client
from pymasmovil.errors.exceptions import (
    MissingLoginCredentialsError,
    AutenthicationError,
)
import os


class Session:
    def __init__(self, session_id):
        self.session_id = session_id

    @classmethod
    def create(cls):

        route = "/v2/login-api"

        login_params = {"domain": os.getenv("MM_DOMAIN")}
        auth_data = {
            "username": os.getenv("MM_USER"),
            "password": os.getenv("MM_PASSWORD"),
        }

        if auth_data["username"] is None:
            raise MissingLoginCredentialsError("MM_USER")
        elif auth_data["password"] is None:
            raise MissingLoginCredentialsError("MM_PASSWORD")
        elif login_params["domain"] is None:
            raise MissingLoginCredentialsError("MM_DOMAIN")

        session = Client().post(route=route, params=login_params, body=auth_data)

        if not session["sessionId"]:
            raise AutenthicationError

        return Session(session["sessionId"])
