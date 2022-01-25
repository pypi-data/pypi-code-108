import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.depth_measurement_rows import DepthMeasurementRows
from cognite.well_model.client.models.resource_list import DepthMeasurementList
from cognite.well_model.client.utils._auxiliary import extend_class
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DepthMeasurement,
    DepthMeasurementData,
    DepthMeasurementDataRequest,
    DepthMeasurementFilter,
    DepthMeasurementFilterRequest,
    DepthMeasurementIngestion,
    DepthMeasurementIngestionItems,
    DepthMeasurementItems,
    DistanceRange,
    DistanceUnit,
    SequenceExternalId,
    SequenceExternalIdItems,
)

logger = logging.getLogger(__name__)


class DepthMeasurementsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

        @extend_class(DepthMeasurement)
        def data(this: DepthMeasurement, measured_depth: Optional[DistanceRange] = None, limit: int = DEFAULT_LIMIT):
            return self.list_data(
                sequence_external_id=this.source.sequence_external_id,
                measured_depth=measured_depth,
                measurement_types=[x.measurement_type for x in this.columns],
                limit=limit,
            )

    def ingest(self, measurements: List[DepthMeasurementIngestion]) -> DepthMeasurementList:
        """Ingest depth measurements

        Args:
            measurements (List[DepthMeasurementIngestion]):

        Returns:
            DepthMeasurementList:
        """
        path = self._get_path("/measurements/depth")
        json = DepthMeasurementIngestionItems(items=measurements).json()
        response: Response = self.client.post(path, json)
        return DepthMeasurementList(DepthMeasurementItems.parse_raw(response.text).items)

    def retrieve(self, sequence_external_id: str) -> Optional[DepthMeasurement]:
        """Retrieve a single depth measurement by sequence external id

        Args:
            sequence_external_id (str): Sequence external id

        Returns:
            Optional[DepthMeasurement]: DepthMeasurement if found, else None.

        Examples:
            Retrieve a depth measurement
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> measurement = wm.depth_measurements.retrieve("VOLVE:seq1")
        """
        path = self._get_path("/measurements/depth/byids")
        json = SequenceExternalIdItems(
            items=[SequenceExternalId(sequence_external_id=sequence_external_id)], ignore_unknown_ids=True
        ).json()
        response: Response = self.client.post(path, json)
        items: List[DepthMeasurement] = DepthMeasurementItems.parse_raw(response.text).items
        return items[0] if items else None

    def retrieve_multiple(self, sequence_external_ids: List[str], ignore_unknown_ids=False) -> DepthMeasurementList:
        """Retrieve multiple depth measurements by sequence external ids.

        Args:
            sequence_external_ids (List[str]): List of sequence external ids.
            ignore_unknown_ids (bool, optional): Ignore unknown ids. Defaults to False.

        Returns:
            DepthMeasurementList: List of matching depth measurements

        Examples:
            Retrieve two depth measurements
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> measurements = wm.depth_measurements.retrieve_multiple([
                ...    "VOLVE:seq1",
                ...    "VOLVE:seq2"
                ... ])
                >>> len(measurements)
                2
        """
        path = self._get_path("/measurements/depth/byids")
        json = SequenceExternalIdItems(
            items=[SequenceExternalId(sequence_external_id=x) for x in sequence_external_ids],
            ignore_unknown_ids=ignore_unknown_ids,
        ).json()
        response: Response = self.client.post(path, json)
        return DepthMeasurementList(DepthMeasurementItems.parse_raw(response.text).items)

    def list(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        measurement_types: Optional[List[str]] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> DepthMeasurementList:
        """List depth measurements

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional):
            wellbore_matching_ids (Optional[List[str]], optional):
            measurement_types (Optional[List[str]], optional): Only get measurements with *any* of these measurement
                types.
            limit (Optional[int], optional):

        Returns:
            DepthMeasurementList:
        """

        def request(cursor, limit):
            identifiers = identifier_list(wellbore_asset_external_ids, wellbore_matching_ids)
            path = self._get_path("/measurements/depth/list")
            json = DepthMeasurementFilterRequest(
                filter=DepthMeasurementFilter(
                    wellbore_ids=identifiers,
                    measurement_types=measurement_types,
                ),
                limit=limit,
                cursor=cursor,
            ).json()
            response: Response = self.client.post(path, json)
            measurement_items = DepthMeasurementItems.parse_raw(response.text)
            return measurement_items

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.items,
            limit=limit,
            request=request,
        )
        return DepthMeasurementList(items)

    def list_data(
        self,
        sequence_external_id: str,
        measured_depth: Optional[DistanceRange] = None,
        depth_unit: Optional[DistanceUnit] = None,
        measurement_types: Optional[List[str]] = None,
        top_surface_name: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
    ) -> DepthMeasurementRows:
        """Get depth measurement data

        Args:
            sequence_external_id (str): Sequence external id
            measured_depth (Optional[DistanceRange], optional): MD range
            depth_unit (Optional[DistanceUnit], optional): Unit and focator for MD measurement
            measurement_types (Optional[List[str]], optional): This decides which columns you will download.
            top_surface_name (Optional[str], optional): If set, only get the rows inside the range defined by the top
                surface.
            limit (int, optional): Max number of rows to get. Defaults to DEFAULT_LIMIT.

        Returns:
            DepthMeasurementRows: Depth measurement with data. An iterator over rows.

        Examples:
            Get depth measurement data
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> data = wm.depth_measurements.list_data(
                ...     sequence_external_id="VOLVE:seq1"
                ... )
                >>> df = data.to_pandas()

            Get depth measurement data using ``.data()``
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> depth_measurement = wm.depth_measurements.list()[0]
                >>> data = depth_measurement.data()
                >>> df = data.to_pandas()

            Get depth measurement data in MD range
                Only get the rows between 150.0 and 500.0 meters MD

                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> depth_measurement = wm.depth_measurements.list()[0]
                >>> data = depth_measurement.data(
                ...     measured_depth={
                ...         "min": 150.0,
                ...         "max": 500.0,
                ...         "unit": "meter",
                ...     }
                ... )

            Get only gamma ray measurements
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> data = wm.depth_measurements.list_data(
                ...     sequence_external_id="VOLVE:seq1",
                ...     measurement_types=["gamma ray"],
                ... )
                >>> df = data.to_pandas()

            Filter and list only gamma ray measurements
                If you have a ``measurement_types`` filter when listing
                depth measurements, then you will only see these
                measurement_types when you use the ``.data()`` function.

                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> depth_measurements = wm.depth_measurements.list(
                ...     measurement_types=["gamma ray"]
                ... )
                >>> for dm in depth_measurements:
                ...     # Will only retrieve the "gamma ray" columns.
                ...     data = dm.data()

        """

        class LastResponse:
            # Using a class with a static variable due to python scoping rules.
            value: DepthMeasurementData = None

        def request(cursor, limit):
            path = self._get_path("/measurements/depth/data")
            json = DepthMeasurementDataRequest(
                sequence_external_id=sequence_external_id,
                measured_depth=measured_depth,
                depth_unit=depth_unit,
                measurement_types=measurement_types,
                top_surface_name=top_surface_name,
                limit=limit,
                cursor=cursor,
            ).json()
            response: Response = self.client.post(path, json)
            data = DepthMeasurementData.parse_raw(response.text)
            LastResponse.value = data
            return data

        all_rows = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.rows,
            limit=limit,
            request=request,
        )
        LastResponse.value.rows = all_rows
        return DepthMeasurementRows.from_measurement_data(LastResponse.value)
