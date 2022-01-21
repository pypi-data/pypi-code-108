from django_rest_client import (
    APIResource,
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
)


class Action(
    APIResource,
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.Action`
    """

    OBJECT_NAME = "api.action"
    EXPANDABLE_FIELDS = {
        "retrieve": ["user"],
        "list": ["user"],
    }
    ORDERING_FIELDS = []
