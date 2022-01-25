# coding: utf-8
# /*##########################################################################
# Copyright (C) 2017 European Synchrotron Radiation Facility
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
#############################################################################*/

"""
This module is used to define the process of the reference creator.
This is related to the issue #184
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "21/09/2018"


from silx.gui import qt
from tomoscan.unitsystem import metricsystem
import logging

_logger = logging.getLogger(__name__)


class MetricEntry(qt.QWidget):
    """
    Create a simple line with a name, a QLineEdit and a combobox to define the
    unit in order to define a metric value.

    :param str name: name of the metric value to define
    :param str: base_unit. Default way to present a value when setted
    """

    _CONVERSION = {
        "nm": metricsystem.nanometer.value,
        "mm": metricsystem.millimeter.value,
        "cm": metricsystem.centimeter.value,
        "m": metricsystem.meter.value,
    }

    def __init__(self, name, default_unit="m", parent=None):
        qt.QWidget.__init__(self, parent)
        assert type(default_unit) is str
        assert default_unit in ("nm", "mm", "cm", "m")
        self._base_unit = default_unit

        self.setLayout(qt.QHBoxLayout())
        self._label = qt.QLabel(name, parent=self)
        self.layout().addWidget(self._label)
        self._qlePixelSize = qt.QLineEdit("0.0", parent=self)
        self._qlePixelSize.setValidator(qt.QDoubleValidator(self._qlePixelSize))
        self.layout().addWidget(self._qlePixelSize)

        self._qcbUnit = qt.QComboBox(parent=self)
        self._qcbUnit.addItem("nm")
        self._qcbUnit.addItem("mm")
        self._qcbUnit.addItem("cm")
        self._qcbUnit.addItem("m")
        self.layout().addWidget(self._qcbUnit)
        self._resetBaseUnit()

    def getCurrentUnit(self):
        assert self._qcbUnit.currentText() in self._CONVERSION
        return self._CONVERSION[self._qcbUnit.currentText()]

    def setValue(self, value):
        """

        :param float value: pixel size in international metric system (meter)
        """
        _value = value
        if type(_value) is str:
            try:
                _value = float(_value)
            except Exception as error:
                raise ValueError("Given string does not represent a float", error)
                return
        assert isinstance(_value, float)
        self._qlePixelSize.setText(str(_value))
        self._resetBaseUnit()

    def _resetBaseUnit(self):
        """Simple reset of the combobox according to the base_unit"""
        index = self._qcbUnit.findText(self._base_unit)
        if index is None:
            raise ValueError("unrecognized base unit")
        else:
            self._qcbUnit.setCurrentIndex(index)

    def getValue(self):
        """

        :return: the value in meter
        :rtype: float
        """
        return float(self._qlePixelSize.text()) * self.getCurrentUnit()


class CentimeterEntry(MetricEntry):
    """
    Define a QlineEdit which will set and get metric values in centimeter
    """

    def __init__(self, name, default_unit="cm", parent=None):
        MetricEntry.__init__(self, name, default_unit=default_unit, parent=parent)

    def setValue(self, value):
        """

        :param float value: pixel size in centimeter
        """
        _value = value
        if type(_value) is str:
            try:
                _value = float(_value)
            except Exception as error:
                raise ValueError("Given string does not represent a float", error)
        _value = _value * metricsystem.centimeter
        MetricEntry.setValue(self, _value)

    def getValue(self):
        """

        :return: the value in meter
        :rtype: float
        """
        value = MetricEntry.getValue(self)
        return value / metricsystem.centimeter
