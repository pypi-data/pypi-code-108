"""
A general tool for plotting, slicing, and analyzing xarray DataArrays.
"""

# ----------------------------------------------------------------------------------

#from iautil.utilities.ui import DataArrayImageView
import numpy as np
import pyqtgraph as pg
from pyqtgraph import dockarea, QtGui, QtCore
import sys
import xarray as xr

# ----------------------------------------------------------------------------------

__all__ = (
    "ImageTool",
    "ImageToolWidget"
)

# ----------------------------------------------------------------------------------

class ImageTool:
    """
    
    """

    app = pg.mkQApp("ImageTool")

    def __init__(self, data_array: xr.DataArray) -> None:
        self.image_tool_widget = ImageToolWidget(data_array)

    def show(self):
        self.image_tool_widget.show()
        self.app.exec_()

# ----------------------------------------------------------------------------------

class ImageToolWidget(QtGui.QWidget):
    """

    """

    def __init__(self, data_array: xr.DataArray) -> None:
        super(ImageToolWidget, self).__init__()

        self.data_array = data_array

        self.data_array_image_view = None
        self.controller_widget = None

        self.dock_area = dockarea.DockArea()
        self.data_array_image_view_dock = None
        self.controller_widget_dock = None
        
        self._create_widgets()
        self._create_docks()

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.dock_area)
        self.setLayout(self.layout)

    # ------------------------------------------------------------------------------

    def _create_widgets(self) -> None:
        """
        
        """
        from iautil.plotting.image_tool.controller import DataArrayController
        from iautil.utilities.ui import DataArrayImageView
        
        self.data_array_image_view = DataArrayImageView()
        self.controller_widget = DataArrayController(self.data_array, self)
        
    # ------------------------------------------------------------------------------
    
    def _create_docks(self) -> None:
        """
        
        """

        self.data_array_image_view_dock = dockarea.Dock(
            name="DataArray ImageView",
            size=(200, 200),
            widget=self.data_array_image_view,
            hideTitle=True
        )

        self.controller_widget_dock = dockarea.Dock(
            name="Controller",
            size=(200, 100),
            widget=self.controller_widget,
            hideTitle=True
        )

        self.dock_area.addDock(self.data_array_image_view_dock)
        self.dock_area.addDock(self.controller_widget_dock)

# ----------------------------------------------------------------------------------
