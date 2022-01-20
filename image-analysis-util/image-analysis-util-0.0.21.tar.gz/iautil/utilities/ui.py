"""
UI widget classes.
"""

# ----------------------------------------------------------------------------------

from typing import Tuple
from matplotlib import colors
from matplotlib import pyplot as plt
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtGui, QtCore
import xarray as xr

# ----------------------------------------------------------------------------------

__all__ = (
    "DataArrayImageView",
    "DataArrayPlot",
    "set_data_array"
)

# ----------------------------------------------------------------------------------

class DataArrayImageView(pg.ImageView):
    """
    A custom PyQtGraph ImageView.
    """
    
    def __init__(self, parent=None) -> None:
        super(DataArrayImageView, self).__init__(
            parent, 
            view=pg.PlotItem(),
            imageItem=pg.ImageItem()
        )

        self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()

        self.view.setAspectLocked(lock=False)
        self.view.enableAutoRange()

    # ------------------------------------------------------------------------------

    def set_data_array(self, data_array: xr.DataArray) -> None:
        """
        
        """

        image = self._set_color_map(data_array.values)
        self.view.setLabels(
            bottom = data_array.dims[0],
            left = data_array.dims[1]
        )
        self._set_axis_coords(data_array)
        self.setImage(image)

    # ------------------------------------------------------------------------------

    def _set_color_map(self, image: np.ndarray) -> np.ndarray:
        """
        
        """

        image_max = np.amax(image)
        norm = colors.LogNorm(vmax=image_max)

        normalized_image = norm(image)
        color_image = plt.cm.jet(normalized_image)

        return color_image

    # ------------------------------------------------------------------------------

    def _set_axis_coords(self, data_array: xr.DataArray) -> None:
        """
        
        """

        def _is_monotonic(values: list):
            dx = np.diff(values)
            return np.all(dx <= 0) or np.all(dx >= 0)

        def _set_rect_values(values: list):
            if type(values[0]) == str or not _is_monotonic(values):
                start = 0
                length = len(values)
            else:
                start = values[0]
                length = values[-1] - values[0]
            return start, length
        
        x_values = data_array.coords[data_array.dims[0]].values
        y_values = data_array.coords[data_array.dims[1]].values

        x, width = _set_rect_values(x_values)
        y, height = _set_rect_values(y_values)

        self.imageItem.setOpts(rect=(x, y, width, height))

# ----------------------------------------------------------------------------------

class DataArrayPlot(pg.PlotWidget):
    """
    A custom PyQtGraph PlotWidget.
    """
    
    def __init__(self, parent=None, plotItem=None) -> None:
        super(DataArrayPlot, self).__init__(parent, plotItem)

# ----------------------------------------------------------------------------------