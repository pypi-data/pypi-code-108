"""
Controls DataArray slice in ImageView.
"""

# ----------------------------------------------------------------------------------

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore
import xarray as xr

# ----------------------------------------------------------------------------------

AXES = ["x", "y", "z1", "z2"]

# ----------------------------------------------------------------------------------

class DataArrayController(QtGui.QWidget):
    """
    Controls DataArray slice in ImageView.
    """

    def __init__(self, data_array: xr.DataArray, parent=None) -> None:
        super(DataArrayController, self).__init__(parent)

        self.parent = parent
        self.data_array = data_array
        
        # Custom layout
        self.layout = DataArrayControllerLayout(data_array, parent=self)
        self.setLayout(self.layout)

        # Component lists from layout
        self.lbl_list = self.layout.lbl_list
        self.axis_cbx_list = self.layout.axis_cbx_list
        self.value_slider_list = self.layout.value_slider_list
        self.value_cbx_list = self.layout.value_cbx_list

        self._update_value()
        self._update_axes()

    # ------------------------------------------------------------------------------

    def _update_value(self) -> None:
        """
        Updates value for axis when changed by a slider or combobox.
        """
        
        if isinstance(self.sender(), QtGui.QSlider):
            dim = self.value_slider_list.index(self.sender())
            value_index = self.sender().value()
            self.value_cbx_list[dim].setCurrentIndex(value_index)

        if isinstance(self.sender(), QtGui.QComboBox):
            dim = self.value_cbx_list.index(self.sender())
            value_index = self.sender().currentIndex()
            self.value_slider_list[dim].setValue(value_index)

        self._update_image_view()

    # ------------------------------------------------------------------------------

    def _update_axes(self) -> None:
        """
        Updates axis order to determine which slice is in view
        """

        # After initial update (after controller is created)
        if not self.sender() is None:
            # Changed axis
            new_axis = self.sender().currentIndex()

            # All axes
            axes = [i for i in range(self.data_array.ndim)]

            # Axes after initial change
            curr_axes = [cbx.currentIndex() for cbx in self.axis_cbx_list]
            
            # Axis that is not in curr_axes
            try:
                axis_to_add = list(set(axes) - set(curr_axes))[0]
            except:
                pass

        # Loops through axes
        for i in range(self.data_array.ndim):
            cbx = self.axis_cbx_list[i]

            # After initial update (after controller is created)
            if not self.sender() is None:
                if cbx.currentIndex() == new_axis and not cbx == self.sender():
                    cbx.setCurrentIndex(axis_to_add)

            # Enables/disables value-changing components based on axis
            if cbx.currentIndex() <= 1:
                self.value_slider_list[i].setEnabled(False)
                self.value_cbx_list[i].setEnabled(False)
            else:
                self.value_slider_list[i].setEnabled(True)
                self.value_cbx_list[i].setEnabled(True)

        self._update_image_view()

    # ------------------------------------------------------------------------------

    def _update_image_view(self) -> None:
        """
        Determines slice to display in ImageView.
        """

        str_numpy_args = ""
        transpose = False
        x_index, y_index = 0, 0

        # Loops through axes
        for i in range(self.data_array.ndim):

            # Checks is axis is enabled (not x or y)
            if self.value_slider_list[i].isEnabled():
                # Adds value index to string for NumPy args
                str_numpy_args += f"{self.value_slider_list[i].value()}"
            else:
                str_numpy_args += ":"

                # Checks for conditions to transpose
                if self.axis_cbx_list[i].currentIndex() == 0:
                    x_index = i
                else:
                    y_index = i

            # Adds commas in between args
            if i < self.data_array.ndim - 1:
                str_numpy_args += ","

        # Transposes image if y occurs before x
        if y_index < x_index:
            transpose = True
        
        # Converts a string into numpy arguments
        numpy_args = eval(f'np.s_[{str_numpy_args}]')

        # DataArray slice
        data_array_slice = self.data_array[numpy_args]

        # Checks for empty slice
        if data_array_slice.values.ndim != 0:

            # Checks for transpose
            if not transpose:
                self.parent.data_array_image_view.set_data_array(data_array_slice)
            else:
                self.parent.data_array_image_view.set_data_array(data_array_slice.T)
        
# ----------------------------------------------------------------------------------

class DataArrayControllerLayout(QtGui.QGridLayout):
    """
    Custom dynamic grid layout for controller
    """

    def __init__(self, data_array: xr.DataArray, parent=None) -> None:
        super(DataArrayControllerLayout, self).__init__(parent)

        # Lists for components
        self.lbl_list = []
        self.axis_cbx_list = []
        self.value_slider_list = []
        self.value_cbx_list = []

        # Axis labels (depends on number of dimensions in DataArray)
        axes = AXES[:data_array.ndim]

        # Loops through axes
        for i in range(data_array.ndim):
            dim_lbl = data_array.dims[i]
            dim_coords = map(str, data_array.coords[dim_lbl].values)

            # Adds new component to respective list
            self.lbl_list.append(QtGui.QLabel(dim_lbl))
            self.axis_cbx_list.append(QtGui.QComboBox())
            self.value_slider_list.append(QtGui.QSlider(QtCore.Qt.Horizontal))
            self.value_cbx_list.append(QtGui.QComboBox())

            # Adds axes and sets current axis
            self.axis_cbx_list[i].addItems(axes)
            self.axis_cbx_list[i].setCurrentIndex(i)

            # Sets max value index 
            self.value_slider_list[i].setMaximum(data_array.shape[i] - 1)

            # Adds values
            self.value_cbx_list[i].addItems(dim_coords)

            # Adds components to layout
            self.addWidget(self.lbl_list[i], i, 0)
            self.addWidget(self.axis_cbx_list[i], i, 1)
            self.addWidget(self.value_slider_list[i], i, 2, 1, 3)
            self.addWidget(self.value_cbx_list[i], i, 5)

            # Connections
            self.axis_cbx_list[i].currentIndexChanged.connect(
                parent._update_axes
            )
            self.value_slider_list[i].valueChanged.connect(
                parent._update_value
            )
            self.value_cbx_list[i].currentIndexChanged.connect(
                parent._update_value
            )

# ----------------------------------------------------------------------------------