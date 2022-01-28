"""Module for handling authentication."""


import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
import requests
from jwt import PyJWK, PyJWKClient, PyJWTError

from peachpayments_partner import config
from peachpayments_partner.exceptions import AuthError
from peachpayments_partner.jwt_formatter import TokenFormatter

jwks_client = PyJWKClient(config.AUTH0_JWKS_URL)


def validate_token(value: str) -> str:
    """Validates token.

    Args:
       - value (str): JWT token string

    Returns:
        a validated token

    Raises:
        AuthError if invalid token is provided
    """
    if not isinstance(value, str):
        raise AuthError("Invalid token type, expecting token of type str")
    parts = value.split()

    if len(parts) != 2:
        raise AuthError("Invalid Authorization token, must be Bearer <token>")

    if len(parts) == 2 and parts[0].lower() != "bearer":
        raise AuthError("Authorization header must start with Bearer")

    is_valid_token = TokenFormatter.is_valid_jwt(parts[1])
    if not is_valid_token:
        raise AuthError("Invalid JWT format provided")
    # Get just the token part of the string
    return parts[1]


def get_key(token: str) -> PyJWK:
    """Gets key using JWT token.

    Args:
        - token (str) : JWT token to be checked for authentication

    Returns:
        a jwt.PyJWK key

    Raises:
        AuthError if key generation fails
    """
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
    except PyJWTError as key_error:
        raise AuthError("Key generation failed") from key_error
    return signing_key


def is_authenticated(token: str, signing_key: Optional[str] = None, audience: Optional[str] = None) -> bool:
    """Checks if a token is created by PeachPayments for the right audience.

    Args:
        - token (str) : JWToken to be checked for authentication

    Kwargs:
        - signing_key (str): key to decode the token, default: None
        - audience (str): recipient that the JWToken is intended for, default: None

    Returns:
         ``True`` if token is valid and intended for the audience

    Raises:
        RuntimeError if audience is not provided or configured.
        AuthError for decode errors.

    The ``signing_key``, if not provided, is collected from the address served by PeachPayments.
    The audience, if not provided, is collected from the environment variable ``AUTH0_AUDIENCE``.
    """
    valid_token = validate_token(token)
    aud = audience or os.getenv("AUTH0_AUDIENCE")
    if not aud:
        raise RuntimeError("Audience is not set")

    key = signing_key or get_key(valid_token).key

    try:
        jwt.decode(valid_token, key, algorithms=["RS256"], audience=aud)
    except PyJWTError as decode_error:
        raise AuthError("Token validation Failed") from decode_error

    return True


_access_token_cache: Dict[str, Dict[str, Any]] = {}


def get_access_token(client_id: str, client_secret: str, audience: str) -> str:
    """Retrieve an access token for a client id+secret pair.

    Also caches the token for a period of time to reduce network traffic when creating a token.

    Args:
       - client_id (str): Application client id
       - client_secret (str): Application client secret
       - audience (str): Token audience

    Returns:
        An access token for use with Peach services

    Raises:
        AuthError if an access token cannot be retrieved.
    """
    key = f"{client_id}:{client_secret}"
    if key in _access_token_cache:
        value = _access_token_cache[key]
        if datetime.utcnow() < value.get("expiration", datetime.utcnow()):
            token: str = value.get("value", "")
            return token
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
    }
    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": config.AUTHENTICATION_GRANT_TYPE,
    }

    response = requests.post(f"{config.AUTH0_URL}oauth/token", json=body, headers=headers)

    if not response.ok:
        raise AuthError("Unable to retrieve an access token.")

    response_body: dict = response.json()
    expires_in = timedelta(seconds=response_body.get("expires_in", 5) - 5)
    access_token: str = response_body.get("access_token", "")

    _access_token_cache.update(
        {
            key: {
                "value": access_token,
                "expiration": datetime.utcnow() + expires_in,
            }
        }
    )

    return access_token
