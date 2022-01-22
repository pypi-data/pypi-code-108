"""revtel fastapi package"""

from fastel.authorizers import (
    ClientIdAuth,
    ClientSecretAuth,
    Credential,
    JWBaseAuth,
    StaticClientAuth,
    StaticJWTAuth,
    StaticSecretAuth,
)
from fastel.cart.exceptions import CartException, cart_exception_handler
from fastel.collections import set_collections
from fastel.exceptions import APIException, api_exception_handler

__version__ = "1.13.10"
__all__ = [
    "APIException",
    "api_exception_handler",
    "ClientIdAuth",
    "ClientSecretAuth",
    "Credential",
    "JWBaseAuth",
    "StaticClientAuth",
    "StaticSecretAuth",
    "StaticJWTAuth",
    "cart_exception_handler",
    "CartException",
    "set_collections",
]
