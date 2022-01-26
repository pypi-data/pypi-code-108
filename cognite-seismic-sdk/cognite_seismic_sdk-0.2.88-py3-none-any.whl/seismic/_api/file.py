# Copyright 2019 Cognite AS

import os
from typing import *

import deprecation
from cognite.seismic._api.api import API
from google.protobuf.struct_pb2 import Struct

if not os.getenv("READ_THE_DOCS"):

    import google.protobuf.wrappers_pb2 as wrappers
    from cognite.seismic.protos.ingest_service_messages_pb2 import (
        DeleteFileRequest,
        EditFileAccessRequest,
        EditFileRequest,
        IngestFileRequest,
        RegisterFileRequest,
    )
    from cognite.seismic.protos.query_service_messages_pb2 import (
        FileCoverageRequest,
        FileLineQueryRequest,
        FileQueryRequest,
        HeaderFileQueryRequest,
        SegYQueryRequest,
    )
    from cognite.seismic.protos.types_pb2 import (
        CRS,
        ExternalId,
        FileStep,
        GeoJson,
        Geometry,
        LineBasedRectangle,
        PositionQuery,
        Wkt,
    )
    from google.protobuf.empty_pb2 import Empty


class FileAPI(API):
    def __init__(self, query, ingestion):
        super().__init__(query=query, ingestion=ingestion)

    def list(self):
        """List all the files.

        Returns:
           A generator of File protocol messages: the files visible in the project, including metadata.
        """
        return (file for file in self.query.ListFiles(Empty()).files)

    def get(self, file_id: Optional[str] = None, file_name: Optional[str] = None):
        """Get a file by either id or name.

        Args:
            file_id (str): Id of the file.
            file_name (str): Name of the file.

        Returns:
            GetFileResponse: File information including file id and name, crs, path, survey_name and the last step of
             the ingestion job

        """
        file = self.identify(file_id, file_name)
        request = FileQueryRequest(file=file)
        return self.query.GetFile(request)

    def get_binary_header(
        self, file_id: Optional[str] = None, file_name: Optional[str] = None, include_raw_header=False
    ):
        """Get binary header of a file by either its id or name

        Args:
            file_id (str): Id of the file.
            file_name (str): Name of the file.
            include_raw_header (bool): True of raw header should be included.

        Returns:
            GetBinaryHeaderResponse: binary header
        """
        file = self.identify(file_id, file_name)
        request = HeaderFileQueryRequest(file=file, include_raw_header=include_raw_header)
        return self.query.GetBinaryHeader(request)

    def get_text_header(self, file_id: Optional[str] = None, file_name: Optional[str] = None, include_raw_header=False):
        """Get text header of a file by either its id or name.

        Args:
            file_id (str): Id of the file.
            file_name (str): Name of the file.
            include_raw_header (bool): True of the raw header should be included.

        Returns:
            GetTextHeaderResponse: text header
        """
        file = self.identify(file_id, file_name)
        request = HeaderFileQueryRequest(file=file, include_raw_header=include_raw_header)
        return self.query.GetTextHeader(request)

    def get_file_coverage(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        crs: Optional[str] = None,
        in_wkt: bool = False,
    ):
        """Get the coverage polygon for a given file identified by either its id or name

        Args:
            file_id (str): Id of the file.
            file_name (str): Name of the file.
            crs (str): (Optional) converts coverage to given CRS if provided. Else returns the original.
            in_wkt (bool): True to return WKT, False (default) to return geoJson.

        Returns:
            DataCoverageResponse: coverage polygon.
        """
        file = self.identify(file_id, file_name)
        wrapped_crs = {"crs": crs} if crs is not None else None
        request = FileCoverageRequest(file=file, crs=wrapped_crs, in_wkt=in_wkt)
        return self.query.GetFileDataCoverage(request)

    @staticmethod
    def _verify_input(crs: str = None, wkt: str = None, geo_json: str = None):
        if not crs:
            raise Exception("CRS is required")
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    def get_segy(self, file_id: Optional[str] = None, file_name: Optional[str] = None):
        """Get a full SEGY file by either its id or name

        Args:
            file_id (str): Id of the file.
            file_name (str): Name of the file.

        Returns:
            SegYQueryResponse: SEGY file
        """
        file = self.identify(file_id, file_name)
        request = SegYQueryRequest(file=file)
        return (i for i in self.query.GetSegYFile(request))

    def get_segy_by_lines(
        self,
        top_left_inline: int,
        top_left_xline: int,
        bottom_right_inline: int,
        bottom_right_xline: int,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
    ):
        """Get a part of a SEGY file with data inside a given range of inlines and xlines

        Args:
            file_id (str): Id of the file.
            file_name (str): Name of the file.
            top_left_inline (int): Top left inline index.
            top_left_xline (int): Top left xline index.
            bottom_right_inline (int): Bottom right inline index.
            bottom_right_xline (int): Bottom right xline index.

        Returns:
            SegYQueryResponse: SEGY file

        """
        file = self.identify(file_id, file_name)
        top_left = PositionQuery(iline=top_left_inline, xline=top_left_xline)
        bottom_right = PositionQuery(iline=bottom_right_inline, xline=bottom_right_xline)
        rectangle = LineBasedRectangle(top_left=top_left, bottom_right=bottom_right)
        request = SegYQueryRequest(file=file, lines=rectangle)
        return (i for i in self.query.GetSegYFile(request))

    def get_segy_by_geometry(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        crs: str = None,
        wkt: str = None,
        geo_json=None,
    ):
        """Get a part of a SEGY file with data inside an arbitrary 2D polygon

        Args:
            file_id (str): Id of the file.
            file_name (str): Name of the file.
            crs (str): CRS
            wkt (str): polygon in WKT format
            geo_json (dict): polygon in geoJson format

        Returns:

        """
        file = self.identify(file_id, file_name)
        self._verify_input(crs, wkt, geo_json)
        if geo_json:
            geo_json_struct = Struct()
            geo_json_struct.update(geo_json)
            geo = Geometry(crs=CRS(crs=crs), geo=GeoJson(json=geo_json_struct))
        else:
            geo = Geometry(crs=CRS(crs=crs), wkt=Wkt(geometry=wkt))

        request = SegYQueryRequest(file=file, polygon=geo)
        return (i for i in self.query.GetSegYFile(request))

    def get_line_range(self, file_id: Optional[str] = None, file_name: Optional[str] = None):
        """Get the minimum and maximum xlines and inlines

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)

        Returns:
            The line range
        """
        file = self.identify(file_id, file_name)
        request = FileQueryRequest(file=file)
        return self.query.GetFileLineRange(request)

    def get_xlines_by_inline(self, file_id: Optional[str] = None, file_name: Optional[str] = None, inline: int = None):
        """Get the range of xlines by a specific inline

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            inline (int): The inline for which to get a crossline

        Returns:
            The line range
        """
        file = self.identify(file_id, file_name)
        request = FileLineQueryRequest(file=file, line=inline)
        return self.query.GetCrosslinesByInline(request)

    def get_inlines_by_xline(self, file_id: Optional[str] = None, file_name: Optional[str] = None, xline: int = None):
        """Get the range of inlines by a specific xline

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            xline (int): The xline for which to get an inline

        Returns:
            The line range
        """
        file = self.identify(file_id, file_name)
        request = FileLineQueryRequest(file=file, line=xline)
        return self.query.GetInlinesByCrossline(request)

    def register(
        self,
        survey_id: Optional[str] = None,
        survey_name: Optional[str] = None,
        bucket: Optional[str] = None,
        file_name: str = None,
        crs: Optional[str] = None,
        metadata: dict = None,
        is_temporary: bool = False,
        inline_offset: Optional[int] = None,
        xline_offset: Optional[int] = None,
        cdp_x_offset: Optional[int] = None,
        cdp_y_offset: Optional[int] = None,
        source_group_scalar_override: Optional[float] = None,
        external_id: Optional[str] = None,
    ):
        """Register a file on a survey

        Args:
            survey_id (str): The survey is identified by either the id or the name. If both are given, the id is used.
            survey_name (str): The survey is identified by either the id or the name. If both are given, the id is used.
            bucket (str): Path to the directory in Google Cloud Storage in which the file is stored
            file_name (str): The file name in Google Cloud Storage. Also used for identifying the file
            crs (str, optional): The CRS of the file. If not given, the CRS will be taken from the survey.
            metadata (dict, optional): A string -> string dictionary with any metadata to add about the file
            is_temporary: is the file temporary - ie generated on the fly instead of being ingested from the bucket
            inline_offset: Byte offset of inline number field in the trace headers. Defaults to 189 as per the SEG-Y rev1 specification
            xline_offset: Byte offset of crossline number field in the trace headers. Defaults to 193 as per the SEG-Y rev1 specification
            cdp_x_offset: Byte offset of x coordinate of ensemble (CDP) position in trace headers. Defaults to 181 as per the SEG-Y rev1 specification
            cdp_y_offset: Byte offset of y coordinate of ensemble (CDP) position in trace headers. Defaults to 185 as per the SEG-Y rev1 specification
            source_group_scalar_override: Multiplier for CDP-X and CDP-Y values, overrides scalar factor obtained from trace header.

                Note that this is a straight multiplier to be applied, not a value to be interpreted like he SEG-Y trace header field.
                Valid values for this parameter are in the range 0.0 < n <= 1.0

            external_id: An optional external id for a file

        Returns:
             The response from the gRPC server with the id the file was registered on.
        """
        survey = self.identify(survey_id, survey_name)
        crs = CRS(crs=crs) if crs is not None else None
        inline_offset_wrapped = None if inline_offset == None else wrappers.Int32Value(value=inline_offset)
        xline_offset_wrapped = None if xline_offset == None else wrappers.Int32Value(value=xline_offset)
        cdp_x_offset_wrapped = None if cdp_x_offset == None else wrappers.Int32Value(value=cdp_x_offset)
        cdp_y_offset_wrapped = None if cdp_y_offset == None else wrappers.Int32Value(value=cdp_y_offset)
        source_group_scalar_override = (
            None if source_group_scalar_override == None else wrappers.FloatValue(value=source_group_scalar_override)
        )
        external_id = None if external_id == None else ExternalId(external_id=external_id)
        request = RegisterFileRequest(
            survey=survey,
            path=bucket,
            name=file_name,
            crs=crs,
            metadata=metadata,
            is_temporary=wrappers.BoolValue(value=is_temporary),
            inline_offset=inline_offset_wrapped,
            crossline_offset=xline_offset_wrapped,
            cdp_x_offset=cdp_x_offset_wrapped,
            cdp_y_offset=cdp_y_offset_wrapped,
            source_group_scalar_override=source_group_scalar_override,
            external_id=external_id,
        )
        return self.ingestion.RegisterFile(request)

    def ingest(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        start_step: int = 1,
        storage_tier: Optional[str] = None,
    ):
        """Ingest a registered file.

        Args:
            file_id(str): File id of the registered file.
            file_name(str): File name of the registered file.
            start_step(int): Selected step to start ingestion. Leave blank to start from last completed step.
               0: REGISTER

               1: INSERT_FILE_HEADERS

               2: INSERT_TRACE_HEADERS

               3: INSERT_DATA

               4: COMPUTE_COVERAGE

               5: COMPUTE_GRID

               6: COMPUTE_TRACE_INDICES
            storage_tier(str): Optional target storage tier. Leave blank to use the default storage tier.
                EARLY ACCESS: Tiered storage is available in preview for select clients. Tier names and configurations
                are client specific and not further documented here.

        Returns:
            IngestFileResponse: a Job id that can be used to query for status of the ingestion job, and the file id.
        """
        if start_step not in FileStep.values():
            raise Exception("Invalid `start_step`")
        file = self.identify(file_id, file_name)
        if not start_step:
            request = IngestFileRequest(file=file, target_storage_tier_name=storage_tier)
        else:
            request = IngestFileRequest(file=file, start_step=start_step, target_storage_tier_name=storage_tier)
        return self.ingestion.IngestFile(request)

    def delete(self, file_id: Optional[str] = None, file_name: Optional[str] = None, keep_registered: bool = None):
        """Delete a file by either its id or name

        Args:
            file_id: Id of the file.
            file_name: Name of the file.
            keep_registered: True if the file should be kept registered.

        Returns:
            Nothing
        """
        file = self.identify(file_id, file_name)
        request = DeleteFileRequest(file=file, keep_registered=keep_registered)
        return self.ingestion.DeleteFile(request)

    def edit(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        bucket: str = None,
        new_name: str = None,
        metadata: dict = None,
        crs: str = None,
        inline_offset: Optional[int] = None,
        xline_offset: Optional[int] = None,
        cdp_x_offset: Optional[int] = None,
        cdp_y_offset: Optional[int] = None,
        source_group_scalar_override: Optional[float] = None,
        external_id: Optional[str] = None,
    ):
        """Edit a file by either its id or name.

        Args:
            file_id (str): Id of the file.
            name (str): Name of the file.
            bucket (str): New path of the file.
            new_name (str): New name of the file.
            metadata (dict): New metadata of the file.
            crs (str): New CRS of the file.
            inline_offset: Byte offset of inline number field in the trace headers.
            xline_offset: Byte offset of crossline number field in the trace headers.
            cdp_x_offset: Byte offset of x coordinate of ensemble (CDP) position in trace headers.
            cdp_y_offset: Byte offset of y coordinate of ensemble (CDP) position in trace headers.
            source_group_scalar_override: Multiplier for CDP-X and CDP-Y values, overrides scalar factor obtained from trace header.

                Note that this is a straight multiplier to be applied, not a value to be interpreted like he SEG-Y trace header field.
                Valid values for scalars multipliers are in the range 0.0 < n <= 1.0.
                To delete an existing source group scalar override set on a file, supply 0.0 or NaN in this argument.

            external_id: External id of the file

        Returns:
            EditFileResponse: File information including file id, name, path and crs.
        """
        file = self.identify(file_id, file_name)
        inline_offset_wrapped = None if inline_offset == None else wrappers.Int32Value(value=inline_offset)
        xline_offset_wrapped = None if xline_offset == None else wrappers.Int32Value(value=xline_offset)
        cdp_x_offset_wrapped = None if cdp_x_offset == None else wrappers.Int32Value(value=cdp_x_offset)
        cdp_y_offset_wrapped = None if cdp_y_offset == None else wrappers.Int32Value(value=cdp_y_offset)
        source_group_scalar_override = (
            None if source_group_scalar_override == None else wrappers.FloatValue(value=source_group_scalar_override)
        )
        crs_wrapped = None if crs == None else CRS(crs=crs)
        external_id = None if external_id == None else ExternalId(external_id=external_id)
        request = EditFileRequest(
            file=file,
            path=bucket,
            name=new_name,
            metadata=metadata,
            crs=crs_wrapped,
            inline_offset=inline_offset_wrapped,
            crossline_offset=xline_offset_wrapped,
            cdp_x_offset=cdp_x_offset_wrapped,
            cdp_y_offset=cdp_y_offset_wrapped,
            source_group_scalar_override=source_group_scalar_override,
            external_id=external_id,
        )
        return self.ingestion.EditFile(request=request)

    @deprecation.deprecated(deprecated_in="0.2.63", details="Multitenant file sharing is not supported anymore")
    def grant_access(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        project_id: Optional[str] = None,
        project_name: Optional[str] = None,
    ):
        """Grants access to a file to another CDF project.
           The file must have been registered (owned) by the currently authorized project

        Args:
            file_id (str): Id of the file. (optional if name is filled)
            file_name (str): Name of the file. (optional if id is filled)
            project_id (str): Id of the project to grant access to (optional if name is filled)
            project_name (str): Name of the project to grant access to (optional if id is filled)
        """
        file = self.identify(file_id, file_name)
        project = self.identify(project_id, project_name)
        request = EditFileAccessRequest(file=file, project=project, add=True)
        self.ingestion.EditFileAccess(request=request)

    @deprecation.deprecated(deprecated_in="0.2.63", details="Multitenant file sharing is not supported anymore")
    def revoke_access(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        project_id: Optional[str] = None,
        project_name: Optional[str] = None,
    ):
        """Grants access to a file to another CDF project.
           The file must have been registered (owned) by the currently authorized project

        Args:
            file_id (str): Id of the file. (optional if name is filled)
            file_name (str): Name of the file. (optional if id is filled)
            project_id (str): Id of the project to grant access to (optional if name is filled)
            project_name (str): Name of the project to grant access to (optional if id is filled)
        """
        file = self.identify(file_id, file_name)
        project = self.identify(project_id, project_name)
        request = EditFileAccessRequest(file=file, project=project, remove=True)
        self.ingestion.EditFileAccess(request=request)
