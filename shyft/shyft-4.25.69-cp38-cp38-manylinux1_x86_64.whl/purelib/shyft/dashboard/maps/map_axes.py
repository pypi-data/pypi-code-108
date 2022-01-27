from typing import List, Tuple

import numpy as np
from bokeh.models import Range1d

from shyft.dashboard.time_series.bindable import Bindable, BindableError


class MapAxesRanges(Bindable):

    def __init__(self,
                 width: int,
                 height: int,
                 xmin: float=0,
                 ymin: float=0,
                 xmax: float=1,
                 ymax: float=1,
                 padding: float=0) -> None:
        """
        Class handling axes ranges for map figures. Padding is an extra distance in map units added outside the
        calculated axes range.

        Note:
        All axes bounds are defined as Tuples with x_min, y_min, x_max, y_max, i.e. defined as bbox coordinates
        """
        super().__init__()
        self._aspect_ration_xy = width/height
        self._x_min = xmin
        self._y_min = ymin
        self._x_max = xmax
        self._y_max = ymax
        self._padding = padding

        self.x_range = Range1d(start=self.x_min, end=self.x_max)
        self.y_range = Range1d(start=self.y_min, end=self.y_max)

    def on_bind(self, *, parent:  'shyft.dashboard.maps.map_viewer.MapViewer') -> None:
        """
        Function which is call when bound to a figure
        """
        try:
            parent.bokeh_figure.x_range = self.x_range
            parent.bokeh_figure.y_range = self.y_range
        except (RuntimeError, AttributeError) as e:
            raise BindableError(f"Attempt to bind MapAxes to not MapViewer {parent}: {e}")

    def set_axes_bounds(self, x_min, y_min, x_max, y_max) -> None:
        """
        Sets the ranges from Tuples[x_min, y_min, x_max, y_max], i.e. defined as bbox coordinates
        """
        self._x_min = x_min
        self._y_min = y_min
        self._x_max = x_max
        self._y_max = y_max
        self.adjust_aspect_ratio()
        self.update_ranges()

    def set_axes_bounds_from_bounds_list(self, bounds_list: List[Tuple[float, float, float, float]]) -> None:
        """
        Updates the ranges from a List[Tuples[x_min, y_min, x_max, y_max]], i.e. defined as bbox coordinates
        """
        bounds_list = np.array(bounds_list)
        self._x_min = np.min(bounds_list[:, 0])
        self._y_min = np.min(bounds_list[:, 1])
        self._x_max = np.max(bounds_list[:, 2])
        self._y_max = np.max(bounds_list[:, 3])
        self.adjust_aspect_ratio()
        self.update_ranges()

    def adjust_aspect_ratio(self):
        """
        This function adjusts y and x ranges to get an 1:1 plot axis ratio also dependent on the plot width and height
        """
        range_x = self._x_max - self._x_min
        range_y = self._y_max - self._y_min
        if range_x == 0:
            ratio = self._aspect_ration_xy-1
        elif range_y == 0:
            ratio = self._aspect_ration_xy+1
        else:
            ratio = range_x/range_y
        if ratio > self._aspect_ration_xy:
            # adjust y axis
            y_range_diff = abs(range_x/self._aspect_ration_xy-range_x)
            self._y_max += y_range_diff/2
            self._y_min -= y_range_diff/2
        elif ratio < self._aspect_ration_xy:
            # adjust x axis
            x_range_diff = abs(range_y*self._aspect_ration_xy - range_x)
            self._x_max += x_range_diff / 2
            self._x_min -= x_range_diff / 2

    @property
    def padding(self) -> float:
        """
        This property of the extra padding
        """
        return self._padding

    @padding.setter
    def padding(self, new_padding: float) -> None:
        """
        Setter to set the new padding
        """
        self._padding = new_padding
        self.update_ranges()

    @property
    def x_min(self) -> float:
        """
        This property returns the padded x_min bound
        """
        return self._x_min - self.padding

    @property
    def y_min(self) -> float:
        """
        This property returns the padded y_min bound
        """
        return self._y_min - self.padding

    @property
    def x_max(self) -> float:
        """
        This property returns the padded x_max bound
        """
        return self._x_max + self.padding

    @property
    def y_max(self) -> float:
        """
        This property returns the padded y_max bound
        """
        return self._y_max + self.padding

    @property
    def axes_bounds(self) -> Tuple[float, float, float, float]:
        """
        This function returns the axes bounds as Tuples[x_min, y_min, x_max, y_max], i.e. defined as bbox coordinates
        """
        return self.x_min, self.y_min, self.x_max, self.y_max

    def update_ranges(self) -> None:
        """
        This function triggers the update of the data ranges
        """
        self.x_range.start = self.x_min
        self.x_range.end = self.x_max

        self.y_range.start = self.y_min
        self.y_range.end = self.y_max
