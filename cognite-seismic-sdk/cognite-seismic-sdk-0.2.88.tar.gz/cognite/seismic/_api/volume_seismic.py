# Copyright 2019 Cognite AS

import os
from typing import *

import numpy as np
from cognite.seismic._api.api import API
from cognite.seismic._api.utility import Direction, LineRange, MaybeString, get_identifier, get_search_spec
from cognite.seismic.data_classes.api_types import RangeInclusive, Trace, VolumeDef

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.types_pb2 import GeoJson
    from cognite.seismic.protos.types_pb2 import Geometry as GeometryProto
    from cognite.seismic.protos.types_pb2 import LineDescriptor, Wkt
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import LineBasedVolume, OptionalMap
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        SearchSeismicsRequest,
        SearchSeismicStoresRequest,
        VolumeRequest,
    )
    from google.protobuf.wrappers_pb2 import Int32Value as i32
    from google.protobuf.wrappers_pb2 import StringValue
else:
    from cognite.seismic._api.shims import LineDescriptor


class ArrayData(NamedTuple):
    """Encapsulates the array returned from :py:meth:`VolumeSeismicAPI.get_array`, along with metadata about coordinates.

    Attributes:
        volume_data: 3D Array containing the requested volume data
        crs: The coordinate system used
        coord_x: 2D array containing the x coordinate of each (inline, xline) pair
        coord_y: 2D array containing the y coordinate of each (inline, xline) pair
        inline_range: The range of inline ids described by the first dimension of the array
        xline_range: The range of xline ids described by the second dimension of the array
        z_range: The range of depth indices described by the third dimension of the array
    """

    volume_data: np.ma.MaskedArray
    crs: str
    coord_x: np.ma.MaskedArray
    coord_y: np.ma.MaskedArray
    inline_range: RangeInclusive
    xline_range: RangeInclusive
    z_range: RangeInclusive

    def __repr__(self) -> str:
        return (
            f"ArrayData(volume_data=<array of shape {self.volume_data.shape}>, "
            f"crs={repr(self.crs)}, "
            f"coord_x=<array of shape {self.coord_x.shape}>, "
            f"coord_y=<array of shape {self.coord_x.shape}>, "
            f"inline_range={repr(self.inline_range)}, "
            f"xline_range={repr(self.xline_range)}, "
            f"z_range={repr(self.z_range)})"
        )


class GetVolumeSize(NamedTuple):
    """Information about the size returned from get_volume.

    Attributes:
        trace_count: The number of traces that will be streamed
        sample_count: The number of samples in each trace, if available
        size_kilobytes: An estimate of the total streaming size in kilobytes (= 1024 bytes),
                        or None if sample_count is None
    """

    trace_count: int
    sample_count: Optional[int]
    size_kilobytes: Optional[int]


