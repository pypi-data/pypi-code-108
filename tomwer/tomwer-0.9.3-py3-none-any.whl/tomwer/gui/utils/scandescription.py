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

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "04/02/2020"


from silx.gui import qt
import os


class ScanNameLabel(qt.QWidget):
    """Scan to display the scan name"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent=parent)
        self.setLayout(qt.QHBoxLayout())
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        label = qt.QLabel("scan: ", self)
        label.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.layout().addWidget(label)
        self._scanNameLabel = qt.QLabel("", self)
        self._scanNameLabel.setAlignment(qt.Qt.AlignLeft)
        self._scanNameLabel.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum
        )
        self.layout().addWidget(self._scanNameLabel)

        # set up
        self.clear()

    def setScan(self, scan):
        if scan is None or scan.path is None:
            self.clear()
        else:
            self._scanNameLabel.setText(os.path.basename(scan.path))
            self._scanNameLabel.setToolTip(scan.path)

    def clear(self):
        self._scanNameLabel.setText("-")
        self._scanNameLabel.setToolTip("")
