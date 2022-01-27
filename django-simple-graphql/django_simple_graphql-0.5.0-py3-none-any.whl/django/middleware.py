from typing import Any

from django.conf import settings
from graphql import GraphQLError


class IntrospectionDisallowedError(GraphQLError):
    pass


class DisableIntrospectionMiddleware:
    def resolve(self, next: Any, root: Any, info: Any, **kwargs) -> Any:
        # TODO: Remove from here and come up with a better setup for changing
        #       middleware during test run.
        if getattr(settings, "TEST_DISABLE_INTROSPECTION_BLOCK", None) is not True:
            self.check_introspection(info)
        return next(root, info, **kwargs)

    def check_introspection(self, info: Any):
        field_name = info.field_name
        allowed_introspection = {
            "__typename",
        }
        is_disallowed = (
            field_name.startswith("__") and field_name not in allowed_introspection
        )
        if is_disallowed:
            raise IntrospectionDisallowedError("Introspection is not allowed")
