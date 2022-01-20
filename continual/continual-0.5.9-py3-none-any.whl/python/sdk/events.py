from __future__ import annotations
from typing import List, Optional

from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager


class EventManager(Manager):
    """Manages event resources."""

    # name_pattern: str = "projects/{project}/models/{model}"

    def get(self, id: str) -> Event:
        """Get Event.

        Arguments:
            id: Event id.

        Returns
            An Event.
        """
        req = management_pb2.GetEventRequest(name=self.name(id))
        resp = self.client._management.GetEvent(req)
        return Event.from_proto(resp, client=self.client)

    def list(
        self,
        filters: List[str] = None,
        page_size: Optional[int] = None,
        parent: str = None,
        all_projects=False,
    ) -> List[Event]:
        """List Events.

        Arguments:
            filter: List of filters to apply to events. Can be:
                - event type (i.e. event:featureSet:CREATED)
                - severity (i.e. severity:CRITICAL)
                - subject (i.e. subject:userAccount/<id>)

            page_size: Number of items to return.

            parent: Parent resource to filter events by

        Returns:
            A list of events.
        """
        if parent is None:
            parent = self.parent
        req = management_pb2.ListEventsRequest(
            parent=parent,
            filters=filters,
            page_size=page_size,
            all_projects=all_projects,
        )
        resp = self.client._management.ListEvents(req)
        return [Event.from_proto(x, client=self.client) for x in resp.events]

    def list_all(self, filters: Optional[list(str)] = None) -> Pager[Event]:
        """List all Events

        Pages through all events using an iterator.

        Returns:
            A iterator of all events.
        """

        def next_page(
            next_page_token,
        ):
            req = management_pb2.ListEventsRequest(
                parent=self.parent, filters=filters, page_token=next_page_token
            )
            resp = self.client._management.ListEvents(req)
            return (
                [Event.from_proto(x, client=self.client) for x in resp.events],
                resp.next_page_token,
            )

        return Pager(next_page)


class Event(Resource, types.Event):
    """Model resource."""

    # name_pattern: str = "projects/{project}/models/{model}"
    manager: EventManager

    def _init(self):
        self.manager = EventManager(parent=self.parent, client=self.client)

    def make_name(self):
        return "%s/events/%s" % (self.parent, self.id)
