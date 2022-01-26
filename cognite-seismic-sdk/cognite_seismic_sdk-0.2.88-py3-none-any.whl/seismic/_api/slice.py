# Copyright 2019 Cognite AS

import os

import deprecation
import google.protobuf.wrappers_pb2 as wrappers
from cognite.seismic._api.api import API

if not os.getenv("READ_THE_DOCS"):

    from cognite.seismic.data_classes.trace_list import Trace2DList
    from cognite.seismic.protos.query_service_messages_pb2 import GeometrySliceQueryRequest, LineSliceQueryRequest
    from cognite.seismic.protos.types_pb2 import CRS, Geometry, LineRange, LineSelect, Wkt


class SliceAPI(API):
    def __init__(self, query):
        super().__init__(query=query)

    @staticmethod
    def _build_range(r_from=None, r_to=None):
        """Returns a LineRange based on to and from values"""
        if r_from or r_to:
            f = wrappers.Int32Value(value=r_from)
            t = wrappers.Int32Value(value=r_to)
            return LineRange(from_line=f, to_line=t)
        else:
            return None

    def _get_slice(self, line_select, file_identifier, include_headers, ort_range):
        """Returns a slice from the gRPC service

        Args:
            line_select: A data type specifying inline or xline
            file_identifier: A data type identifying the file
            include_headers (bool): Include headers in response
            ort_range: The range for which to get the slice (specified as line_select is inline if xline and vice versa)

        Returns:
            Traces
        """
        request = LineSliceQueryRequest(
            file=file_identifier, line=line_select, include_trace_header=include_headers, range=ort_range
        )

        def get_stream():
            return self.query.GetSliceByLine(request)

        return Trace2DList(get_stream)

    @deprecation.deprecated(
        deprecated_in="0.1.57",
        details='Use volume API instead, for example: client.volume.get(file_id="id", inline_range=(inline, inline))',
    )
    def get_inline(self, inline, file_id=None, file_name=None, include_headers=False, from_line=None, to_line=None):
        """Gets the traces of an inline in a given file.

        Args:
            inline (int): Inline number
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            include_headers (bool, optional): Whether or not to include the trace headers in the response
            from_line (int, optional): Include only xlines equal or greater to this in the slice
            to_line (int, optional): Include only xlines equal or less than this in the slice

        Returns:
            Series of traces where each contains its inline, xline and the values.
            The line can be converted to a 2D numpy array with just the values calling .to_array() on it
        """
        return self._get_slice(
            line_select=LineSelect(iline=inline),
            file_identifier=self.identify(file_id, file_name),
            include_headers=include_headers,
            ort_range=self._build_range(from_line, to_line),
        )

    @deprecation.deprecated(
        deprecated_in="0.1.57",
        details='Use volume API instead, for example: client.volume.get(file_id="id", xline_range=(xline, xline))',
    )
    def get_xline(self, xline, file_id=None, file_name=None, include_headers=False, from_line=None, to_line=None):
        """Gets the traces of a xline in a given file.

        Args:
            xline (int): xline number
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            include_headers (bool, optional): Whether or not to include the trace headers in the response
            from_line (int, optional): Include only inlines equal or greater to this in the slice
            to_line (int, optional): Include only inlines equal or less than this in the slice
        Returns:
            Series of traces where each contains its inline, xline and the values.
            The line can be converted to a 2D numpy array with just the values calling .to_array() on it
        """
        return self._get_slice(
            line_select=LineSelect(xline=xline),
            file_identifier=self.identify(file_id, file_name),
            include_headers=include_headers,
            ort_range=self._build_range(from_line, to_line),
        )

    def get_arbitrary_line(
        self, file_id=None, file_name=None, x0=None, y0=None, x1=None, y1=None, crs=None, interpolation_method=1
    ):
        """Returns a series of traces on an arbitrary line starting from (x0, yo) and ending in (x1, y1)

        Currently, all the traces are snapped to the grid inlines or xlines

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            crs (str): Specify the CRS in which the coordinates x0, y0, x1 and y1 are given (Ex.: "EPSG:23031")
            interpolation_method (int, optional): Specify the interpolation_method. Currently possible are 0 for snapping the traces to the nearest
                    grid points (inlines or xlines) or 1 for weighing the nearest traces on each side of the line
        Returns:
            Series of traces composing the line.
            The line can be converted to a 2D numpy array with just the values calling .to_array() on it
        """
        if x0 is None or y0 is None or x1 is None or y1 is None or not crs:
            raise Exception("x0, y0, x1, y1 and crs must be specified")
        p0 = f"{x0} {y0}"
        p1 = f"{x1} {y1}"
        linestring = f"LINESTRING({p0},{p1})"
        line = Geometry(crs=CRS(crs=crs), wkt=Wkt(geometry=linestring))
        file = self.identify(file_id, file_name)
        request = GeometrySliceQueryRequest(file=file, arbitrary_line=line, interpolation_method=interpolation_method)

        def get_stream():
            return self.query.GetSliceByGeometry(request)

        return Trace2DList(get_stream)
