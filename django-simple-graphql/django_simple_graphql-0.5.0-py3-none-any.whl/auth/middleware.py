from typing import Any

from django.contrib.auth.models import AnonymousUser

from simple_graphql.auth.auth import AUTH_HEADER, TokenAuthentication

AUTH = TokenAuthentication()


class AuthMiddleware:
    # TODO: Replace Any types with better types
    def resolve(self, next: Any, root: Any, info: Any, **kwargs) -> Any:
        self.authenticate(info)
        return next(root, info, **kwargs)

    def authenticate(self, info: Any) -> None:
        graphql_authenticated = getattr(info.context, "graphql_authenticated", False)
        if not hasattr(info.context, "user") or (
            info.context.user and not graphql_authenticated
        ):
            info.context.user = AnonymousUser()
        if info.context.META.get(AUTH_HEADER) and not graphql_authenticated:
            auth_result = AUTH.authenticate(info.context)
            if auth_result:
                info.context.user = auth_result[0]
                info.context.graphql_authenticated = True
