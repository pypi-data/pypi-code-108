from django_rest_client import (
    APIResource,
    SingletonAPIResourceMixin,
)


class UserAccessInfo(
    APIResource,
    SingletonAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.UserAccessInfo`
    """

    OBJECT_NAME = "api.me.access"
    EXPANDABLE_FIELDS = {
        "retrieve": [],
        "list": [],
    }
    ORDERING_FIELDS = []
