# Copyright 2019 Cognite AS

import os
from typing import *

from cognite.seismic._api.api import API
from google.protobuf import wrappers_pb2 as wrappers

if not os.getenv("READ_THE_DOCS"):

    from cognite.seismic.data_classes.surface_point_list import SurfacePointList
    from cognite.seismic.protos.query_service_messages_pb2 import GeometryTimeSliceQueryRequest, Surface
    from cognite.seismic.protos.types_pb2 import CRS, GeoJson, Geometry, LineBasedRectangle, PositionQuery, Wkt


class TimeSliceAPI(API):
    def __init__(self, query):
        super().__init__(query=query)

    @staticmethod
    def _verify_input(crs: str = None, wkt: str = None, geo_json: str = None):
        if not crs:
            raise Exception("CRS is required")
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    def get_time_slice_by_lines(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        top_left_inline: int = None,
        top_left_xline: int = None,
        bottom_right_inline: int = None,
        bottom_right_xline: int = None,
        z: int = None,
        surface: List[List[int]] = None,
    ):
        """Get a horizontal slice for a given depth or time and constrained by a range of inlines and xlines

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            top_left_inline (int): Top left inline number
            top_left_xline (int): Top left xline number
            bottom_right_inline (int): Bottom right inline number
            bottom_right_xline (int): Bottom right xline number
            z (int): The depth index to return
            surface (List[List[int]], optional): The surface to use as the depth indices across the returned traces
        Returns:
            A slice of trace data
        """
        raise Exception("get_time_slice_by_lines has been removed, use slab api instead: client.slab.get(..)")

    def get_time_slice_by_geometry(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        crs: str = None,
        wkt: str = None,
        geo_json=None,
        z: int = None,
    ):
        """Get a horizontal slice for a given depth or time and constrained by an arbitrary 2D polygon

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            crs (str): Specify the CRS in which the coordinates x0, y0, x1 and y1 are given (Ex.: "EPSG:23031")
            wkt (str, optional): Geometry can be specified either by wkt or geo json (wkt will be used first if both are provided)
            geo_json (str, optional): Geometry can be specified either by wkt or geo json (wkt will be used first if both are provided)
            z (int): The depth index to return
        Returns:
            A slice of trace data
        """
        file = self.identify(file_id, file_name)
        self._verify_input(crs, wkt, geo_json)
        geo = (
            Geometry(crs=CRS(crs=crs), wkt=Wkt(geometry=wkt))
            if wkt
            else Geometry(crs=CRS(crs=crs), geo=GeoJson(json=geo_json))
        )
        req = GeometryTimeSliceQueryRequest(file=file, geometry=geo, z=wrappers.Int32Value(value=z))

        def get_stream():
            return self.query.GetTimeSliceByGeometry(req)

        return SurfacePointList(get_stream)
