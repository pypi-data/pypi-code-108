# Copyright 2019 Cognite AS

import os
from typing import *

import deprecation
from cognite.seismic._api.api import API

if not os.getenv("READ_THE_DOCS"):

    from cognite.seismic.data_classes.trace_list import Trace3DList
    from cognite.seismic.protos.ingest_service_messages_pb2 import StoreTraceRequest
    from cognite.seismic.protos.query_service_messages_pb2 import (
        GeometryCubeRequest,
        LineBasedVolume,
        LineCubeRequest,
        VolumeRequest,
    )
    from cognite.seismic.protos.types_pb2 import (
        CRS,
        GeoJson,
        Geometry,
        LineBasedRectangle,
        LineDescriptor,
        PositionQuery,
        Wkt,
    )
    from google.protobuf import wrappers_pb2 as wrappers


class VolumeAPI(API):
    def __init__(self, query, ingestion):
        super().__init__(query=query, ingestion=ingestion)

    @staticmethod
    def _verify_input(crs: str = None, wkt: str = None, geo_json: str = None):
        if not crs:
            raise Exception("CRS is required")
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    @deprecation.deprecated(
        deprecated_in="0.1.57",
        details="Use VolumeAPI.get(inline_range=(top_left_inline, bottom_right_inline), xline_range=(top_left_xline, bottom_right_xline)) instead.",
    )
    def get_cube_by_lines(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        top_left_inline=None,
        top_left_xline=None,
        bottom_right_inline=None,
        bottom_right_xline=None,
        include_trace_header=False,
    ):
        """Get a cube of trace data from a specified inline and xline square

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            top_left_inline (int): Top left inline number
            top_left_xline (int): Top left xline number
            bottom_right_inline (int): Bottom right inline number
            bottom_right_xline (int): Bottom right xline number
            include_trace_header (bool, optional): Include the trace headers (default false)

        Returns:
            Cube of trace data
        """
        file = self.identify(file_id, file_name)
        top_left = PositionQuery(iline=top_left_inline, xline=top_left_xline)
        bottom_right = PositionQuery(iline=bottom_right_inline, xline=bottom_right_xline)
        rectangle = LineBasedRectangle(top_left=top_left, bottom_right=bottom_right)
        request = LineCubeRequest(file=file, rectangle=rectangle, include_trace_header=include_trace_header)

        def get_stream():
            return self.query.GetCubeByLines(request)

        return Trace3DList(get_stream)

    def get_cube_by_geometry(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        crs: str = None,
        wkt: str = None,
        geo_json=None,
        include_trace_header: bool = False,
    ):
        """Get a cube of trace data from a specified geometry

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            crs (str): Specify the CRS in which the coordinates x0, y0, x1 and y1 are given (Ex.: "EPSG:23031")
            wkt (str, optional): Geometry can be specified either by wkt or geo json (wkt will be used first if both are provided)
            geo_json (str, optional): Geometry can be specified either by wkt or geo json (wkt will be used first if both are provided)
            include_trace_header (bool, optional): Include the trace headers (default false)

        Returns:
            Cube of trace data
        """
        file = self.identify(file_id, file_name)
        self._verify_input(crs, wkt, geo_json)
        geo = (
            Geometry(crs=CRS(crs=crs), wkt=Wkt(geometry=wkt))
            if wkt
            else Geometry(crs=CRS(crs=crs), geo=GeoJson(json=geo_json))
        )
        request = GeometryCubeRequest(file=file, geometry=geo, include_trace_header=include_trace_header)

        def get_stream():
            return self.query.GetCubeByGeometry(request)

        return Trace3DList(get_stream)

    def store(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        inline: int = None,
        xline: int = None,
        trace: List[float] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        trace_header: Optional[ByteString] = None,
    ):
        """
        Store a single trace in a given grid position of a temporary file.

        Alpha API, expected to change.

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            inline (int): Inline of the grid position where the trace should be stored.
            xline (int): Xline of the grid position where the trace should be stored.
            trace (list[Float]): Trace data to be stored. No length requirement or other data consistency constraints are enforced.
            x (int, optional): X coordinate of the trace, in the CRS of the file.
            y (int, optional): X coordinate of the trace, in the CRS of the file.
            trace_header (ByteString, optional): Trace header data to be stored along with the trace. Again, no data consistency
                requirements are enforced, you are on your own here.
        """
        file = self.identify(file_id, file_name)
        request = StoreTraceRequest(file=file, iline=inline, xline=xline, trace=trace, x=x, y=y, raw_header=bytes())
        return self.ingestion.StoreTrace(request)

    def get(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        inline_range: Optional[Tuple[int, int]] = None,
        xline_range: Optional[Tuple[int, int]] = None,
        z_index_range: Optional[Tuple[int, int]] = None,
        include_trace_header=False,
    ):
        """Get a volume of traces from a file. The volume can be sliced in any direction.

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            inline_range (int tuple, optional): filter volume by min and max inline indices
            xline_range (int tuple, optional): filter volume by min and max xline indices
            z_index_range (int tuple, optional): filter volume by min and max z indices
            include_trace_header (bool, optional): Include the trace headers (default false)
        Returns:
            Volume of traces in specified ranges. If no slices are specified, returns all the traces in the seg-y file
        """
        file = self.identify(file_id, file_name)
        volume = LineBasedVolume(
            iline=wrap_line_range(inline_range), xline=wrap_line_range(xline_range), z=wrap_line_range(z_index_range)
        )
        request = VolumeRequest(file=file, volume=volume, include_trace_header=include_trace_header)

        def get_stream():
            return self.query.GetVolume(request)

        return Trace3DList(get_stream)


def wrap_line_range(lrange: Tuple[int, int]):
    return (
        LineDescriptor(min=wrappers.Int32Value(value=lrange[0]), max=wrappers.Int32Value(value=lrange[1]))
        if lrange is not None
        else None
    )
