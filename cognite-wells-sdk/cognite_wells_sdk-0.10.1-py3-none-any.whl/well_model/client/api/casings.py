import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import CasingsList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    CasingFilter,
    CasingFilterRequest,
    CasingIngestionItems,
    CasingItems,
    CasingSchematicIngestion,
)

logger = logging.getLogger(__name__)


class CasingsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, casings: List[CasingSchematicIngestion]) -> CasingsList:
        """Ingest casings

        Args:
            casings (List[CasingSchematicIngestion]):

        Returns:
            CasingsList:
        """
        path = self._get_path("/casings")
        json = CasingIngestionItems(items=casings).json()
        response: Response = self.client.post(path, json)
        return CasingsList(CasingItems.parse_raw(response.text).items)

    def list(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> CasingsList:
        """List casings

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional):
            wellbore_matching_ids (Optional[List[str]], optional):
            limit (Optional[int], optional): Max number of casings.

        Returns:
            CasingsList:
        """

        def request(cursor, limit):
            identifiers = identifier_list(wellbore_asset_external_ids, wellbore_matching_ids)
            path = self._get_path("/casings/list")
            json = CasingFilterRequest(
                filter=CasingFilter(
                    wellbore_ids=identifiers,
                ),
                limit=limit,
                cursor=cursor,
            ).json()
            response: Response = self.client.post(path, json)
            casing_items = CasingItems.parse_raw(response.text)
            return casing_items

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.items,
            limit=limit,
            request=request,
        )
        return CasingsList(items)
