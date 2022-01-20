# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#      https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""Q-CTRL API authentication module."""
import re
import time
from typing import (
    Callable,
    Dict,
    Tuple,
)

import jwt
from aiohttp.client_reqrep import helpers as aio_helpers
from requests.auth import AuthBase

from .exceptions import QctrlException


class ClientAuthBase(aio_helpers.BasicAuth, AuthBase):
    """Base class that defines the signature for other authentication classes
    to be used either synchronously with `requests` or asynchronously with
    `aiohttp`.

    Inherited classes must define `encode(self)` method that returns the
    `Authorization` header value.
    """

    def __new__(  # pylint: disable=signature-differs,unused-argument
        cls, *args
    ) -> Tuple:
        """Overrides `__new__()` from `aiohttp` BasicAuth to allow other
        authentication methods.

        Parameters
        ----------
        *args
            argument list for instantiating ClientAuthBase.

        Returns
        -------
        Tuple
            a ClientAuthBase object accept new authentication methods.
        """
        return tuple.__new__(cls, args)

    def __call__(self, r):
        r.headers["Authorization"] = self.encode()
        return r

    def encode(self) -> str:
        """Method that returns the value to be sent on `Authorization`
        header."""
        raise NotImplementedError()

    def __repr__(self):
        return AuthBase.__repr__(self)


class BearerTokenAuth(ClientAuthBase):
    """Represents BearerTokenAuth Model."""

    REFRESH_THRESHOLD = 30  # seconds
    REQUIRED_PRODUCT = re.compile("boulder opal", re.IGNORECASE)

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        refresh_client: Callable[[str], Tuple[str, str]] = None,
        token_observer: Callable[[Dict[str, str]], None] = None,
    ):
        """
        Parameters
        ----------
        access_token: str
            A valid access token.
        refresh_token: str
            A valid refresh token.
        refresh_client: callable
            A callable that accepts a valid refresh token string as the only
            argument and returns a new pair of access token and refresh token.
        token_observer: callable
            A callable that accepts a dict as the only argument that contains
            the access token and refresh token.
        """
        super().__init__()
        self._refresh_client = refresh_client
        self._token_observer = token_observer or (lambda *_: None)
        self._set_tokens(access_token, refresh_token)

    @staticmethod
    def get_expiry(token: str) -> float:
        """
        Returns the token expire time.

        Parameters
        ----------
        token: str
            the token to be examined.

        Returns
        -------
        float
            the expire time of the token.

        Raises
        ------
        KeyError
            if there's no `exp` field in the jwt token.
        """
        payload = jwt.decode(token, options={"verify_signature": False})

        if "exp" not in payload:
            raise KeyError(f"no expiry found in payload: {payload}")

        return payload["exp"]

    def _expires_soon(self) -> bool:
        """Checks if the access token will expire soon e.g. within
        REFRESH_THRESHOLD seconds.

        Returns
        -------
        bool
            True if it expires soon, False otherwise.
        """
        return self._expires_at - time.time() < self.REFRESH_THRESHOLD

    def _set_tokens(self, access_token: str, refresh_token: str):
        self._check_subscription(access_token)
        self._access_token = access_token
        self._expires_at = self.get_expiry(access_token)
        self._refresh_token = refresh_token
        self._token_observer(
            {"access_token": access_token, "refresh_token": refresh_token}
        )

    @classmethod
    def _check_subscription(cls, access_token: str) -> None:
        """Checks if the user belongs to the access token has the required
        subscription. If the user does not have the subscription, it will
        raise exception.

        Parameters
        ----------
        access_token: str
            jwt access token

        Raises
        ------
        QctrlException
            the subscription is invalid.
        """
        payload = jwt.decode(access_token, options={"verify_signature": False})

        # don't check subscription for superusers
        if payload.get("is_superuser", False):
            return

        found = any(
            cls.REQUIRED_PRODUCT.search(product) for product in payload["products"]
        )

        if not found:
            raise QctrlException(
                "Access not allowed due to invalid subscription."
                " Please contact support@q-ctrl.com if you would like to reactivate your access."
            )

    @property
    def access_token(self) -> str:
        """Returns the access token and handles refreshing.

        Returns
        -------
        str
            jwt access token.
        """
        if self._expires_soon():
            self._refresh_tokens()

        return self._access_token

    def _refresh_tokens(self) -> None:
        """Uses the current refresh token to obtain a new access token and
        refresh token.
        """
        access, refresh = self._refresh_client(self._refresh_token)
        self._set_tokens(access, refresh)

    def encode(self) -> str:
        return f"Bearer {self.access_token}"
