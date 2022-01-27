import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.api.merge_rules.wellbores import WellboreMergeRulesAPI
from cognite.well_model.client.models.resource_list import WellboreList
from cognite.well_model.client.models.wellbore_merge_details import WellboreMergeDetailList, WellboreMergeDetailResource
from cognite.well_model.client.utils._auxiliary import extend_class
from cognite.well_model.client.utils._identifier_list import identifier_items, identifier_items_single
from cognite.well_model.models import (
    IdentifierItems,
    Wellbore,
    WellboreIngestion,
    WellboreIngestionItems,
    WellboreItems,
    WellboreMergeDetailItems,
)

logger = logging.getLogger(__name__)


class WellboresAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)
        self.merge_rules = WellboreMergeRulesAPI(client)

        @extend_class(Wellbore)
        def merge_details(this: Wellbore) -> WellboreMergeDetailResource:
            return self.merge_details(matching_id=this.matching_id)

    def ingest(self, ingestions: List[WellboreIngestion]) -> WellboreList:
        """Ingest wellbores

        Args:
            ingestions (List[WellboreIngestion]):

        Returns:
            WellboreList:
        """
        path = self._get_path("/wellbores")
        json = WellboreIngestionItems(items=ingestions).json()
        response: Response = self.client.post(path, json)
        wellbore_items: WellboreItems = WellboreItems.parse_obj(response.json())
        wellbores: List[Wellbore] = wellbore_items.items
        return WellboreList(wellbores)

    # guranteed to be non-empty list
    def _retrieve_multiple(self, identifiers: IdentifierItems) -> List[Wellbore]:
        path: str = self._get_path("/wellbores/byids")
        response: Response = self.client.post(url_path=path, json=identifiers.json())
        wellbore_items: WellboreItems = WellboreItems.parse_raw(response.text)
        wellbores: List[Wellbore] = wellbore_items.items
        return wellbores

    def retrieve(self, asset_external_id: Optional[str] = None, matching_id: Optional[str] = None) -> Wellbore:
        """Get wellbore by asset external id or matching id.

        Args:
            asset_external_id (Optional[str], optional)
            matching_id (Optional[str], optional)

        Returns:
            Wellbore:
        """
        identifiers = identifier_items_single(asset_external_id, matching_id)
        return self._retrieve_multiple(identifiers)[0]

    def retrieve_multiple(
        self, asset_external_ids: Optional[List[str]] = None, matching_ids: Optional[List[str]] = None
    ) -> WellboreList:
        """Get wellbores by a list assets external ids and matching ids

        Args:
            asset_external_ids (Optional[List[str]]): list of wellbore asset external ids
            matching_ids (Optional[List[str]]): List of wellbore matching ids
        Returns:
            WellboreList:
        """
        identifiers = identifier_items(asset_external_ids, matching_ids)
        return WellboreList(self._retrieve_multiple(identifiers))

    def merge_details(
        self,
        asset_external_id: Optional[str] = None,
        matching_id: Optional[str] = None,
    ) -> Optional[WellboreMergeDetailResource]:
        """Retrieve merge details for a wellbore

        Args:
            asset_external_id (str, optional)
            matching_id (str, optional)
        Returns:
            Optional[WellboreMergeDetailResource]: merge details if the wellbore exists.

        Examples:
            Get merge details for a single wellbore
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> details = wm.wellbores.merge_details(matching_id="11/5-F-5")

            Get merge details for a Wellbore object
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> details = wm.wellbores.retrieve(matching_id="11/5-F-5").merge_details()
        """
        identifiers = identifier_items_single(
            asset_external_id=asset_external_id,
            matching_id=matching_id,
        )
        identifiers.ignore_unknown_ids = True

        path = self._get_path("/wellbores/mergedetails")
        response = self.client.post(path, json=identifiers.json())

        items = WellboreMergeDetailItems.parse_raw(response.content)
        if len(items.items) == 0:
            return None
        assert len(items.items) == 1
        return WellboreMergeDetailResource(items.items[0])

    def merge_details_multiple(
        self,
        asset_external_ids: Optional[List[str]] = None,
        matching_ids: Optional[List[str]] = None,
        ignore_unknown_ids: Optional[bool] = False,
    ) -> WellboreMergeDetailList:
        """Retrieve merge details for multiple wellbores

        Args:
            asset_external_ids: list of wellbore asset external ids.
            matching_ids: List of wellbore matching ids.
            ignore_unknown_ids (Optional[bool]): If set to True,
                it will ignore unknown wells.

        Returns:
            WellboreMergeDetailList: List-like object of merge details

        Examples:
            Get merge details for a single well
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> details = wm.wellbores.merge_details_multiple(matching_ids=["11/5-F-5"])
        """
        identifiers = identifier_items(asset_external_ids, matching_ids)
        identifiers.ignore_unknown_ids = ignore_unknown_ids

        path = self._get_path("/wellbores/mergedetails")
        response = self.client.post(path, json=identifiers.json())

        items = WellboreMergeDetailItems.parse_raw(response.content)
        return WellboreMergeDetailList([WellboreMergeDetailResource(x) for x in items.items])
