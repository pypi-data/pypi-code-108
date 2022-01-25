from __future__ import annotations
from typing import List, Optional, Iterator
from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from continual.python.sdk.waiter import wait
from continual.python.sdk.events import EventManager


class IngestionManager(Manager):
    """Manages ingestions resources."""

    name_pattern: str = (
        "projects/{project}/featureSets/{feature_set}/ingestions/{ingestions}"
    )

    def get(self, id: str) -> Ingestion:
        """Get ingestion.

        Arguments:
            id: Ingestion name or id.

        Returns
            A ingestion.
        """
        req = management_pb2.GetIngestionRequest(name=self.name(id))
        resp = self.client._management.GetIngestion(req)
        return Ingestion.from_proto(resp, client=self.client)

    def list(
        self,
        page_size: Optional[int] = None,
        filters: List[str] = None,
        all_projects: bool = False,
    ) -> List[Ingestion]:
        """List ingestions.

        Arguments:
            page_size: Number of items to return.

        Returns:
            A list of ingestions.
        """
        req = management_pb2.ListIngestionsRequest(
            parent=self.parent,
            page_size=page_size,
            filters=filters,
            all_projects=all_projects,
        )
        resp = self.client._management.ListIngestions(req)
        return [Ingestion.from_proto(u, client=self.client) for u in resp.ingestions]

    def list_all(self) -> Iterator[Ingestion]:
        """List all ingestions.

        Pages through all ingestions using an iterator.

        Returns:
            A iterator of all ingestions.
        """

        def next_page(next_page_token):
            req = management_pb2.ListIngestionsRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListIngestions(req)
            return (
                [Ingestion.from_proto(u, client=self.client) for u in resp.ingestions],
                resp.next_page_token,
            )

        return Pager(next_page)

    def cancel(self, id: str) -> None:
        """Cancel an ingestion.

        Arugments:
            id: Name or id of ingestion

        """
        req = management_pb2.CancelIngestionRequest(name=self.name(id))
        self.client._management.CancelIngestion(req)


class Ingestion(Resource, types.Ingestion):
    """Ingestion resource."""

    name_pattern: str = (
        "projects/{project}/featureSets/{feature_set}/ingestions/{ingestions}"
    )
    manager: IngestionManager

    events: EventManager
    """Event manager."""

    def _init(self):
        self.manager = IngestionManager(parent=self.parent, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def cancel(self):
        """Cancel ingestion."""
        self.manager.cancel(self.id)

    def wait(self, echo: bool = True, timeout: int = None) -> Ingestion:
        """Wait for ingestion to complete.

        Arguments:
            echo: Display progress.
            timeout: Timeout in seconds.
        Returns:
            Updated ingestion.
        """
        return wait(
            getter=lambda: self.manager.get(self.id),
            echo=echo,
            timeout=timeout,
        )
