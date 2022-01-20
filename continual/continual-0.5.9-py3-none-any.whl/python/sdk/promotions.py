from __future__ import annotations
from typing import List, Optional
from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from continual.python.sdk.waiter import wait
from continual.python.sdk.events import EventManager


class PromotionManager(Manager):
    """Manages promotion resources."""

    name_pattern: str = "projects/{project}/models/{model}/promotions/{promotion}"

    def get(self, id: str) -> Promotion:
        """Get promotion.

        Arguments:
            id: Promotion name or id.

        Returns
            A promotion.
        """
        req = management_pb2.GetPromotionRequest(name=self.name(id))
        resp = self.client._management.GetPromotion(req)
        return Promotion.from_proto(resp, client=self.client)

    def list(
        self,
        page_size: Optional[int] = None,
        filters: List[str] = None,
        all_projects: bool = False,
    ) -> List[Promotion]:
        """List promotions.

        Arguments:
            page_size: Number of items to return.

        Returns:
            A list of promotions.
        """
        req = management_pb2.ListPromotionsRequest(
            parent=self.parent,
            page_size=page_size,
            filters=filters,
            all_projects=all_projects,
        )
        resp = self.client._management.ListPromotions(req)
        return [Promotion.from_proto(x, client=self.client) for x in resp.promotions]

    def list_all(self) -> Pager[Promotion]:
        """List all promotions.

        Pages through all promotions using an iterator.

        Returns:
            A iterator of all promotions.
        """

        def next_page(next_page_token):
            req = management_pb2.ListPromotionsRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListPromotions(req)
            return (
                [Promotion.from_proto(x, client=self.client) for x in resp.promotions],
                resp.next_page_token,
            )

        return Pager(next_page)


class Promotion(Resource, types.Promotion):
    """Promotion resource."""

    name_pattern: str = "projects/{project}/models/{model}/promotions/{promotion}"
    manager: PromotionManager

    events: EventManager
    """Event manager."""

    def _init(self):
        self.manager = PromotionManager(parent=self.parent, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def wait(
        self,
        echo: bool = False,
        timeout: Optional[int] = None,
    ) -> Promotion:
        """Wait for promotion state transition to complete.

        Arguments:
            echo: Display progress.
            timeout: Timeout in second.

        Returns:
            An updated model version.
        """
        return wait(lambda: self.manager.get(self.id), echo=echo, timeout=timeout)
