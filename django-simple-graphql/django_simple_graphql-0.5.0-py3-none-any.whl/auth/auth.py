# Based on implementation from Django Rest Framework and as such might be
# subject to the license associated with Django Rest Framework.
# See https://github.com/encode/django-rest-framework/blob/master/LICENSE.md
from typing import Any, Optional, Protocol, Tuple, Type

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from simple_graphql.auth.exceptions import AuthenticationException

AUTH_HEADER = "HTTP_AUTHORIZATION"


def get_authorization_header(request: HttpRequest) -> bytes:
    auth = request.META.get(AUTH_HEADER, b"")
    # Ensure Django test client is uniform with RFC5987
    if isinstance(auth, str):
        auth = auth.encode("iso-8859-1")
    return auth


class AuthenticationProvider(Protocol):
    @classmethod
    def authenticate(cls, key: str) -> Optional[Tuple[Any, Any]]:
        ...


class TokenAuthentication:
    keyword: str = "Token"
    model_cls: Optional[Type[AuthenticationProvider]] = None

    def get_model_cls(self) -> Type[AuthenticationProvider]:
        if self.model_cls is not None:
            return self.model_cls
        from simple_graphql.auth.models import AuthenticationSession

        return AuthenticationSession

    def authenticate(self, request: HttpRequest) -> Optional[Tuple[Any, Any]]:
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise AuthenticationException(msg)
        elif len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise AuthenticationException(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _(
                "Invalid token header. "
                "Token string should not contain invalid characters."
            )
            raise AuthenticationException(msg)

        model_cls = self.get_model_cls()
        return model_cls.authenticate(token)
