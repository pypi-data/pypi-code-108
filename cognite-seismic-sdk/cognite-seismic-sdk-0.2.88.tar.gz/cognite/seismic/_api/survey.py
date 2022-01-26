# Copyright 2019 Cognite AS

import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import make_geometry
from cognite.seismic.data_classes.api_types import SurveyGridTransformation, survey_grid_transformation_to_proto
from google.protobuf.struct_pb2 import Struct

if not os.getenv("READ_THE_DOCS"):

    from cognite.seismic.protos.ingest_service_messages_pb2 import (
        DeleteSurveyRequest,
        EditSurveyRequest,
        RegisterSurveyRequest,
    )
    from cognite.seismic.protos.query_service_messages_pb2 import (
        ListSurveysQueryRequest,
        MetadataFilter,
        SearchSurveyRequest,
        SurveyQueryRequest,
    )
    from cognite.seismic.protos.types_pb2 import (
        CRS,
        CoverageParameters,
        CustomSurveyCoverage,
        ExternalId,
        GeoJson,
        Geometry,
        TraceCorners,
        Wkt,
    )


class SurveyAPI(API):
    def __init__(self, query, ingestion):
        super().__init__(query=query, ingestion=ingestion)

    def get(
        self,
        survey_id: Optional[str] = None,
        survey_name: Optional[str] = None,
        list_files: bool = False,
        include_metadata: bool = False,
        crs: Optional[str] = None,
        in_wkt: Optional[bool] = None,
        include_grid_transformation: Optional[bool] = False,
        include_custom_coverage: Optional[bool] = False,
    ):
        """
        Get a survey by either id or name.
        Provide either crs or in_wkt to get survey coverage.

        Args:
            survey_id (str, optional): survey id.
            survey_name (str, optional): survey name.
            list_files (bool): true if the files from this survey should be listed.
            include_metadata (bool): true if metadata should be included in the response.
            crs: the crs in which the survey coverage is returned, default is original survey crs
            in_wkt: survey coverage format, set to true if wkt format is needed, default is geojson format
            include_grid_transformation (bool, optional): if set to True, return the user-specified transformation between bin grid and projected coordinates
            include_custom_coverage (bool, optional): if set to True, return the customer-specified survey coverage

        Returns:
            GetSurveyResponse: the requested survey, its files and coverage (if requested).
        """
        survey = self.identify(survey_id, survey_name)
        coverageParamCrs = CRS(crs=crs) if crs is not None else None
        coverageParams = (
            CoverageParameters(crs=coverageParamCrs, in_wkt=in_wkt)
            if coverageParamCrs is not None or in_wkt is not None
            else None
        )
        req = SurveyQueryRequest(
            survey=survey,
            list_files=list_files,
            include_metadata=include_metadata,
            include_coverage=coverageParams,
            include_grid_transformation=include_grid_transformation,
            include_custom_coverage=include_custom_coverage,
        )
        return self.query.GetSurvey(req)

    def list(
        self,
        list_files: bool = False,
        include_metadata: bool = False,
        include_grid_transformation: Optional[bool] = False,
        include_custom_coverage: Optional[bool] = False,
    ):
        """List all the surveys.

        Args:
            list_files (bool): true if the files from the surveys should be listed.
            include_metadata (bool): true if metadata should be included in the response.
            include_grid_transformation (bool, optional): if set to True, return the user-specified transformation between bin grid and projected coordinates
            include_custom_coverage (bool, optional): if set to True, return the customer-specified survey coverage

        Returns:
            SurveyWithFilesResponse: the requested surveys and their files (if requested).
        """
        return self.query.ListSurveys(
            ListSurveysQueryRequest(
                list_files=list_files,
                include_metadata=include_metadata,
                include_grid_transformation=include_grid_transformation,
                include_custom_coverage=include_custom_coverage,
            )
        )

    @staticmethod
    def _verify_input(wkt: str = None, geo_json: str = None):
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    def search(
        self,
        crs: str,
        wkt: str = None,
        geo_json: dict = None,
        survey_metadata_filter: dict = None,
        file_metadata_filter: dict = None,
        include_metadata: bool = False,
    ):
        """Finds surveys for which the coverage area intersects with the given set of coordinates or exact metadata key-value match.

        Args:
            crs (str): CRS (Ex.: "EPSG:23031").
            wkt (str): Interested area represented in WKT format. At max one geometry representation should be provided.
            geo_json (dict): Interested area represented in GeoJson format. At max one geometry representation should be provided.
            survey_metadata_filter (dict): survey metadata to filter.
            file_metadata_filter (dict): file metadata to filter.
            include_metadata (bool): true of metadata should be included in the response.

        Returns:
            SurveyWithFilesResponse: the requested surveys and their files (if requested).
        """
        if wkt and geo_json:
            raise Exception("Only one geometry representation should be provided.")

        geo = make_geometry(crs=crs, wkt=wkt, geo_json=geo_json)

        if survey_metadata_filter and file_metadata_filter:
            request = SearchSurveyRequest(
                polygon=geo,
                survey_metadata=MetadataFilter(filter=survey_metadata_filter),
                file_metadata=MetadataFilter(filter=file_metadata_filter),
                include_metadata=include_metadata,
            )
        elif survey_metadata_filter and not file_metadata_filter:
            request = SearchSurveyRequest(
                polygon=geo,
                survey_metadata=MetadataFilter(filter=survey_metadata_filter),
                include_metadata=include_metadata,
            )
        elif not survey_metadata_filter and file_metadata_filter:
            request = SearchSurveyRequest(
                polygon=geo,
                file_metadata=MetadataFilter(filter=file_metadata_filter),
                include_metadata=include_metadata,
            )
        else:
            request = SearchSurveyRequest(polygon=geo, include_metadata=include_metadata)
        return self.query.SearchSurveys(request)

    def register(
        self,
        survey_name: str,
        metadata: dict = None,
        external_id: Optional[str] = None,
        crs: Optional[str] = None,
        grid_transformation: Optional[SurveyGridTransformation] = None,
        custom_coverage_wkt: Optional[str] = None,
        custom_coverage_geojson: Optional[dict] = None,
    ):
        """Finds surveys for which the coverage area intersects with the given set of coordinates or exact metadata key-value match.

        Args:
            survey_name (str): survey name.
            metadata (dict): metadata of the survey.
            external_id: external id of the survey.
            crs (Optional[str]): Coordinate reference system to be used by all
                                 members of this survey
            grid_transformation (Optional[SurveyGridTransformation]):
                Manually specify an affine transformation between bin grid
                coordinates and projected crs coordinates, either using an
                origin point and the azimuth of the xline axis
                (:py:class:`~cognite.seismic.data_classes.api_types.P6Transformation`)
                or by specifying three or more corners of the grid as a list of
                :py:class:`~cognite.seismic.data_classes.api_types.DoubleTraceCoordinates`.
                This transformation must be valid for all members of this survey.
                If this is provided, crs must also be provided.
            custom_coverage_wkt (Optional[str]):
                Specify a custom coverage polygon for this survey in the wkt format
            custom_coverage_geojson (Optional[dict]):
                Specify a custom coverage polygon for this survey in the geojson format

        Returns:
            RegisterSurveyResponse: id, name and metadata of the survey.
        """
        external_id = None if external_id == None else ExternalId(external_id=external_id)
        wrapped_crs = None if crs is None else CRS(crs=crs)
        if wrapped_crs is None and grid_transformation is not None:
            raise Exception("crs must be provided if grid_transformation is provided")

        if custom_coverage_wkt is not None or custom_coverage_geojson is not None:
            if crs is None:
                raise Exception("crs must be provided if custom_coverage is provided")
            geo = make_geometry(crs=crs, wkt=custom_coverage_wkt, geo_json=custom_coverage_geojson)
            custom_coverage = CustomSurveyCoverage(custom_coverage=geo)
        else:
            custom_coverage = None

        request = RegisterSurveyRequest(
            name=survey_name,
            metadata=metadata,
            external_id=external_id,
            crs=wrapped_crs,
            grid_transformation=survey_grid_transformation_to_proto(grid_transformation),
            custom_coverage=custom_coverage,
        )
        return self.ingestion.RegisterSurvey(request)

    def edit(
        self,
        survey_id: Optional[str] = None,
        survey_name: Optional[str] = None,
        metadata: dict = None,
        external_id: Optional[str] = None,
        crs: Optional[str] = None,
        grid_transformation: Optional[SurveyGridTransformation] = None,
        custom_coverage_wkt: Optional[str] = None,
        custom_coverage_geojson: Optional[dict] = None,
        clear_custom_coverage: Optional[bool] = False,
    ):
        """Edit a survey

        Args:
            survey_id (Optional[str]): id of the survey to edit.
            survey_name (Optional[str]): name of the survey to edit.
            metadata (dict): metadata of the survey to edit.
            external_id (Optional[str]): external id of the survey
            crs (Optional[str]): Coordinate reference system to be used by all
                                 members of this survey
            grid_transformation (Optional[SurveyGridTransformation]):
                Manually specify an affine transformation between bin grid
                coordinates and projected crs coordinates, either using an
                origin point and the azimuth of the xline axis
                (:py:class:`~cognite.seismic.data_classes.api_types.P6Transformation`)
                or by specifying three or more corners of the grid as a list of
                :py:class:`~cognite.seismic.data_classes.api_types.DoubleTraceCoordinates`.
                This transformation must be valid for all members of this survey.
            custom_coverage_wkt (Optional[str]):
                Specify a custom coverage polygon for this survey in the wkt format
            custom_coverage_geojson (Optional[dict]):
                Specify a custom coverage polygon for this survey in the geojson format
            clear_custom_coverage (Optional[bool]):
                Set this to True to clear the custom coverage from this survey, so that coverage is
                computed as a union of the included objects.

        Returns:
            EditSurveyResponse: id, name and metadata of the survey.
        """
        survey = self.identify(survey_id, survey_name)
        wrapped_external_id = None if external_id == None else ExternalId(external_id=external_id)
        wrapped_crs = None if crs is None else CRS(crs=crs)
        if custom_coverage_wkt is not None or custom_coverage_geojson is not None:
            if clear_custom_coverage:
                raise Exception("Provide a custom_coverage or set clear_custom_coverage, but not both")
            custom_coverage = CustomSurveyCoverage(
                custom_coverage=make_geometry(crs=crs, wkt=custom_coverage_wkt, geo_json=custom_coverage_geojson)
            )
        elif clear_custom_coverage:
            custom_coverage = CustomSurveyCoverage(no_custom_coverage=CustomSurveyCoverage.NoCustomCoverage())
        else:
            custom_coverage = None

        request = EditSurveyRequest(
            survey=survey,
            name=survey_name,
            metadata=metadata,
            external_id=wrapped_external_id,
            crs=wrapped_crs,
            grid_transformation=survey_grid_transformation_to_proto(grid_transformation),
            custom_coverage=custom_coverage,
        )
        return self.ingestion.EditSurvey(request)

    def delete(self, survey_id: Optional[str] = None, survey_name: Optional[str] = None):
        """Delete a survey

        Args:
            survey_id (Optional[str]): id of the survey to delete.
            survey_name (Optional[str]): name of the survey to delete.

        Returns:
            Nothing

        """
        survey = self.identify(survey_id, survey_name)
        request = DeleteSurveyRequest(survey=survey)
        return self.ingestion.DeleteSurvey(request)
