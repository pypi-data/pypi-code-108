import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.api.merge_rules.wells import WellMergeRulesAPI
from cognite.well_model.client.models.property_filter import PropertyFilter, filter_to_model
from cognite.well_model.client.models.resource_list import WellList, WellWellheadViewList
from cognite.well_model.client.models.well_merge_details import WellMergeDetailList, WellMergeDetailResource
from cognite.well_model.client.utils._auxiliary import extend_class
from cognite.well_model.client.utils._identifier_list import identifier_items, identifier_items_single
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    AssetSource,
    DateRange,
    DeleteWells,
    DistanceRange,
    IdentifierItems,
    PolygonFilter,
    Well,
    WellDepthMeasurementFilter,
    WellFilter,
    WellFilterRequest,
    WellIngestion,
    WellIngestionItems,
    WellItems,
    WellMergeDetailItems,
    WellNdsFilter,
    WellNptFilter,
    WellSearch,
    WellTimeMeasurementFilter,
    WellTopFilter,
    WellTrajectoryFilter,
    WellWellheadView,
    WellWellheadViewItems,
)

logger = logging.getLogger(__name__)


class WellsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)
        self.merge_rules = WellMergeRulesAPI(client)

        @extend_class(Well)
        def merge_details(this: Well) -> WellMergeDetailResource:
            return self.merge_details(matching_id=this.matching_id)

    def ingest(self, ingestions: List[WellIngestion]) -> WellList:
        """Ingest wells

        Args:
            ingestions (List[WellIngestion]): List of WellIngestions

        Returns:
            List[Well]: List of wells
        """
        path = self._get_path("/wells")
        json = WellIngestionItems(items=ingestions).json()
        response: Response = self.client.post(path, json)
        well_items: WellItems = WellItems.parse_obj(response.json())
        items: List[Well] = well_items.items
        return WellList(items)

    def delete(self, well_sources: List[AssetSource], recursive: bool = False):
        """Delete wells. If recursive is set to false, it will fail if a well
        has attached wellbores. If recursive is set to true, it will delete the
        well along with all its wellbores.

        **NOTE** that the delete endpoint operates on *WellIngestions* and not
        *Wells*. If a well ``well-1`` is comprised of two well ingestions
        ``EDM:well-1`` and ``WITSML:well-1``, then deleting ``EDM:well-1`` will
        not touch anything ingested under ``WITSML:well-1``.

        Args:
            well_sources (List[AssetSource]): List of well sources.
            recursive (bool, optional): [description]. Defaults to False.
                If the well has any wellbores, this flag must be set to true
                to delete it.

        Examples:
            Delete a well
                >>> from cognite.well_model import CogniteWellsClient
                >>> from cognite.well_model.models import AssetSource
                >>> wm = CogniteWellsClient()
                >>> asset_source = AssetSource(asset_external_id="EDM:well-1", source_name="EDM")
                >>> wm.wells.delete([asset_source], recursive=True)  # doctest:+SKIP
        """
        path = self._get_path("/wells/delete")
        json = DeleteWells(items=well_sources, recursive=recursive).json()
        self.client.post(path, json)

    # guaranteed to be non-empty list
    def _retrieve_multiple(self, identifiers: IdentifierItems) -> List[Well]:
        path: str = self._get_path("/wells/byids")
        response: Response = self.client.post(url_path=path, json=identifiers.json())
        wells: List[Well] = WellItems.parse_raw(response.text).items
        return wells

    def retrieve(self, asset_external_id: Optional[str] = None, matching_id: Optional[str] = None) -> Well:
        """Get well by asset external id or matching id

        Args:
            asset_external_id (str, optional)
            matching_id (str, optional)
        Returns:
            Well:
        Raises:
            CogniteAPIError: If well is not found
        Examples:
            Get well by asset external id
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> well = wm.wells.retrieve(asset_external_id="EDM:15/9-F-15")

            Get well by matching_id
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> well = wm.wells.retrieve(matching_id="15/9-F-15")
        """
        identifiers = identifier_items_single(asset_external_id, matching_id)
        return self._retrieve_multiple(identifiers)[0]

    def retrieve_multiple(
        self, asset_external_ids: Optional[List[str]] = None, matching_ids: Optional[List[str]] = None
    ) -> WellList:
        """Get wells by a list of asset external ids and matching ids

        Args:
            asset_external_ids: list of well asset external ids
            matching_ids: List of well matching ids
        Returns:
            List[Well]: List of wells
        """
        identifiers = identifier_items(asset_external_ids, matching_ids)
        return WellList(self._retrieve_multiple(identifiers))

    def list(
        self,
        string_matching: Optional[str] = None,
        quadrants: PropertyFilter = None,
        regions: PropertyFilter = None,
        blocks: PropertyFilter = None,
        fields: PropertyFilter = None,
        operators: PropertyFilter = None,
        sources: Optional[List[str]] = None,
        water_depth: Optional[DistanceRange] = None,
        datum: Optional[DistanceRange] = None,
        spud_date: Optional[DateRange] = None,
        well_types: PropertyFilter = None,
        licenses: PropertyFilter = None,
        trajectories: Optional[WellTrajectoryFilter] = None,
        depth_measurements: Optional[WellDepthMeasurementFilter] = None,
        time_measurements: Optional[WellTimeMeasurementFilter] = None,
        npt: Optional[WellNptFilter] = None,
        nds: Optional[WellNdsFilter] = None,
        polygon: Optional[PolygonFilter] = None,
        output_crs: Optional[str] = None,
        well_tops: Optional[WellTopFilter] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> WellList:
        """Get wells that matches the filter

        The result of this request is a list of wells with wellbores. If you are
        filtering only on well data, then each well in the response will contain
        all its wellbores. However, if you are filtering on *wellbore data*
        (trajectories, depth and time measurements, npt, nds, and well tops),
        then each well will only contain the wellbores that matched the request.

        Args:
            string_matching (Optional[str], optional): Fuzzy match on description and name.
            quadrants (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of quadrants or :class:`~cognite.well_model.NotSet`
            regions (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of regions or :class:`~cognite.well_model.NotSet`
            blocks (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of blocks or :class:`~cognite.well_model.NotSet`
            fields (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of fields or :class:`~cognite.well_model.NotSet`
            operators (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of operators or :class:`~cognite.well_model.NotSet`
            sources (Optional[List[str]], optional): List of sources on wells
            water_depth (Optional[DistanceRange], optional):
            datum: Optional[DistanceRange] optional,: Distance range for datum of the wells
            spud_date (Optional[DateRange], optional):
            well_types (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of well types or :class:`~cognite.well_model.NotSet`
            licenses (List[str] | :class:`~cognite.well_model.NotSet`, optional):  List of licenses or :class:`~cognite.well_model.NotSet`
            trajectories (Optional[WellTrajectoryFilter], optional):
            depth_measurements (Optional[WellDepthMeasurementFilter], optional):
                Filter wellbores which have measurements in certain depths.
            time_measurements (Optional[WellTimeMeasurementFilter], optional):
            npt (Optional[WellNptFilter], optional):
            nds (Optional[WellNdsFilter], optional):
            polygon (Optional[PolygonFilter], optional):
            output_crs (Optional[str], optional):
                The CRS you want the wellheads to be in. Default=EPSG:4326 (WGS84)
            well_tops (Optional[WellTopFilter], optional):
            limit (Optional[int], optional): [description]. Defaults to DEFAULT_LIMIT.

        Returns:
            WellList: List of wells

        Examples:
            Get all wells
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> wells = wm.wells.list()

            Get wells within a polygon
                >>> from cognite.well_model import CogniteWellsClient
                >>> from cognite.well_model.models import PolygonFilter
                >>> wm = CogniteWellsClient()
                >>> polygon = "POLYGON((3.4 60.7,6.08 57.44,1.16 58.44,3.40 60.7))"
                >>> wells = wm.wells.list(polygon=PolygonFilter(
                ...     geometry=polygon,
                ...     crs="EPSG:4326",
                ...     geometry_type="WKT",
                ... ))

            Get wells without a block
                >>> from cognite.well_model import CogniteWellsClient, NotSet
                >>> wm = CogniteWellsClient()
                >>> wells = wm.wells.list(blocks=NotSet)

            Get wells with gamma ray measurements between 500 and 1000 feet
                >>> from cognite.well_model import CogniteWellsClient, NotSet
                >>> from cognite.well_model.models import (
                ...     ContainsAllOrAny,
                ...     DistanceRange,
                ...     WellDepthMeasurementFilter,
                ... )
                >>> wm = CogniteWellsClient()
                >>> wells = wm.wells.list(depth_measurements=WellDepthMeasurementFilter(
                ...     measured_depth=DistanceRange(unit="foot", min=500.0, max=1000.0),
                ...     measurement_types=ContainsAllOrAny(
                ...         contains_any=["gamma ray"]
                ...     )
                ... ))

            Get wellbores from wells list
                >>> from cognite.well_model import CogniteWellsClient
                >>> from cognite.well_model.models import WellNdsFilter
                >>> wm = CogniteWellsClient()
                >>> wells = wm.wells.list(nds = WellNdsFilter())
                >>> wellbores = wells.wellbores()

        """  # noqa: E501

        def request(cursor, limit):
            search = WellSearch(query=string_matching) if string_matching else None
            well_filter = WellFilterRequest(
                filter=WellFilter(
                    quadrant=filter_to_model(quadrants),
                    region=filter_to_model(regions),
                    block=filter_to_model(blocks),
                    field=filter_to_model(fields),
                    operator=filter_to_model(operators),
                    well_type=filter_to_model(well_types),
                    license=filter_to_model(licenses),
                    sources=sources,
                    water_depth=water_depth,
                    datum=datum,
                    spud_date=spud_date,
                    trajectories=trajectories,
                    depth_measurements=depth_measurements,
                    time_measurements=time_measurements,
                    polygon=polygon,
                    npt=npt,
                    nds=nds,
                    well_tops=well_tops,
                ),
                search=search,
                output_crs=output_crs,
                cursor=cursor,
                limit=limit,
            )
            path: str = self._get_path("/wells/list")
            response: Response = self.client.post(url_path=path, json=well_filter.json())
            well_items_data: WellItems = WellItems.parse_raw(response.text)
            return well_items_data

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor, get_items=lambda x: x.items, limit=limit, request=request
        )
        return WellList(items)

    def wellheads(self, limit: Optional[int] = DEFAULT_LIMIT) -> WellWellheadViewList:
        """Retrieve Wellheads view for all wells

        Args:
            limit (Optional[int], optional): [description]. Defaults to DEFAULT_LIMIT. use None to get all items.
        Returns:
            WellWellheadViewList: a list of all :class:`~cognite.well_model.models.WellWellheadViews` in the project.

        Examples:
            Get all wellheadsviews in the project
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> well_wellhead_views = wm.wells.wellheads(limit=None)
        """

        def request(cursor, limit):
            path: str = self._get_path("/wells/wellheads")
            response: Response = self.client.get(url_path=path, params={"cursor": cursor, "limit": limit})
            return WellWellheadViewItems.parse_raw(response.text)

        items: List[WellWellheadView] = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor, get_items=lambda x: x.items, limit=limit, request=request
        )
        return WellWellheadViewList(items)

    def merge_details(
        self,
        asset_external_id: Optional[str] = None,
        matching_id: Optional[str] = None,
    ) -> Optional[WellMergeDetailResource]:
        """Retrieve merge details for a well

        Args:
            asset_external_id (str, optional)
            matching_id (str, optional)
        Returns:
            Optional[WellMergeDetailResource]: merge details if the well exists.

        Examples:
            Get merge details for a single well
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> details = wm.wells.merge_details(matching_id="15/9-F-15")

            Get merge details for a single well using a Well object
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> details = wm.wells.retrieve(matching_id="15/9-F-15").merge_details()
        """
        identifiers = identifier_items_single(
            asset_external_id=asset_external_id,
            matching_id=matching_id,
        )
        identifiers.ignore_unknown_ids = True

        path = self._get_path("/wells/mergedetails")
        response = self.client.post(path, json=identifiers.json())

        items = WellMergeDetailItems.parse_raw(response.content)
        if len(items.items) == 0:
            return None
        assert len(items.items) == 1
        return WellMergeDetailResource(items.items[0])

    def merge_details_multiple(
        self,
        asset_external_ids: Optional[List[str]] = None,
        matching_ids: Optional[List[str]] = None,
        ignore_unknown_ids: Optional[bool] = False,
    ) -> WellMergeDetailList:
        """Retrieve merge details for multiple wells

        Args:
            asset_external_ids: list of well asset external ids.
            matching_ids: List of well matching ids.
            ignore_unknown_ids (Optional[bool]): If set to True,
                it will ignore unknown wells.

        Returns:
            WellMergeDetailList: List-like object of merge details

        Examples:
            Get merge details for a single well
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> details = wm.wells.merge_details_multiple(matching_ids=["15/9-F-15"])
        """
        identifiers = identifier_items(asset_external_ids, matching_ids)
        identifiers.ignore_unknown_ids = ignore_unknown_ids

        path = self._get_path("/wells/mergedetails")
        response = self.client.post(path, json=identifiers.json())

        items = WellMergeDetailItems.parse_raw(response.content)
        return WellMergeDetailList([WellMergeDetailResource(x) for x in items.items])
