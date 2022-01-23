"""
Nozomi
Internal Key Module
Copyright Amatino Pty Ltd
"""
import hmac
from nozomi.http.headers import Headers
from collections.abc import Mapping


class InternalKey:
    """
    Default implementation of a key authenticating requests from internal
    applications.
    """
    def __init__(
        self,
        key: str,
        header_key: str
    ) -> None:

        self._key = key
        self._header_key = header_key

        return

    def add_to(self, headers: Mapping) -> Mapping:
        headers[self._header_key] = self._key
        return headers

    def matches_headers(self, headers: Headers) -> bool:
        """
        Return true if the supplied headers authenticate a request as
        coming from an internal application.
        """
        credential = headers.value_for(self._header_key)
        if credential is None:
            return False
        return self.matches(credential)

    def matches(self, credential: str) -> bool:
        """
        Return true if the supplied credential authenticates a request
        as coming from an internal application.
        """
        return hmac.compare_digest(credential, self._key)
