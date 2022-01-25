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
__date__ = "16/11/2020"


from silx.gui import qt
from orangewidget import gui

import tomwer.core.process.control.volumesymlink
from tomwer.web.client import OWClient
from orangewidget.settings import Setting
from orangewidget.widget import Output, Input
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.process.control.volumesymlink import (
    OutputType,
    VolumeSymbolicLinkProcess,
)
from orangecontrib.tomwer.orange.managedprocess import SuperviseOW
from processview.core.manager import ProcessManager, DatasetState
import logging

_logger = logging.getLogger(__name__)


class VolumeSymLinkOW(SuperviseOW, OWClient):
    """
    link volume reconstructed at proposal file if possible else under
    the given folder
    """

    name = "volume symbolic link"
    id = "orange.widgets.tomwer.control.VolumeSymLinkOW.VolumeSymLinkOW"
    description = (
        "create a symbolic link for the latest volume reconstructed on a "
        "given folder"
    )
    icon = "icons/volumesymlink.svg"
    priority = 200
    keywords = [
        "hdf5",
        "tomwer",
        "folder",
        "volume",
        "symlink",
        "tomography",
        "symbolic link",
    ]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    ewokstaskclass = tomwer.core.process.control.volumesymlink.VolumeSymbolicLinkProcess

    _scans = Setting(list())

    class Inputs:
        data = Input(name="data", type=TomwerScanBase, doc="scan to be process")

    class Outputs:
        data = Output(name="data", type=TomwerScanBase, doc="one scan to be process")

    def __init__(self, parent=None):
        SuperviseOW.__init__(self, parent)
        OWClient.__init__(self)
        self._mainWidget = _OutputDir(parent=self)
        layout = gui.vBox(self.mainArea, self.name).layout()
        layout.addWidget(self._mainWidget)

    @Inputs.data
    def process(self, scan):
        if scan is None:
            return
        symlink_process = VolumeSymbolicLinkProcess()
        symlink_process.set_configuration(
            {
                "output_type": self._mainWidget.getOutputType(),
                "output_folder": self._mainWidget.getOutputFolder(),
            }
        )
        ProcessManager().notify_dataset_state(
            dataset=self.scan,
            process=self,
            state=DatasetState.ON_GOING,
        )
        try:
            scan = symlink_process.process(scan=scan)
        except Exception:
            mess = "Failed to create symbolic link for {}".format(str(scan))
            _logger.processFailed(mess)
            ProcessManager().notify_dataset_state(
                dataset=self.scan, process=self, state=DatasetState.FAILED, details=mess
            )
        else:
            mess = "Create symbolic link for {}".format(str(scan))
            _logger.processSucceed(mess)
            ProcessManager().notify_dataset_state(
                dataset=self.scan,
                process=self,
                state=DatasetState.SUCCEED,
                details=mess,
            )
        self.Outputs.data.send(scan)

    def reprocess(self, dataset):
        self.process(dataset)


class _OutputDir(qt.QGroupBox):
    def __init__(self, parent):
        qt.QGroupBox.__init__(self, parent)
        self._button_grp = qt.QButtonGroup(self)
        self._button_grp.setExclusive(True)
        self.setLayout(qt.QGridLayout())
        self._oneLevelCB = qt.QRadioButton(OutputType.ONE_LEVEL_UPPER.value, self)
        self._button_grp.addButton(self._oneLevelCB)
        self.layout().addWidget(self._oneLevelCB, 1, 0, 1, 3)
        self._staticOpt = qt.QRadioButton("", self)
        self._button_grp.addButton(self._staticOpt)
        self.layout().addWidget(self._staticOpt, 2, 0, 1, 1)
        self._qleFolder = qt.QLineEdit("", self)
        self.layout().addWidget(self._qleFolder, 2, 1, 1, 1)
        self._selectPB = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectPB, 2, 2, 1, 1)

        # connect signal / slot
        self._selectPB.released.connect(self._selectFolder)
        self._qleFolder.editingFinished.connect(self._activeStaticOpt)

        # set up
        self._oneLevelCB.setChecked(True)

    def _activeStaticOpt(self, *args, **kwargs):
        self._staticOpt.setChecked(True)

    def _selectFolder(self):
        dialog = qt.QFileDialog(self)
        dialog.setWindowTitle("Select destination folder for symbolic link")
        dialog.setModal(1)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_():
            dialog.close()
            return None

        dest_folder = dialog.selectedFiles()[0]
        self._qleFolder.setText(dest_folder)

    def getOutputType(self) -> OutputType:
        if self._oneLevelCB.isChecked():
            return OutputType.ONE_LEVEL_UPPER
        elif self._staticOpt.isChecked():
            return OutputType.STATIC
        else:
            raise TypeError("Not managed")

    def getOutputFolder(self):
        return self._qleFolder.text()
