# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""
contains gui relative to semi-automatic axis calculation
"""


__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "05/02/2021"


from silx.gui import qt
from tomoscan.unitsystem import metricsystem
from collections.abc import Iterable


class DimensionWidget(qt.QGroupBox):
    """
    Simple widget to display value over 3 dimensions

    :param parent:
    :param str title: QGroupBox title
    :param dims_name: name of the dimension. If set will be store in each
                      QDoubleLine prefix
    :type dims_name: tuple
    :param dims_colors: color associated to the three dimensions if any
    :type dims_colors: tuple
    """

    valuesChanged = qt.Signal()
    """Signal emitted when a value change"""

    def __init__(
        self, parent=None, title=None, dims_name=None, dims_colors=None, title_size=10
    ):
        qt.QGroupBox.__init__(self, parent)
        self.setFont(qt.QFont("Arial", title_size))
        assert title is not None
        assert dims_name is None or (
            isinstance(dims_name, Iterable) and len(dims_name) == 3
        )
        assert dims_colors is None or (
            isinstance(dims_colors, Iterable) and len(dims_colors) == 3
        )
        self._dim0Value = 1.0 * metricsystem.millimeter.value
        self._dim1Value = 1.0 * metricsystem.millimeter.value
        self._dim2Value = 1.0 * metricsystem.millimeter.value
        self._displayUnit = metricsystem.MetricSystem.MILLIMETER
        # defined unit to display values. Always stored in m (International
        # System)
        ## set GUI
        self.setTitle(title)
        self.setLayout(qt.QHBoxLayout())
        # dim 0
        self._dim0ValueQLE = qt.QDoubleSpinBox(self)
        if dims_name is not None:
            self._dim0ValueQLE.setPrefix(dims_name[0])
        self._dim0ValueQLE.setRange(0, 999999999999)
        self._dim0ValueQLE.setDecimals(10)
        self._dim0ValueQLE.setSingleStep(0.0001)
        self._dim0ValueQLE.setValue(self._getDim0DisplayValue())
        if dims_colors is not None:
            stylesheet = "background-color: {}".format(dims_colors[0])
            self._dim0ValueQLE.setStyleSheet(stylesheet)
        self.layout().addWidget(self._dim0ValueQLE)
        # dim 1
        self._dim1ValueQLE = qt.QDoubleSpinBox(self)
        if dims_name is not None:
            self._dim1ValueQLE.setPrefix(dims_name[1])
        self._dim1ValueQLE.setRange(0, 999999999999)
        self._dim1ValueQLE.setDecimals(10)
        self._dim1ValueQLE.setSingleStep(0.0001)
        self._dim1ValueQLE.setValue(self._getDim1DisplayValue())
        if dims_colors is not None:
            stylesheet = "background-color: {}".format(dims_colors[1])
            self._dim1ValueQLE.setStyleSheet(stylesheet)
        self.layout().addWidget(self._dim1ValueQLE)
        # dim 2
        self._dim2ValueQLE = qt.QDoubleSpinBox(self)
        if dims_name is not None:
            self._dim2ValueQLE.setPrefix(dims_name[2])
        self._dim2ValueQLE.setRange(0, 999999999999)
        self._dim2ValueQLE.setDecimals(10)
        self._dim2ValueQLE.setSingleStep(0.0001)
        self._dim2ValueQLE.setValue(self._getDim2DisplayValue())
        if dims_colors is not None:
            stylesheet = "background-color: {}".format(dims_colors[2])
            self._dim2ValueQLE.setStyleSheet(stylesheet)
        self.layout().addWidget(self._dim2ValueQLE)

        # set up
        self.setUnit(self._displayUnit)

        # connect signal / slot
        self._dim0ValueQLE.editingFinished.connect(self._userSetDim0)
        self._dim1ValueQLE.editingFinished.connect(self._userSetDim1)
        self._dim2ValueQLE.editingFinished.connect(self._userSetDim2)

    def _getDim0DisplayValue(self) -> float:
        return self._dim0Value / self._displayUnit.value

    def _getDim1DisplayValue(self) -> float:
        return self._dim1Value / self._displayUnit.value

    def _getDim2DisplayValue(self) -> float:
        return self._dim2Value / self._displayUnit.value

    def setUnit(self, unit):
        """
        define with which unit we should display the size
        :param unit: metric to be used for display. Internally this is always
                     stored using the international metric system
        """
        self._displayUnit = metricsystem.MetricSystem.from_value(unit)
        for widget in (self._dim0ValueQLE, self._dim1ValueQLE, self._dim2ValueQLE):
            widget.setSuffix(str(self.unit()))
        # update displayed values
        old = self.blockSignals(True)
        self._dim0ValueQLE.setValue(self._getDim0DisplayValue())
        self._dim1ValueQLE.setValue(self._getDim1DisplayValue())
        self._dim2ValueQLE.setValue(self._getDim2DisplayValue())
        self.blockSignals(old)

    def unit(self) -> metricsystem.MetricSystem:
        """

        :return: metric system used for display
        :rtype: metricsystem.MetricSystem
        """
        return self._displayUnit

    def setValues(self, dim0, dim1, dim2, unit="mm") -> None:
        """

        :param float dim0: value to dim0
        :param float dim1: value to dim1
        :param float dim2: value to dim2
        :param Union[str,MetricSystem] unit: unit used for the provided values
        :return:
        """
        old = self.blockSignals(True)
        self.setDim0value(value=dim0, unit=unit)
        self.setDim1value(value=dim1, unit=unit)
        self.setDim2value(value=dim2, unit=unit)
        self.blockSignals(old)
        self.valuesChanged.emit()

    def getValues(self) -> tuple:
        """

        :return: (dim0 value, dim1 value, dim2 value, unit)
        :rtype: tuple
        """
        return (
            self.getDim0Value()[0],
            self.getDim1Value()[0],
            self.getDim2Value()[0],
            metricsystem.MetricSystem.METER,
        )

    def getDim0Value(self) -> tuple:
        """Return Dim 0 value and unit. Unit is always metter"""
        return self._dim0Value, metricsystem.MetricSystem.METER

    def setDim0value(self, value, unit="mm"):
        """

        :param value: value to set to dim 0.
        :param Union[str,MetricSystem] unit:
        :return:
        """
        self._dim0Value = value * metricsystem.MetricSystem.from_value(unit).value
        old = self.blockSignals(True)
        self._dim0ValueQLE.setValue(self._dim0Value)
        self.blockSignals(old)
        self.valuesChanged.emit()

    def getDim1Value(self) -> tuple:
        """Return Dim 0 value and unit. Unit is always metter"""
        return self._dim1Value, metricsystem.MetricSystem.METER

    def setDim1value(self, value, unit="mm"):
        """

        :param value: value to set to dim 1.
        :param Union[str,MetricSystem] unit:
        :return:
        """
        self._dim1Value = value * metricsystem.MetricSystem.from_value(unit).value
        old = self.blockSignals(True)
        self._dim1ValueQLE.setValue(self._dim1Value)
        self.blockSignals(old)
        self.valuesChanged.emit()

    def getDim2Value(self) -> tuple:
        """Return Dim 0 value and unit. Unit is always metter"""
        return self._dim2Value, metricsystem.MetricSystem.METER

    def setDim2value(self, value, unit="mm"):
        """

        :param value: value to set to dim 2.
        :param Union[str,MetricSystem] unit:
        :return:
        """
        self._dim2Value = value * metricsystem.MetricSystem.from_value(unit).value
        old = self.blockSignals(True)
        self._dim2ValueQLE.setValue(self._dim2Value)
        self.blockSignals(old)
        self.valuesChanged.emit()

    def _valuesChanged(self, *args, **kwargs):
        self.valuesChanged.emit()

    def _userSetDim0(self):
        """callback when the user modify the dim 0 QDSP"""
        old = self.blockSignals(True)
        self._dim0Value = self._dim0ValueQLE.value() * self.unit().value
        self.blockSignals(old)
        self.valuesChanged.emit()

    def _userSetDim1(self):
        """callback when the user modify the dim 1 QDSP"""
        old = self.blockSignals(True)
        self._dim1Value = self._dim1ValueQLE.value() * self.unit().value
        self.blockSignals(old)
        self.valuesChanged.emit()

    def _userSetDim2(self):
        """callback when the user modify the dim 2 QDSP"""
        old = self.blockSignals(True)
        self._dim2Value = self._dim2ValueQLE.value() * self.unit().value
        self.blockSignals(old)
        self.valuesChanged.emit()
