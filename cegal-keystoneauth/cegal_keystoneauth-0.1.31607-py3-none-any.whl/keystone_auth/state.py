# Copyright 2021 Cegal AS
# All rights reserved

from base64 import urlsafe_b64encode
from hashlib import sha256
from http.cookies import Morsel, SimpleCookie
from json import dumps

from cegal.keystone_auth import logger as logger


class _State:
    def __init__(self, code_verifier, after_auth) -> None:
        self.state = {"code_verifier": code_verifier, "after_auth": after_auth}
        self.state_enc = urlsafe_b64encode(str.encode(dumps(self.state)))
        self.state_enc_hashed = sha256(self.state_enc).digest()
        # logger.debug("Cookie info: %s", str(self.cookie))

    def cookie(self, path):
        cookie = (
            "Cookie",
            f"state={self.state_enc};samesite=none;httponly=true;secure=true;path={path}",
        )
        return cookie

    # @property
    # def cookie(self):
    #     morsel = Morsel()
    #     morsel.set("state", self.state_enc, self.state_enc)
    #     morsel.set("samesite", "None", "None")
    #     morsel["httponly"] = True
    #     morsel["secure"] = True
    #     morsel["path"] = "http://localhost"
    #     return morsel
