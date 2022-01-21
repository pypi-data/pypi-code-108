from django_rest_client import (
    APIResource,
    ListableAPIResourceMixin,
    DeletableAPIResourceMixin,
)


class Session(
    APIResource,
    ListableAPIResourceMixin,
    DeletableAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.Session`
    """

    OBJECT_NAME = "api.auth.sessions"
    EXPANDABLE_FIELDS = {
        "retrieve": [],
        "list": [],
    }
    ORDERING_FIELDS = []
