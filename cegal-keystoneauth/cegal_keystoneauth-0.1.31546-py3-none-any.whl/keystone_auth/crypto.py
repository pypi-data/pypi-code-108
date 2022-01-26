# Copyright 2021 Cegal AS
# All rights reserved

import base64
import datetime
import os
import struct

import jwt
from cegal.keystone_auth import logger, verify_tls
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

__all__ = ["verify_access_token"]


def verify_access_token(access_token, issuer, jwks_uri, context, audience=None):
    algorithms = ["RS256"]
    options = {"verify_exp": True, "verify_iss": True}
    signing_key = _signing_key(access_token, jwks_uri, context)
    leeway = datetime.timedelta(seconds=10)
    if audience == None:
        payload = jwt.decode(
            access_token,
            issuer=issuer,
            key=signing_key,
            algorithms=algorithms,
            options=options,
            leeway=leeway,
        )
    else:
        payload = jwt.decode(
            access_token,
            issuer=issuer,
            audience=audience,
            key=signing_key,
            algorithms=algorithms,
            options=options,
            leeway=leeway,
        )

    if os.environ.get("CEGAL_KEYSTONE_INJECT_FAILURE"):
        raise Exception("CEGAL_KEYSTONE_INJECT_FAILURE")

    if payload == None:
        raise Exception("Invalid access token.")


def _intarr2long(arr):
    return int("".join(["%02x" % byte for byte in arr]), 16)


def _base64_to_long(data):
    if isinstance(data, str):
        data = data.encode("ascii")

        _d = base64.urlsafe_b64decode(bytes(data) + b"==")
        return _intarr2long(struct.unpack("%sB" % len(_d), _d))


def _long_to_base64(data):
    bs = bytearray()
    while data:
        bs.append(data & 0xFF)
        data >>= 8

    bs.reverse()
    return base64.urlsafe_b64encode(bs).decode("ascii")


def _convert_to_pem(jwk):
    exponent = _base64_to_long(jwk["e"])
    modulus = _base64_to_long(jwk["n"])
    numbers = RSAPublicNumbers(exponent, modulus)
    public_key = numbers.public_key(backend=default_backend())
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem


def _signing_key(access_token, jwks_uri, context):
    token_headers = jwt.get_unverified_header(access_token)
    kid = token_headers["kid"]

    req = context.identity_server.signing_keys(jwks_uri, verify_tls)
    jwks = req.json()
    for jwk in jwks["keys"]:
        if jwk["kid"] == kid:
            pem = _convert_to_pem(jwk)
            return pem
        else:
            raise Exception("No matching signing keys")
