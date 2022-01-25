import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.property_filter import PropertyFilter, filter_to_model
from cognite.well_model.client.models.resource_list import NptList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DistanceRange,
    DurationRange,
    Npt,
    NptFilter,
    NptFilterRequest,
    NptIngestion,
    NptIngestionItems,
    NptItems,
)

logger = logging.getLogger(__name__)


class NptEventsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, npt_events: List[NptIngestion]) -> NptList:
        """Ingest NPT events

        Args:
            npt_events (List[NptIngestion])

        Returns:
            NptList: Ingested NPT events
        """
        path = self._get_path("/npt")
        json = NptIngestionItems(items=npt_events).json()
        response: Response = self.client.post(path, json)
        return NptList(NptItems.parse_raw(response.text).items)

    def list(
        self,
        md: Optional[DistanceRange] = None,
        duration: Optional[DurationRange] = None,
        npt_codes: PropertyFilter = None,
        npt_code_details: PropertyFilter = None,
        root_causes: PropertyFilter = None,
        locations: PropertyFilter = None,
        subtypes: PropertyFilter = None,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> NptList:
        """Get NPT events matching the arguments

        Args:
            md (Optional[DistanceRange], optional)
            duration (Optional[DurationRange], optional)
            npt_codes (PropertyFilter, optional): [description]. Defaults to None.
            npt_code_details (PropertyFilter, optional): [description]. Defaults to None.
            root_causes (PropertyFilter, optional): [description]. Defaults to None.
            locations (PropertyFilter, optional): [description]. Defaults to None.
            subtypes (PropertyFilter, optional): [description]. Defaults to None.
            wellbore_asset_external_ids (Optional[List[str]], optional): [description]. Defaults to None.
            wellbore_matching_ids (Optional[List[str]], optional): [description]. Defaults to None.
            limit (Optional[int], optional): [description]. Defaults to DEFAULT_LIMIT.

        Returns:
            NptList: [description]

        Examples:
            Get NPT events with ``npt_code`` set to None.
                >>> from cognite.well_model import CogniteWellsClient, NotSet
                >>> wm = CogniteWellsClient()
                >>> npt_events = wm.npt.list(npt_codes=NotSet)

            Get NPT events with ``npt_codes`` and ``wellbores``
                >>> from cognite.well_model import CogniteWellsClient, NotSet
                >>> wm = CogniteWellsClient()
                >>> npt_events = wm.npt.list(
                ...     npt_codes=["ABCD", "DEFG"],
                ...     wellbore_asset_external_ids=["VOLVE:15/9-1 A"]
                ... )
        """

        def request(cursor, limit):
            npt_filter = NptFilterRequest(
                filter=NptFilter(
                    measured_depth=md,
                    duration=duration,
                    npt_code=filter_to_model(npt_codes),
                    npt_code_detail=filter_to_model(npt_code_details),
                    root_cause=filter_to_model(root_causes),
                    location=filter_to_model(locations),
                    subtype=filter_to_model(subtypes),
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                ),
                cursor=cursor,
                limit=limit,
            )

            path: str = self._get_path("/npt/list")
            response: Response = self.client.post(url_path=path, json=npt_filter.json())
            npt_items: NptItems = NptItems.parse_raw(response.text)
            return npt_items

        items = cursor_multi_request(
            get_cursor=self._get_cursor, get_items=self._get_items, limit=limit, request=request
        )
        return NptList(items)

    @staticmethod
    def _get_items(npt_items: NptItems) -> List[Npt]:
        items: List[Npt] = npt_items.items  # For mypy
        return items

    @staticmethod
    def _get_cursor(npt_items: NptItems) -> Optional[str]:
        next_cursor: Optional[str] = npt_items.next_cursor  # For mypy
        return next_cursor
