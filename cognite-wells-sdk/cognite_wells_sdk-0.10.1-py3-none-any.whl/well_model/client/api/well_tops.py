import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import WellTopsList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    WellTopIngestionItems,
    WellTopItems,
    WellTops,
    WellTopsFilter,
    WellTopsFilterRequest,
    WellTopsIngestion,
)

logger = logging.getLogger(__name__)


class WellTopsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, ingestions: List[WellTopsIngestion]) -> WellTopsList:
        """Ingest well tops

        Args:
            ingestions (List[WellTopsIngestion])

        Returns:
            WellTopsList:
        """
        path = self._get_path("/welltops")
        json = WellTopIngestionItems(items=ingestions).json()
        response: Response = self.client.post(path, json)
        welltop_items: WellTopItems = WellTopItems.parse_obj(response.json())
        welltops_list: List[WellTops] = welltop_items.items
        return WellTopsList(welltops_list)

    def list(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> WellTopsList:
        """List well tops

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional)
            wellbore_matching_ids (Optional[List[str]], optional)
            limit (Optional[int], optional)
        Returns:
            WellTopsList
        """

        def request(cursor, limit):
            identifiers = identifier_list(wellbore_asset_external_ids, wellbore_matching_ids)
            path = self._get_path("/welltops/list")
            json = WellTopsFilterRequest(
                filter=WellTopsFilter(
                    wellbore_ids=identifiers,
                )
                if identifiers is not None
                else None,
                limit=limit,
                cursor=cursor,
            ).json()
            response: Response = self.client.post(path, json)
            well_top_items = WellTopItems.parse_raw(response.text)
            return well_top_items

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.items,
            limit=limit,
            request=request,
        )
        return WellTopsList(items)
