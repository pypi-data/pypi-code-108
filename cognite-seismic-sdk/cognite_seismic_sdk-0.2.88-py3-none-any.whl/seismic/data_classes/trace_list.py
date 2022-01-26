# Copyright 2019 Cognite AS

import itertools
from enum import Enum

import numpy as np
from cognite.seismic.data_classes.custom_list import CustomList

TRACE_HEADER_SIZE = 240


class TraceField(Enum):
    """
    Trace header field enumerator
    """

    SourceGroupScalar = 70
    CDP_X = 180
    CDP_Y = 184
    INLINE_3D = 188
    CROSSLINE_3D = 192


def _read_header_short(trace_header, ie):
    i = ie.value
    return int.from_bytes(trace_header[i : i + 2], byteorder="big", signed=True)


def _read_header_int(trace_header, ie):
    i = ie.value
    return int.from_bytes(trace_header[i : i + 4], byteorder="big", signed=True)


def _get_dimensions(traces):
    if not traces:
        return ([0, 0], [0, 0], 0)

    inline_range = [2147483647, -2147483648]
    xline_range = [2147483647, -2147483648]
    trace_len = 0

    for trace in traces:
        inline_range[0] = min(inline_range[0], trace.iline.value)
        inline_range[1] = max(inline_range[1], trace.iline.value)
        xline_range[0] = min(xline_range[0], trace.xline.value)
        xline_range[1] = max(xline_range[1], trace.xline.value)
        trace_len = max(trace_len, len(trace.trace))

    if trace_len == 0:
        return ([0, 0], [0, 0], 0)

    return (inline_range, xline_range, trace_len)


class Trace:
    def __init__(self, trace):
        self.__trace = trace

    def __getitem__(self, item):
        return self.__trace[item]

    def __getattr__(self, item):
        return getattr(self.__trace, item)

    def __repr__(self):
        return repr(self.__trace)

    def _check_headers(self):
        if len(self.__trace.trace_header) != TRACE_HEADER_SIZE:
            raise ValueError("Header not requested")

    def get_source_group_scalar(self):
        self._check_headers()
        return _read_header_short(self.__trace.trace_header, TraceField.SourceGroupScalar)

    def get_x(self):
        self._check_headers()
        x = float(_read_header_int(self.__trace.trace_header, TraceField.CDP_X))
        scale_factor = self.get_source_group_scalar()
        if scale_factor > 0:
            x = x * scale_factor
        elif scale_factor < 0:
            x = x / -scale_factor
        return x

    def get_y(self):
        self._check_headers()
        y = float(_read_header_int(self.__trace.trace_header, TraceField.CDP_Y))
        scale_factor = self.get_source_group_scalar()
        if scale_factor > 0:
            y = y * scale_factor
        elif scale_factor < 0:
            y = y / -scale_factor
        return y

    def get_inline(self):
        self._check_headers()
        return _read_header_int(self.__trace.trace_header, TraceField.INLINE_3D)

    def get_xline(self):
        self._check_headers()
        return _read_header_int(self.__trace.trace_header, TraceField.CROSSLINE_3D)


class TraceIteratorWrapper:
    def __init__(self, get_stream):
        self.it = (i for i in get_stream())

    def __iter__(self):
        return self

    def __next__(self):
        return Trace(self.it.__next__())


class Trace3DList(CustomList):
    def __init__(self, get_stream):
        def get_trace_stream():
            return TraceIteratorWrapper(get_stream)

        super(Trace3DList, self).__init__(get_trace_stream)

    def to_array(self):
        (inline_range, xline_range, trace_len) = _get_dimensions(self.to_list())
        volume = np.zeros((inline_range[1] - inline_range[0] + 1, xline_range[1] - xline_range[0] + 1, trace_len))
        for trace in self.iterable:
            volume[trace.iline.value - inline_range[0]][trace.xline.value - xline_range[0]] = np.append(
                np.zeros(trace_len - len(trace.trace)), trace.trace
            )
        return volume

    def xy_array(self):
        (inline_range, xline_range, trace_len) = _get_dimensions(self.to_list())
        volume = np.zeros(
            (inline_range[1] - inline_range[0] + 1, xline_range[1] - xline_range[0] + 1, 2 if trace_len > 0 else 0)
        )
        for trace in self.iterable:
            volume[trace.iline.value - inline_range[0]][trace.xline.value - xline_range[0]] = np.array(
                [trace.get_x(), trace.get_y()]
            )
        return volume


class Trace2DList(CustomList):
    def __init__(self, get_stream):
        def get_trace_stream():
            return TraceIteratorWrapper(get_stream)

        super(Trace2DList, self).__init__(get_trace_stream)

    def to_array(self):
        return np.array([np.array(t.trace) for t in self.to_list() if len(t.trace) > 0])

    def xy_array(self):
        return np.array([np.array([t.get_x(), t.get_y()]) for t in self.to_list() if len(t.trace) > 0])
