import typing as t

from pyarrow.flight import ActionType, FlightClient, Ticket  # type: ignore
from pydantic import BaseModel

from tktl.core.serializers import deserialize_arrow

from .utils import batch_arrow


class EndpointActionGroup(BaseModel):
    endpoint: ActionType
    X: ActionType
    y: ActionType


class SDKArrowEndpoint:
    """SDKArrowEndpoint.

    This is a SDK Arrow endpoint, exposing function calling through
    `__call__` and sample data through `X` and `y`.
    """

    def __init__(self, *, client: FlightClient, action_group: EndpointActionGroup):
        self._client = client
        self._action_group = action_group
        self.__name__ = action_group.endpoint.type

    def __call__(self, X: t.Any) -> t.Any:
        return batch_arrow(client=self._client, action=self._action_group.endpoint, X=X)

    def X(self) -> t.Any:
        reader = self._client.do_get(Ticket(ticket=self._action_group.X.type))
        return deserialize_arrow(reader.read_all())

    def y(self) -> t.Any:
        reader = self._client.do_get(Ticket(ticket=self._action_group.y.type))
        return deserialize_arrow(reader.read_all())


class ArrowEndpoints:
    """ArrowEndpoints.

    This is the `endpoints` object on TaktileSDK Arrow Clients.
    """

    def __init__(self, *, client: FlightClient, actions: t.List[ActionType]):

        action_types = [a.type for a in actions]
        action_groups = []

        for action in actions:

            if (
                action.type + "__X" in action_types
                and action.type + "__y" in action_types
            ):
                action_groups.append(
                    EndpointActionGroup(
                        endpoint=action,
                        X=[a for a in actions if a.type == action.type + "__X"][0],
                        y=[a for a in actions if a.type == action.type + "__y"][0],
                    )
                )

        for group in action_groups:
            setattr(
                self,
                group.endpoint.type,
                SDKArrowEndpoint(client=client, action_group=group),
            )
