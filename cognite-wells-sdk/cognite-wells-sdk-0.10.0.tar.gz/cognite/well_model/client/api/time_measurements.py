import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import TimeMeasurementList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    TimeMeasurement,
    TimeMeasurementFilter,
    TimeMeasurementFilterRequest,
    TimeMeasurementItems,
)

logger = logging.getLogger(__name__)


class TimeMeasurementsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, measurements: List[TimeMeasurement]) -> TimeMeasurementList:
        """Ingests time measurements

        Args:
            measurements (List[TimeMeasurement]):
        Returns:
            TimeMeasurementList: List of ingested measurements
        """
        path = self._get_path("/measurements/time")
        json = TimeMeasurementItems(items=measurements).json()
        response: Response = self.client.post(path, json)
        return TimeMeasurementList(TimeMeasurementItems.parse_raw(response.text).items)

    def list(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        measurement_types: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> TimeMeasurementList:
        """List time measurements

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional)
            wellbore_matching_ids (Optional[List[str]], optional)
            measurement_types (Optional[List[str]], optional)
            limit (Optional[int], optional)

        Returns:
            TimeMeasurementList:
        """

        def request(cursor, limit):
            identifiers = identifier_list(wellbore_asset_external_ids, wellbore_matching_ids)
            path = self._get_path("/measurements/time/list")
            json = TimeMeasurementFilterRequest(
                filter=TimeMeasurementFilter(
                    wellbore_ids=identifiers,
                    measurement_types=measurement_types,
                ),
                limit=limit,
                cursor=cursor,
            ).json()
            response: Response = self.client.post(path, json)
            measurement_items = TimeMeasurementItems.parse_raw(response.text)
            return measurement_items

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.items,
            limit=limit,
            request=request,
        )
        return TimeMeasurementList(items)
