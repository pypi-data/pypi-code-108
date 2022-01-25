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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "16/04/2021"

from silx.gui import qt


class _IgnoreWheelBase:
    """QWidget giving priority to the scrollArea containing it"""

    def __init__(self, scrollArea):
        self._scrollArea = scrollArea

    def wheelEvent(self, *args, **kwargs):
        if self._scrollArea is not None:
            self._scrollArea.wheelEvent(*args, **kwargs)


class QComboBoxIgnoreWheel(qt.QComboBox, _IgnoreWheelBase):
    """Combobox which give priority to the scrollArea containing it"""

    def __init__(self, parent, scrollArea):
        qt.QComboBox.__init__(self, parent, scrollArea=scrollArea)
        _IgnoreWheelBase.__init__(self, scrollArea)

    def wheelEvent(self, *args, **kwargs):
        # Note: we are enforce to duplicate this due to an error on pyqt side.
        self._scrollArea.wheelEvent(*args, **kwargs)


class QDoubleSpinBoxIgnoreWheel(qt.QDoubleSpinBox):
    def __init__(self, parent, scrollArea):
        qt.QDoubleSpinBox.__init__(self, parent)
        _IgnoreWheelBase.__init__(self, scrollArea)

    def wheelEvent(self, *args, **kwargs):
        # Note: we are enforce to duplicate this due to an error on pyqt side.
        self._scrollArea.wheelEvent(*args, **kwargs)


class QSpinBoxIgnoreWheel(qt.QSpinBox, _IgnoreWheelBase):
    def __init__(self, parent, scrollArea):
        qt.QSpinBox.__init__(self, parent, scrollArea=scrollArea)
        _IgnoreWheelBase.__init__(self, scrollArea)

    def wheelEvent(self, *args, **kwargs):
        # Note: we are enforce to duplicate this due to an error on pyqt side.
        self._scrollArea.wheelEvent(*args, **kwargs)
