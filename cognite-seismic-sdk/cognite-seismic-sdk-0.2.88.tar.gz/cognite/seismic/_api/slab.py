import os
import sys
from typing import *

import numpy as np
import numpy.ma as ma
from cognite.seismic._api.api import API
from cognite.seismic._api.file import FileAPI

if not os.getenv("READ_THE_DOCS"):

    from cognite.seismic.protos.query_service_messages_pb2 import LineSlabRequest, Surface
    from cognite.seismic.protos.types_pb2 import LineBasedRectangle, PositionQuery
    from google.protobuf.wrappers_pb2 import Int32Value


class SlabAPI(API):
    def __init__(self, query, file_api: FileAPI):
        super().__init__(query=query)
        self.file_api = file_api

    def get(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        inline_range: Tuple[int, int] = None,
        xline_range: Tuple[int, int] = None,
        z: int = None,
        surface: List[List[int]] = None,
        n_below: int = None,
        n_above: int = None,
    ):

        """Get a seismic slab along a surface or constant depth bounded by inline and xline ranges

        Args:
            file_id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            file_name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            inline_range (int tuple, optional): filter volume by min and max inline indices
            xline_range (int tuple, optional): filter volume by min and max xline indices
            n_below (int, optional): number of trace values to retrieve above given surface/depth
            n_above (int, optional): number of trace values to retrieve below given surface/depth
            z (int): The depth index to return
            surface (List[List[int]], optional): The surface to use as the depth indices across the returned traces

        Returns:
            Flattened numpy array representing the seismic slab. Dims are (inline, crossline, z_offset)
        """

        # TODO: store the results from service in an object and return that object (which would have revelant accessor methods, like
        # getting the response array z-index, or as a masked volume, or as a point cloud, or whatever else)

        file = self.identify(file_id, file_name)

        if inline_range is None or xline_range is None:
            line_range = (
                self.file_api.get_line_range(file_id=file_id)
                if file_id is not None
                else self.file_api.get_line_range(file_name=file_name)
            )
            if inline_range is None:
                inline_range = (line_range.inline.min.value, line_range.inline.max.value)
            if xline_range is None:
                xline_range = (line_range.xline.min.value, line_range.xline.max.value)

        top_left = PositionQuery(iline=inline_range[0], xline=xline_range[0])
        bottom_right = PositionQuery(iline=inline_range[1], xline=xline_range[1])
        rectangle = LineBasedRectangle(top_left=top_left, bottom_right=bottom_right)

        if z is None and surface is None:
            raise ValueError("either z or surface must be specified")

        if n_below is None:
            n_below = 0
        else:
            if n_below < 0:
                raise ValueError("n_below must be positive")
        if n_above is None:
            n_above = 0
        else:
            if n_above < 0:
                raise ValueError("n_above must be positive")

        inline_dim = inline_range[1] - inline_range[0] + 1  # +1 because range is inclusive
        xline_dim = xline_range[1] - xline_range[0] + 1  # +1 because range is inclusive

        dims = (inline_dim, xline_dim, n_above + n_below + 1)

        if z is not None:
            request = LineSlabRequest(
                file=file,
                rectangle=rectangle,
                constant=z,
                n_below=Int32Value(value=n_below),
                n_above=Int32Value(value=n_above),
            )
        else:
            if len(surface) == 0:
                raise ValueError("empty surface given")
            surface_inline_dim = len(surface)
            surface_xline_dim = len(surface[0])
            if (inline_dim, xline_dim) != (surface_inline_dim, surface_xline_dim):
                raise ValueError(
                    "mismatch between shape of inline/xline ranges and given surface. ranges shape: (%d,%d) surface shape: (%d,%d)"
                    % (inline_dim, xline_dim, surface_inline_dim, surface_xline_dim)
                )
            flat_surface = [index for inline_surface in surface for index in inline_surface]
            request = LineSlabRequest(
                file=file,
                rectangle=rectangle,
                surface=Surface(z_values=flat_surface),
                n_below=Int32Value(value=n_below),
                n_above=Int32Value(value=n_above),
            )

        output = np.full(dims, np.nan, dtype=np.float32)

        stream = self.query.GetSlabByLines(request)
        for s in stream:
            inline_index = s.trace.iline.value - inline_range[0]
            xline_index = s.trace.xline.value - xline_range[0]
            output[inline_index][xline_index][0 : (s.z_to - s.z_from + 1)] = s.trace.trace

        return output
