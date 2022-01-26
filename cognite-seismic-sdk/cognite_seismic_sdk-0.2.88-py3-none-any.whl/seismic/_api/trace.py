# Copyright 2019 Cognite AS

import os
from typing import *

from cognite.seismic._api.api import API

if not os.getenv("READ_THE_DOCS"):

    from cognite.seismic.protos.query_service_messages_pb2 import (
        CoordinateQuery,
        CoordinateTraceQueryRequest,
        LineTraceQueryRequest,
    )
    from cognite.seismic.protos.types_pb2 import PositionQuery


class TraceAPI(API):
    def __init__(self, query):
        super().__init__(query=query)

    def get_trace_by_line(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        inline: int = None,
        xline: int = None,
        include_trace_header: bool = False,
        include_trace_data: bool = False,
        include_trace_coordinates: bool = False,
    ):
        """Get a trace from a specified inline and xline position

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            inline (int): Inline number
            xline (int): Xline number
            include_trace_coordinates (bool, optional): Include the trace coordinates
            include_trace_data (bool, optional): Include the trace data
            include_trace_header (bool, optional): Include the trace header

        Returns:
            Trace data
        """
        file = self.identify(file_id, file_name)
        position = PositionQuery(iline=inline, xline=xline)

        def request():  # GRPC _really_ wants an iterable argument for a streaming call
            yield LineTraceQueryRequest(
                file=file,
                position=position,
                include_trace_coordinates=include_trace_coordinates,
                include_trace_data=include_trace_data,
                include_trace_header=include_trace_header,
            )

        return self.query.GetTracesByLine(request()).next()

    def get_trace_by_coordinates(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        x: float = None,
        y: float = None,
        max_radius: float = None,
        include_trace_header: bool = False,
    ):
        """Get a trace from a specified coordinate position

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            x (float): The x coordinate
            y (float): The y coordinate
            max_radius (float, optional): If not given, uses N
            include_trace_header (bool, optional): Include the trace header

        Returns:
            Trace data
        """
        file = self.identify(file_id, file_name)
        coordinates = CoordinateQuery(x=x, y=y)
        request = CoordinateTraceQueryRequest(
            file=file, coordinates=coordinates, max_radius=max_radius, include_trace_header=include_trace_header
        )
        return self.query.GetTraceByCoordinates(request)