class VolumeSeismicAPI(API):
    def __init__(self, query, ingestion):
        super().__init__(query=query, ingestion=ingestion)

    def get_volume(
        self,
        *,
        id: Optional[int] = None,
        external_id: MaybeString = None,
        seismic_store_id: Optional[int] = None,
        inline_range: Optional[LineRange] = None,
        xline_range: Optional[LineRange] = None,
        z_range: Optional[LineRange] = None,
        include_trace_header: bool = False,
    ) -> Iterable[Trace]:
        """Retrieve traces from a seismic or seismic store

        Provide one of: the seismic id, the seismic external id, the seismic store id.
        The line ranges are specified as tuples of either (start, end) or (start, end, step).
        If a line range is not specified, the maximum ranges will be assumed.

        Args:
            id (int | None): The id of the seismic to query
            external_id (str | None): The external id of the seismic to query
            seismic_store_id (int | None): The id of the seismic store to query
            inline_range ([int, int] | [int, int, int] | None): The inline range
            xline_range ([int, int] | [int, int, int] | None): The xline range
            z_range ([int, int] | [int, int, int]): The range of samples to include
            include_trace-header (bool): Whether to include trace header info in the response.

        Returns:
            Iterable[:py:class:`~cognite.seismic.data_classes.api_types.Trace`], the traces for the specified volume
        """
        inline = into_line_range(inline_range)
        xline = into_line_range(xline_range)
        zline = into_line_range(z_range)
        lbs = LineBasedVolume(iline=inline, xline=xline, z=zline)
        req = VolumeRequest(volume=lbs, include_trace_header=include_trace_header)
        if seismic_store_id:
            req.seismic_store_id = seismic_store_id
        else:
            req.seismic.MergeFrom(get_identifier(id, external_id))

        for proto in self.query.GetVolume(req):
            yield Trace.from_proto(proto)

    def _get_volumedef(
        self, *, id: Optional[int] = None, external_id: MaybeString = None, seismic_store_id: Optional[int] = None
    ) -> VolumeDef:
        """Helper function for get_volume_size and get_array to fetch the volumedef"""
        if seismic_store_id:
            spec = get_search_spec(id=seismic_store_id)
            req = SearchSeismicStoresRequest(seismic_store=spec)
            req.include_volume_definitions = True
            [store] = self.query.SearchSeismicStores(req)
            return VolumeDef.from_proto(store.inline_volume_def)
        else:
            spec = get_search_spec(id, external_id)
            req = SearchSeismicsRequest(seismic=spec)
            req.include_volume_definition = True
            [seismic] = self.query.SearchSeismics(req)
            return VolumeDef.from_proto(seismic.volume_def)

    def get_volume_size(
        self,
        *,
        id: Optional[int] = None,
        external_id: MaybeString = None,
        seismic_store_id: Optional[int] = None,
        inline_range: Optional[LineRange] = None,
        xline_range: Optional[LineRange] = None,
        z_range: Optional[LineRange] = None,
        include_trace_header: bool = False,
    ) -> GetVolumeSize:
        """Estimate the total size of data streamed by get_volume

        Parameters: See :py:meth:`VolumeSeismicAPI.get_volume`

        Returns:
            A :py:class:`~GetVolumeSize` object describing the size
        """
        volumedef = self._get_volumedef(id=id, external_id=external_id, seismic_store_id=seismic_store_id)
        trace_count = volumedef.count_total_traces(inline_range=inline_range, xline_range=xline_range)
        sample_count = volumedef.parsed.get("sample_count")
        if z_range[0] < 0:
            raise Exception("z_range has min < 0")
        if z_range[0] > z_range[1]:
            raise Exception("z_range has min > max")
        if sample_count is not None:
            if z_range is not None:
                z_range = RangeInclusive.from_linerange(z_range)
                # Clip range to be within (0..=sample_count)
                start = min(z_range.start, sample_count)
                stop = min(z_range.stop, sample_count)
                z_range = RangeInclusive(start, stop, z_range.step)
                sample_count = len(z_range)

            # According to segy spec
            header_size = 240 if include_trace_header else 0
            int32_size = 4
            float_size = 4
            # I guess we will have to do with this estimate?
            crs_size = len(b"EPSG:23031") + 1  # Null-terminated?
            coordinate_size = crs_size + 2 * float_size
            trace_size = header_size + 2 * int32_size + float_size * sample_count + coordinate_size
            size_bytes = trace_count * trace_size
            size_kilobytes = round(size_bytes / 1024)
        else:
            size_kilobytes = None

        return GetVolumeSize(trace_count=trace_count, sample_count=sample_count, size_kilobytes=size_kilobytes)

    # Refuse to allocate arrays larger than this
    # FIXME(audunska): Figure out the right limit here, or maybe just use numpy's memory limit
    ARR_LIM = 1e8

    def get_array(
        self,
        *,
        id: Optional[int] = None,
        external_id: MaybeString = None,
        seismic_store_id: Optional[int] = None,
        inline_range: Optional[LineRange] = None,
        xline_range: Optional[LineRange] = None,
        z_range: Optional[LineRange] = None,
        progress: Optional[bool] = False,
    ) -> ArrayData:
        """Store traces from a seismic or seismic store into a numpy array

        Provide one of: the seismic id, the seismic external id, the seismic store id.
        The line ranges are specified as tuples of either (start, end) or (start, end, step).
        If a line range is not specified, the maximum ranges will be assumed.

        Args:
            id (int | None): The id of the seismic to query
            external_id (str | None): The external id of the seismic to query
            seismic_store_id (int | None): The id of the seismic store to query
            inline_range ([int, int] | [int, int, int] | None): The inline range
            xline_range ([int, int] | [int, int, int] | None): The xline range
            z_range ([int, int] | [int, int, int]): The range of samples to include
            progress: (bool): If set to true, display a progress bar. Default: False

        Returns:
            An :py:class:`~ArrayData` object encapsulating the retrieved array (see below)
        """

        volumedef = self._get_volumedef(id=id, external_id=external_id, seismic_store_id=seismic_store_id)
        z_size = volumedef.parsed.get("sample_count")

        # Compute optimal ranges
        if inline_range is None:
            inline_res = volumedef.common_inline_range()
        else:
            inline_res = RangeInclusive.from_linerange(inline_range)
        if xline_range is None:
            xline_res = volumedef.common_xline_range()
        else:
            xline_res = RangeInclusive.from_linerange(xline_range)
        inline_size = len(inline_res)
        xline_size = len(xline_res)
        if z_range is not None:
            z_res = RangeInclusive.from_linerange(z_range)
            z_size = len(z_res)
        elif z_size is not None:
            z_res = RangeInclusive(0, z_size - 1)
        else:
            z_res = None

        def alloc(z_size):
            if inline_size * xline_size * z_size > self.ARR_LIM:
                raise ValueError(
                    f"Array of size ({inline_size},{xline_size},{z_size}) has more than {self.ARR_LIM} elements. Consider restricting the array using inline_range etc."
                )
            return np.ma.masked_all((inline_size, xline_size, z_size), dtype="float")

        if z_size is not None:
            volume_data = alloc(z_size)

        crs = None
        coord_x = np.ma.masked_all((inline_size, xline_size), dtype="float")
        coord_y = np.ma.masked_all((inline_size, xline_size), dtype="float")
        # Fetch data
        traces = self.get_volume(
            id=id,
            external_id=external_id,
            seismic_store_id=seismic_store_id,
            inline_range=inline_range,
            xline_range=xline_range,
            z_range=z_range,
            include_trace_header=False,
        )
        if progress:
            try:
                from tqdm.auto import tqdm
            except ImportError:
                raise Exception("progress=True requires the tqdm package. Install with 'pip install tqdm'.")
            traces = tqdm(traces, total=volumedef.count_total_traces(inline_range, xline_range))
        for trace in traces:
            if z_size is None:
                z_size = len(trace.trace)
                z_res = RangeInclusive(0, z_size - 1)
                # Now we know the trace length, so allocate
                volume_data = alloc(z_size)

            inline_ind = inline_res.index(trace.inline)
            xline_ind = xline_res.index(trace.xline)
            volume_data[inline_ind, xline_ind, :] = trace.trace
            if crs is None:
                crs = trace.coordinate.crs
            elif trace.coordinate.crs != crs:
                raise Exception("Incompatible coordinate systems between traces")
            coord_x[inline_ind, xline_ind] = trace.coordinate.x
            coord_y[inline_ind, xline_ind] = trace.coordinate.y
        return ArrayData(
            volume_data=volume_data,
            crs=crs,
            coord_x=coord_x,
            coord_y=coord_y,
            inline_range=inline_res,
            xline_range=xline_res,
            z_range=z_res,
        )


def into_line_range(linerange: Optional[LineRange]) -> LineDescriptor:
    "Converts a tuple of two or three values into a LineDescriptor"
    if linerange is None:
        return None
    if len(linerange) == 2:
        start, stop = linerange
        return LineDescriptor(min=i32(value=start), max=i32(value=stop))
    if len(linerange) == 3:
        start, stop, step = linerange
        return LineDescriptor(min=i32(value=start), max=i32(value=stop), step=i32(value=step))
    raise Exception("A line range should be None, (int, int), or (int, int, int).")
