import logging
from typing import List

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import SummaryList, WellPropertiesList
from cognite.well_model.models import (
    DistanceRange,
    DoglegSeverityRange,
    DurationRange,
    MeasurementType,
    MeasurementTypeItems,
    SummaryCount,
    SummaryItems,
    WellPropertiesEnum,
    WellPropertiesSummaryItems,
    WellPropertiesSummaryRequest,
)

logger = logging.getLogger(__name__)


class SummariesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def welltypes(self) -> SummaryList:
        """Get all well types

        Returns:
            SummaryList: list of well types
        """
        output: SummaryList = self._summary("welltypes")
        return output

    def datum(self) -> DistanceRange:
        """Get a range og minimum and maximum datum

        Returns:
            DistanceRange: A range value for minimum and maximum datum
        """
        path: str = self._get_path("/summaries/datum")
        response: Response = self.client.get(url_path=path)
        return DistanceRange.parse_raw(response.text)

    def measurement_types(self) -> List[MeasurementType]:
        """Get all active measurement types

        Returns:
            List[MeasurementType]: A list of measurement types that are in use
        """
        path: str = self._get_path("/summaries/measurementtypes")
        response: Response = self.client.get(url_path=path)
        items: List[MeasurementType] = MeasurementTypeItems.parse_raw(response.text).items
        return items

    def npt_codes(self) -> SummaryList:
        """Get all Npt codes

        Returns:
            SummaryList: list of Npt codes
        """
        # For some reason I need to be explicit about types here.
        output: SummaryList = self._summary("npt/codes")
        return output

    def npt_detail_codes(self) -> SummaryList:
        """Get all Npt detail codes

        Returns:
            SummaryList: list of Npt detail codes
        """
        output: SummaryList = self._summary("npt/detailcodes")
        return output

    def npt_durations(self) -> DurationRange:
        """Get the minimum and maximum NPT duration

        Returns:
            DurationRange: describing min and max duration
        """
        path: str = self._get_path("/summaries/npt/durations")
        response: Response = self.client.get(url_path=path)
        return DurationRange.parse_raw(response.text)

    def nds_risk_types(self) -> SummaryList:
        """Get all Nds risk types

        Returns:
            SummaryList: list of Nds risk types
        """
        output: SummaryList = self._summary("nds/risktypes")
        return output

    def trajectories_measured_depth(self) -> DistanceRange:
        """Get a range of minimum and maximum measured depth on trajectories

        Returns:
            DistanceRange: a range representing minimum and maximum measured depth
        """
        path: str = self._get_path("/summaries/trajectories/measureddepth")
        response: Response = self.client.get(url_path=path)
        return DistanceRange.parse_raw(response.text)

    def trajectories_true_vertical_depth(self) -> DistanceRange:
        """Get a range of minimum and maximum true vertical depth on trajectories

        Returns:
            DistanceRange: a range representing minimum and maximum true vertical depth
        """
        path: str = self._get_path("/summaries/trajectories/trueverticaldepth")
        response: Response = self.client.get(url_path=path)
        return DistanceRange.parse_raw(response.text)

    def trajectories_dogleg_severity(self) -> DoglegSeverityRange:
        """Get a range of minimum and maximum dogleg severity on trajectories

        Returns:
            DoglegSeverityRange: a range representing minimum and maximum dogleg severity
        """
        path: str = self._get_path("/summaries/trajectories/doglegseverity")
        response: Response = self.client.get(url_path=path)
        return DoglegSeverityRange.parse_raw(response.text)

    def well_properties(self, types: List[WellPropertiesEnum]) -> WellPropertiesList:
        """Get aggregated well properties.

        Send in a list of aggregation criteria's, and get wells grouped by the
        criterias.

        Args:
            types (List[WellPropertiesEnum]): [description]

        Returns:
            WellPropertiesList: [description]

        Examples
            Group by region and field
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> groups = wm.summaries.well_properties(["region", "field"])
                >>> groups.to_pandas()
                      region     field  wellsCount
                0  North Sea   ALVHEIM           3
                1  North Sea  SLEIPNER           2
                2  North Sea      None           1
        """
        path: str = self._get_path("/summaries/wellproperties")
        request_body = WellPropertiesSummaryRequest(items=types).json()
        response: Response = self.client.post(url_path=path, json=request_body)
        data: WellPropertiesSummaryItems = WellPropertiesSummaryItems.parse_raw(response.text)
        return WellPropertiesList(data.items)

    def _summary(self, route: str) -> SummaryList:
        path: str = self._get_path(f"/summaries/{route}")
        response: Response = self.client.get(url_path=path)
        items: List[SummaryCount] = SummaryItems.parse_raw(response.text).items
        return SummaryList(items)
