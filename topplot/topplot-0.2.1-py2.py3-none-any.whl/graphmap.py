from typing import Callable, NamedTuple

from matplotlib.axis import Axis
from pandas import DataFrame

from .figman import FigManager

# ------------------------------------------------------------------------------


class GraphMapEntry(NamedTuple):
    fn: Callable[[FigManager, DataFrame, Axis, str, bool], None]
    data: DataFrame


GraphMap = dict[str, GraphMapEntry]


# ------------------------------------------------------------------------------
