"""
Contains overridden UI widget classes from PyQtGraph.
"""

# ----------------------------------------------------------------------------------

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
    A custom PyQtGraph ImageView widget. Only displays 2D images, so all slice 
    controls (switching slice/direction) are handled externally.
    """
    
    def __init__(self, parent=None) -> None:
        super(DataArrayImageView, self).__init__(
            parent, 
            view=pg.PlotItem(),
            imageItem=pg.ImageItem()
        )

        # Removes out default ImageView features
        self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()

        # Aspect/range settings
        self.view.setAspectLocked(lock=False)
        self.view.enableAutoRange()

    # ------------------------------------------------------------------------------

    def set_data_array(self, data_array: xr.DataArray) -> None:
        """
        Sets image, axis labels, axis coordinates for ImageView.

        Parameters:
            data_array (xr.DataArray): 2D DataArray with data, coords, and dims
        """

        # Adds matplotlib colormap to image
        image = self._set_color_map(data_array.values)

        # Sets plot labels
        self.view.setLabels(
            bottom = data_array.dims[0],
            left = data_array.dims[1]
        )

        # Retrieves axis starting positions and scaling
        pos, scale = self._get_axis_coords(data_array)

        # Adds image to ImageView with proper axes
        self.setImage(image, pos=pos, scale=scale)

    # ------------------------------------------------------------------------------

    def _set_color_map(self, image: np.ndarray) -> np.ndarray:
        """
        Adds colormap to an image. Currently only supports matplotlib "jet" in
        logarithmic scale.

        Parameters:
            image (np.ndarray): NumPy array to map

        Returns:
            color_image (np.ndarray): NumPy array with color mapping
        """

        # Max pixel value in image
        image_max = np.amax(image)

        # Normalizer
        norm = colors.LogNorm(vmax=image_max)

        # Normalized image
        normalized_image = norm(image)

        # Normalized image with colormap
        color_image = plt.cm.jet(normalized_image)

        return color_image

    # ------------------------------------------------------------------------------

    def _get_axis_coords(self, data_array: xr.DataArray):
        """
        Retrieves axis starting points and scaling for image.

        Parameters:
            data_array (xr.DataArray): 2D DataArray with data, coords, and dims

        Returns:
            x (float): starting x point
            y (float): starting y point
            x_scale (float): space between x points
            y_scale (float): space between y points
        """

        def _is_monotonic(values: list) -> bool:
            """
            Checks list for monoticity.
            """
            # Differentiated list
            dx = np.diff(values)

            return np.all(dx <= 0) or np.all(dx >= 0)

        def _set_rect_values(values: list):
            """
            Selects starting point and scale based on list item type and monoticity.
            """

            if type(values[0]) == str or not _is_monotonic(values):
                start = 0
                scale = 1
            else:
                start = values[0]
                scale = values[1] - values[0]

            return start, scale
        
        # NumPy arrays of values from DataArray
        x_values = data_array.coords[data_array.dims[0]].values
        y_values = data_array.coords[data_array.dims[1]].values

        x, x_scale = _set_rect_values(x_values)
        y, y_scale = _set_rect_values(y_values)

        return (x, y), (x_scale, y_scale)

# ----------------------------------------------------------------------------------

class DataArrayPlot(pg.PlotWidget):
    """
    A custom PyQtGraph PlotWidget.
    """
    
    def __init__(self, parent=None, plotItem=None) -> None:
        super(DataArrayPlot, self).__init__(parent, plotItem)

# ----------------------------------------------------------------------------------