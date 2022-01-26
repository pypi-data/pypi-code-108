# Copyright 2021 Cegal AS
# All rights reserved

from base64 import urlsafe_b64encode
from hashlib import sha256
from secrets import token_urlsafe


class _Pkce:
    def __init__(self) -> None:
        self.code_verifier = token_urlsafe(49)
        code_verifier_sha256 = sha256(self.code_verifier.encode("utf-8")).digest()
        code_challenge_enc = urlsafe_b64encode(code_verifier_sha256)
        self.code_challenge = code_challenge_enc.decode("utf-8")[:-1]
