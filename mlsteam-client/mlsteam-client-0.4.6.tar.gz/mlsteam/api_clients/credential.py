import os
import json
import base64
from mlsteam import envs
from mlsteam.exceptions import (
    MLSteamMissingApiTokenException,
    MLSteamInvalidApiTokenException,
)

class Credential(object):
    def __init__(self, token):
        if token is None:
            token = os.getenv(envs.API_TOKEN_ENV)
        if token is None:
            raise MLSteamMissingApiTokenException()
        token_dict = self.api_token_to_dict(token)
        if "api_address" not in token_dict:
            raise MLSteamInvalidApiTokenException()
        self._api_address = token_dict["api_address"]
        self._api_token = token

    def api_token_to_dict(self, api_token):
        try:
            tokend = {}
            tokens = api_token.split('.')
            if len(tokens) != 3:
                raise MLSteamInvalidApiTokenException()
            tokend = self.token_decode(tokens[0])
            tokend.update(self.token_decode(tokens[1]))
            return tokend
        except Exception:
            raise MLSteamInvalidApiTokenException()

    def token_decode(self, token):
        try:
            tokenb = token.encode() + b'=' * (-len(token) % 4)
            return json.loads(base64.b64decode(tokenb).decode('utf-8'))
        except Exception:
            raise MLSteamInvalidApiTokenException()

    @property
    def api_token(self):
        return self._api_token

    @property
    def api_address(self):
        return self._api_address
