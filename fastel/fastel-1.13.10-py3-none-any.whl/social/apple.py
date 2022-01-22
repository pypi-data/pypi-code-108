from datetime import datetime, timezone
from typing import Any, Dict

import requests
from jwt.algorithms import get_default_algorithms
from jwt.api_jwt import decode, decode_complete


class AppleLogin:
    @classmethod
    def decode_id_token(cls, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        unverified = decode_complete(token, options={"verify_signature": False})

        signing_keys = requests.get("https://appleid.apple.com/auth/keys").json()
        for key in signing_keys["keys"]:
            if key["kid"] == unverified["header"]["kid"]:
                signing_key = key
                break

        algo = get_default_algorithms()["RS256"]  # type: ignore

        signing_key = algo.from_jwk(signing_key)
        verified = decode(
            token, key=signing_key, algorithms=["RS256"], options={"verify_aud": False}
        )

        if verify_exp:
            now = datetime.now(timezone.utc).timestamp()
            if now > verified["exp"]:
                raise RuntimeError("Apple id token expired")

        return verified
