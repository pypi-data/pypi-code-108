"""
Endpoint implementation for the rest client.
"""
import typing as t

from pyarrow.flight import ActionType, FlightClient, Ticket  # type: ignore
from pydantic import BaseModel

from taktile_client.arrow.serialize import deserialize
from taktile_client.arrow.utils import batch_arrow


class EndpointActionGroup(BaseModel):
    """
    Actiongroup of an Arrow endpoint.

    Collects the endpoint and sample data actions into a single type
    """

    endpoint: ActionType
    X: ActionType
    y: ActionType


class ClientArrowEndpoint:
    """
    The actual endpoint object.

    This is an Arrow endpoint, exposing function calling through
    `__call__`. This is the object that is `client.endpoints.repayment`.

    Parameters
    ----------
    client : FlightCLient
        the client to use for making the calls
    action_group : EndpointActionGroup
        the endpoint action_group for this endpoint
    """

    def __init__(
        self, *, client: FlightClient, action_group: EndpointActionGroup
    ):
        self._client = client
        self._action_group = action_group
        self.__name__ = action_group.endpoint.type

    def __call__(self, payload: t.Any, nrows: t.Optional[int] = None) -> t.Any:
        """
        Call the endpoint

        Parameters
        ----------
        payload : t.Any
            payload to send

        nrows : t.Optional[int]
            number of rows to send per batch
        Returns
        -------
        t.Any
            The response of the endpoint
        """
        return batch_arrow(
            client=self._client,
            action=self._action_group.endpoint,
            payload=payload,
            nrows=nrows,
        )

    def X(self) -> t.Any:  # pylint: disable=invalid-name
        """
        Sample input data of endpoint

        Returns
        -------
        t.Any
            sample data
        """
        reader = self._client.do_get(Ticket(ticket=self._action_group.X.type))
        return deserialize(reader.read_all())

    def y(self) -> t.Any:  # pylint: disable=invalid-name
        """
        Sample output data of endpoint

        Returns
        -------
        t.Any
            sample data
        """
        reader = self._client.do_get(Ticket(ticket=self._action_group.y.type))
        return deserialize(reader.read_all())


class ArrowEndpoints:  # pylint: disable=too-few-public-methods
    """
    A collection object for Arrow endpoints.

    This is the `endpoints` object on Taktile Arrow Clients.

    Parameters
    ----------
    client : FlightClient
        the client to use for calls
    actions : t.List[ActionType]
        ungrouped actions of model
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
                        X=[
                            a for a in actions if a.type == action.type + "__X"
                        ][0],
                        y=[
                            a for a in actions if a.type == action.type + "__y"
                        ][0],
                    )
                )

        for group in action_groups:
            setattr(
                self,
                group.endpoint.type,
                ClientArrowEndpoint(
                    client=client,
                    action_group=group,
                ),
            )
