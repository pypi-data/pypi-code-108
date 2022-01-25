import re
from abc import abstractmethod
from typing import Dict, Optional
from functools import cached_property

from origin.tokens import TokenEncoder
from origin.models.auth import InternalToken
from origin.auth import TOKEN_HEADER_NAME, TOKEN_COOKIE_NAME

from .responses import Unauthorized


class Context(object):
    """
    Context for a single incoming HTTP request.

    An instance is create for each HTTP request, and dies when the request
    if out of scope again.
    """

    # Regex pattern for matching bearer token (in HTTP header)
    TOKEN_PATTERN = re.compile(r'^Bearer:\s*(.+)$', re.IGNORECASE)

    def __init__(self, token_encoder: TokenEncoder[InternalToken]):
        """
        :param token_encoder: Internal token encoder
        """
        self.token_encoder = token_encoder

    @property
    @abstractmethod
    def headers(self) -> Dict[str, str]:
        """
        :returns: HTTP request headers
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def cookies(self) -> Dict[str, str]:
        """
        :returns: HTTP request cookies
        """
        raise NotImplementedError

    # -- Tokens --------------------------------------------------------------

    @property
    def opaque_token(self) -> Optional[str]:
        """
        Returns value for the opaque token provided by the client in a cookie.

        :returns: Opaque token or None
        """
        return self.cookies.get(TOKEN_COOKIE_NAME)

    @property
    def internal_token_encoded(self) -> Optional[str]:
        """
        Returns value for the raw, encoded internal token. The opaque token
        (provided by the client in a cookie) is translated to an internal
        token by the API gateway and passed on as a header.

        :returns: Raw, encoded internal token
        """
        if TOKEN_HEADER_NAME in self.headers:
            matches = self.TOKEN_PATTERN \
                .findall(self.headers[TOKEN_HEADER_NAME])

            if matches:
                return matches[0]

    @cached_property
    def token(self) -> Optional[InternalToken]:
        """
        Parses token into an OpaqueToken.
        """
        if self.internal_token_encoded is None:
            return None

        try:
            internal_token = self.token_encoder.decode(
                self.internal_token_encoded)
        except self.token_encoder.DecodeError:
            # TODO Raise exception if in debug mode?
            return None

        if not internal_token.is_valid:
            # TODO Raise exception if in debug mode?
            return None

        return internal_token

    @property
    def is_authorized(self) -> bool:
        """
        Check whether or not the client provided a valid token.
        """
        return self.token is not None

    def has_scope(self, scope: str) -> bool:
        """
        TODO
        """
        if self.token:
            return scope in self.token.scope
        return False

    def get_token(self, required=True) -> Optional[InternalToken]:
        """
        TODO
        """
        if self.token:
            return self.token
        elif required:
            raise Unauthorized('')  # TODO Error message

    def get_subject(self, required=True) -> Optional[str]:
        """
        TODO
        """
        if self.token:
            return self.token.subject
        elif required:
            raise Unauthorized('')  # TODO Error message
