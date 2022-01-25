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

__authors__ = ["C. Nemoz", "H. Payno"]
__license__ = "MIT"
__date__ = "18/02/2018"


from silx.gui import qt

from tomwer.core.process.control.datawatcher.datawatcher import _DataWatcher
from tomwer.core.process.control.datawatcher import status


class _DWConfigurationWidget(qt.QWidget):

    startByOldestStateChanged = qt.Signal(bool)

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self._observationMethod = _ObservationMethodSelector(parent=self)
        self.layout().addWidget(self._observationMethod)

        # checkbox start scan from oldest
        self._qcboldest = qt.QCheckBox("Start scan by the oldest", parent=self)
        tooltip = (
            "If NOT activated will explore folders from the latest to "
            "the newest. Otherwise will explore the folders from the "
            "newest to the oldest."
        )
        self._qcboldest.setToolTip(tooltip)
        self.startByOldestStateChanged = self._qcboldest.toggled
        self.layout().addWidget(self._qcboldest)


class _ObservationMethodSelector(qt.QGroupBox):
    """Group box allowing selection of an observation method"""

    sigSelectionChanged = qt.Signal(tuple)
    """Return the selection made as a string and some information if needed in
    a dictionary"""

    def __init__(self, parent):
        qt.QGroupBox.__init__(
            self, parent, title="End acquisition observation method for edf"
        )
        self.setLayout(qt.QVBoxLayout())

        self._qrbXml = qt.QRadioButton(status.DET_END_XML, parent=self)
        self.layout().addWidget(self._qrbXml)
        self._qrbInfo = qt.QRadioButton(status.PARSE_INFO_FILE, parent=self)
        self.layout().addWidget(self._qrbInfo)

        self._qwUserEntry = qt.QWidget(parent=self)
        self.layout().addWidget(self._qwUserEntry)
        self._qrbUserEntry = qt.QRadioButton(status.DET_END_USER_ENTRY, parent=self)
        self.layout().addWidget(self._qrbUserEntry)

        widgetFilePtrn = qt.QWidget(parent=self)
        widgetFilePtrn.setLayout(qt.QHBoxLayout())

        widgetFilePtrn.layout().addWidget(
            qt.QLabel(text="pattern: ", parent=widgetFilePtrn)
        )
        self._qleFilePattern = qt.QLineEdit(text="", parent=self._qwUserEntry)
        widgetFilePtrn.layout().addWidget(self._qleFilePattern)
        self.widgetFilePtrn = widgetFilePtrn
        self.layout().addWidget(self.widgetFilePtrn)

        self._qrbXml.setChecked(_DataWatcher.DEFAULT_OBS_METH == status.DET_END_XML)
        self._qrbInfo.setChecked(
            _DataWatcher.DEFAULT_OBS_METH == status.PARSE_INFO_FILE
        )
        self._qrbUserEntry.setChecked(
            _DataWatcher.DEFAULT_OBS_METH == status.DET_END_USER_ENTRY
        )

        self.widgetFilePtrn.setVisible(self._qrbUserEntry.isVisible())

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        # deal with connections
        self._qrbUserEntry.toggled.connect(self.widgetFilePtrn.setVisible)
        self._qrbXml.toggled.connect(self._selectionChanged)
        self._qrbInfo.toggled.connect(self._selectionChanged)
        self._qrbUserEntry.toggled.connect(self._selectionChanged)
        self._qleFilePattern.editingFinished.connect(self._selectionChanged)

        # add some tooltips
        t = """If a file with this pattern is found in the [scan] folder then
            we will consider the acquisition as ended"""
        self._qrbUserEntry.setToolTip(t)

        t = """Wild charracter allowed"""
        self._qleFilePattern.setToolTip(t)

        t = """If we founf the [scan].xml in the [scan] folder then
            we will consider the acquisition ended"""
        self._qrbXml.setToolTip(t)

        t = """We will look for the [scan].info file in the [scan]
            directory. If it exists then we will parse it to get the number of
            .edf file we should have and wait for all of them to be acquired
            (also checking file size)"""
        self._qrbInfo.setToolTip(t)

    def _selectionChanged(self):
        if self._qrbXml.isChecked():
            self.sigSelectionChanged.emit((status.DET_END_XML,))
        elif self._qrbInfo.isChecked():
            self.sigSelectionChanged.emit((status.PARSE_INFO_FILE,))
        else:
            self.sigSelectionChanged.emit(
                (status.DET_END_USER_ENTRY, {"pattern": self._qleFilePattern.text()})
            )
