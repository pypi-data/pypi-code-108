"""
Widget that controls the DataArray loaded into an ImageTool instance.
"""

# ----------------------------------------------------------------------------------

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore
import xarray as xr

# ----------------------------------------------------------------------------------

__all__ = (
    "DataArrayController"
)

# ----------------------------------------------------------------------------------

AXES = ["x", "y", "z", "t"]

# ----------------------------------------------------------------------------------

class DataArrayController(QtGui.QWidget):
    """
    Controller for the ImageTool DataArray.
    """

    def __init__(self, data_array: xr.DataArray, parent=None) -> None:
        super(DataArrayController, self).__init__(parent)

        self.parent = parent
        self.data_array = data_array
        
        self.layout = DataArrayControllerLayout(data_array, parent=self)
        self.setLayout(self.layout)

        self.dim_lbl_list = self.layout.dim_lbl_list
        self.dim_axis_cbx_list = self.layout.dim_axis_cbx_list
        self.dim_slider_list = self.layout.dim_slider_list
        self.dim_currval_cbx_list = self.layout.dim_currval_cbx_list

        self._update_currval()
        self._update_axes()

    # ------------------------------------------------------------------------------

    def _update_currval(self) -> None:
        """
        
        """
        
        if isinstance(self.sender(), QtGui.QSlider):
            dim = self.dim_slider_list.index(self.sender())
            currval_index = self.sender().value()
            self.dim_currval_cbx_list[dim].setCurrentIndex(currval_index)

        if isinstance(self.sender(), QtGui.QComboBox):
            dim = self.dim_currval_cbx_list.index(self.sender())
            currval_index = self.sender().currentIndex()
            self.dim_slider_list[dim].setValue(currval_index)

        self._update_image_view()

    # ------------------------------------------------------------------------------

    def _update_axes(self) -> None:
        """
        
        """

        if not self.sender() is None:
            new_axis = self.sender().currentIndex()
            axes = [i for i in range(self.data_array.ndim)]
            curr_axes = [cbx.currentIndex() for cbx in self.dim_axis_cbx_list]
            
            try:
                axis_to_add = list(set(axes) - set(curr_axes))[0]
            except:
                pass

        for i in range(self.data_array.ndim):
            cbx = self.dim_axis_cbx_list[i]

            if not self.sender() is None:
                if cbx.currentIndex() == new_axis and not cbx == self.sender():
                    cbx.setCurrentIndex(axis_to_add)

            if cbx.currentIndex() <= 1:
                self.dim_slider_list[i].setEnabled(False)
                self.dim_currval_cbx_list[i].setEnabled(False)
            else:
                self.dim_slider_list[i].setEnabled(True)
                self.dim_currval_cbx_list[i].setEnabled(True)

        self._update_image_view()

    # ------------------------------------------------------------------------------

    def _update_image_view(self) -> None:
        """
        
        """

        image_view_image = None
        str_numpy_args = ""
        transpose = False
        x_index, y_index = 0, 0

        for i in range(self.data_array.ndim):
            if self.dim_slider_list[i].isEnabled():
                str_numpy_args += f"{self.dim_slider_list[i].value()}"
            else:
                str_numpy_args += ":"
                if self.dim_axis_cbx_list[i].currentIndex() == 0:
                    x_index = i
                else:
                    y_index = i

            if i < self.data_array.ndim - 1:
                str_numpy_args += ","

        if y_index < x_index:
            transpose = True
        
        numpy_args = eval(f'np.s_[{str_numpy_args}]')
        data_array_slice = self.data_array[numpy_args]

        if data_array_slice.values.ndim != 0:
            if not transpose:
                self.parent.data_array_image_view.set_data_array(data_array_slice)
            else:
                self.parent.data_array_image_view.set_data_array(data_array_slice.T)
        
# ----------------------------------------------------------------------------------

class DataArrayControllerLayout(QtGui.QGridLayout):
    """
    
    """

    def __init__(self, data_array: xr.DataArray, parent=None) -> None:
        super(DataArrayControllerLayout, self).__init__(parent)

        self.dim_lbl_list = []
        self.dim_axis_cbx_list = []
        self.dim_slider_list = []
        self.dim_currval_cbx_list = []
        axes = AXES[:data_array.ndim]

        for i in range(data_array.ndim):
            dim_lbl = data_array.dims[i]
            dim_coords = map(str, data_array.coords[dim_lbl].values)

            self.dim_lbl_list.append(QtGui.QLabel(dim_lbl))
            self.dim_axis_cbx_list.append(QtGui.QComboBox())
            self.dim_slider_list.append(QtGui.QSlider(QtCore.Qt.Horizontal))
            self.dim_currval_cbx_list.append(QtGui.QComboBox())

            self.dim_axis_cbx_list[i].addItems(axes)
            self.dim_axis_cbx_list[i].setCurrentIndex(i)
            self.dim_slider_list[i].setMaximum(data_array.shape[i] - 1)
            self.dim_currval_cbx_list[i].addItems(dim_coords)

            self.addWidget(self.dim_lbl_list[i], i, 0)
            self.addWidget(self.dim_axis_cbx_list[i], i, 1)
            self.addWidget(self.dim_slider_list[i], i, 2, 1, 3)
            self.addWidget(self.dim_currval_cbx_list[i], i, 5)

            self.dim_axis_cbx_list[i].currentIndexChanged.connect(
                parent._update_axes
            )
            self.dim_slider_list[i].valueChanged.connect(
                parent._update_currval
            )
            self.dim_currval_cbx_list[i].currentIndexChanged.connect(
                parent._update_currval
            )

# ----------------------------------------------------------------------------------