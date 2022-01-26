# Copyright 2019 Cognite AS

import numpy as np
from cognite.seismic.data_classes.custom_list import CustomList


def _get_dimensions(traces):
    if not traces:
        return ([0, 0], [0, 0])

    inline_range = [2147483647, -2147483648]
    xline_range = [2147483647, -2147483648]

    for trace in traces:
        inline_range[0] = min(inline_range[0], trace.iline)
        inline_range[1] = max(inline_range[1], trace.iline)
        xline_range[0] = min(xline_range[0], trace.xline)
        xline_range[1] = max(xline_range[1], trace.xline)

    return (inline_range, xline_range)


class SurfacePointList(CustomList):
    def to_array(self):
        (inline_range, xline_range) = _get_dimensions(self.to_list())
        surface = np.zeros((inline_range[1] - inline_range[0] + 1, xline_range[1] - xline_range[0] + 1))
        for trace_point in self.iterable:
            surface[trace_point.iline - inline_range[0]][trace_point.xline - xline_range[0]] = trace_point.value

        return surface
