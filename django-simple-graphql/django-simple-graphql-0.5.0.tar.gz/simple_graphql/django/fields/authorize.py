from typing import TYPE_CHECKING, Any

from simple_graphql.django.fields.exceptions import AuthorizationError

if TYPE_CHECKING:
    from simple_graphql.django import ModelSchemaConfig


def authorize_query(config: "ModelSchemaConfig", info: Any):
    if config.require_login is True:
        user = getattr(info.context, "user", None)
        if user is None or user.is_anonymous:
            raise AuthorizationError("Unauthorized")
