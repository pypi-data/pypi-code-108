from typing import List, Optional

from benchling_api_client.api.events import list_events
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import Event, EventsPaginatedList
from benchling_sdk.services.base_service import BaseService


class EventService(BaseService):
    """
    Events.

    The Events system allows external services to subscribe to events that are triggered in Benchling (e.g. plasmid
    registration, request submission, etc).

    See https://benchling.com/api/reference#/Events
    """

    @api_method
    def _events_page(
        self,
        created_atgte: Optional[str] = None,
        starting_after: Optional[str] = None,
        event_types: Optional[str] = None,
        poll: Optional[bool] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[EventsPaginatedList]:
        return list_events.sync_detailed(  # type: ignore
            client=self.client,
            starting_after=none_as_unset(starting_after),
            created_atgte=none_as_unset(created_atgte),
            event_types=none_as_unset(event_types),
            poll=none_as_unset(poll),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )

    def list(
        self,
        created_atgte: Optional[str] = None,
        starting_after: Optional[str] = None,
        event_types: Optional[str] = None,
        poll: Optional[bool] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[Event]:
        """
        List Events.

        See https://benchling.com/api/reference#/Events/listEvents
        """

        def api_call(next_token: NextToken) -> Response[EventsPaginatedList]:
            return self._events_page(
                starting_after=starting_after,
                created_atgte=created_atgte,
                event_types=event_types,
                poll=poll,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: EventsPaginatedList) -> Optional[List[Event]]:
            return body.events

        return PageIterator(api_call, results_extractor)
