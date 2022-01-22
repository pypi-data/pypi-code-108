from .jwt import FlyJWT
from .config import _JWTConfig
import jwt
from datetime import datetime
from calendar import timegm


def create_refresh_token(payload, exp, **kwargs):
    return _create_token(payload, exp, **kwargs)

def create_access_token(payload, exp, **kwargs):
    return _create_token(payload, exp, **kwargs)

"""

    Create refresh token:
    @param paylaod(dict):           Payload(Data) of JWT
    @param exp(int):                How long the refresh token is valid since this function was called.(in seconds). Expiration time is UTC datetime of now + @exp.
    @param nbf(int or datetime):    time when refresh token become valid.
    @param iss(str):                string to identify the person(service) that issued the refresh token.
    @param aud(str):                string to identify the person(service) that is issued the refresh token.
    @param iat(int or datetime):    time at which refresh token was issued.
"""
def _create_token(payload, exp, **kwargs):
    if not isinstance(payload, dict):
        raise TypeError("payload must be dict type.")

    _pay = dict()
    # UTC timestamp (in seconds)
    _now_utc = timegm(datetime.utcnow().utctimetuple())
    _exp_utc = _now_utc + exp
    _pay["exp"] = _exp_utc

    nbf = kwargs.get("nbf")
    iss = kwargs.get("iss")
    aud = kwargs.get("aud")
    iat = kwargs.get("iat")
    if nbf is not None:
        _pay["nbf"] = nbf
    if iss is not None:
        if not isinstance(iss, str):
            raise TypeError("iss must be str type.")
        _pay["iss"] = iss
    if aud is not None:
        if not isinstance(aud, str):
            raise TypeError("aud must be str type.")
        _pay["aud"] = aud
    if iat is not None:
        _pay["iat"] = iat

    payload.update(_pay)
    _conf = _JWTConfig(
            **kwargs
            )

    _jwt = FlyJWT(_conf)
    return _jwt.encode(payload)


def decode_refresh_token(
        token,
        algorithm,
        private_key=None,
        private_key_path=None,
        public_key=None,
        public_key_path=None,
        **kwargs):
    return _decode_token(
            token,
            algorithm=algorithm,
            private_key=private_key,
            private_key_path=private_key_path,
            public_key=public_key,
            public_key_path=public_key_path,
            **kwargs)


def decode_access_token(
        token,
        algorithm,
        private_key=None,
        private_key_path=None,
        public_key=None,
        public_key_path=None,
        **kwargs):
    return _decode_token(
            token,
            algorithm=algorithm,
            private_key=private_key,
            private_key_path=private_key_path,
            public_key=public_key,
            public_key_path=public_key_path,
            **kwargs)


def _decode_token(
        token,
        algorithm,
        private_key=None,
        private_key_path=None,
        public_key=None,
        public_key_path=None,
        **kwargs):
    if not isinstance(token, (str, bytes)):
        raise TypeError("token must be str type.")

    token_bytes = token.encode("utf-8") if isinstance(token, str) else token

    _conf = _JWTConfig(
            algorithm=algorithm,
            private_key=private_key,
            private_key_path=private_key_path,
            public_key=public_key,
            public_key_path=public_key_path,
            )
    _jwt = FlyJWT(_conf)
    return _jwt.decode(token_bytes, **kwargs)


