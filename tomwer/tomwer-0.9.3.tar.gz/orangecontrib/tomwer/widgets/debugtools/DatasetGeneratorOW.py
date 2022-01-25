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

__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "28/09/2020"

from silx.gui import qt
from orangewidget import widget, gui
from orangewidget.widget import Output
from tomwer.gui.debugtools.datasetgenerator import DatasetGeneratorDialog
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.blissscan import BlissScan
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.utils.scanutils import MockHDF5
from tomwer.core.utils.scanutils import MockBlissAcquisition
from orangewidget.settings import Setting
from silx.gui.utils import concurrent
import threading
import os
import uuid


class DatasetGeneratorOW(widget.OWBaseWidget, openclass=True):
    """
    A simple widget to generate on the fly and 'continuously' datasets
    """

    name = "random data generator"
    id = "orangecontrib.tomwer.widgets.debugtools.datasetgeneratorow"
    description = "create on the fly dataset"
    icon = "icons/hammer.png"
    priority = 250
    keywords = ["tomography", "file", "tomwer", "dataset", "debug"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    _settings = Setting(dict())

    class Outputs:
        data = Output(name="data", type=object)

    def __init__(self, parent=None):
        widget.OWBaseWidget.__init__(self, parent=parent)
        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self.generatorGUI = DatasetGeneratorDialog(parent=self)
        self._layout.addWidget(self.generatorGUI)
        self._displayTimer = qt.QTimer()

        self._loadSettings()

        # connect signal / slot
        self.generatorGUI.sigGenerationStopped.connect(self._stop)
        self.generatorGUI.sigGenerationStarted.connect(self._start)
        self.generatorGUI.sigConfigChanged.connect(self._reset)
        self.generatorGUI.sigCreateOne.connect(self._generate)
        #  connection with the interface to update settings
        self.generatorGUI.sigConfigChanged.connect(self._saveSettings)

    def _start(self):
        self._displayTimer.timeout.connect(self._generateAndRestart)
        self._displayTimer.start(self.generatorGUI.getTimeout())

    def _stop(self):
        self._displayTimer.timeout.disconnect(self._generateAndRestart)
        self._displayTimer.stop()

    def _reset(self):
        if self._displayTimer.isActive():
            self._stop()
            self._start()

    def _generateAndRestart(self):
        self._generate()
        self._displayTimer.start(self.generatorGUI.getTimeout())

    def _generate(self):
        scan_path = os.path.join(
            self.generatorGUI.getRootDir(),
            str(uuid.uuid4()).split("-")[0],
        )
        thread = _DatasetGeneratorThread()
        thread.init(
            type_to_generate=self.generatorGUI.getTypeToGenerate(),
            scan_path=scan_path,
            callback=self.Outputs.data.send,
            n_proj=self.generatorGUI.getNProj(),
            create_ini_dark=self.generatorGUI.isDarkNeededAtBeginning(),
            create_ini_flat=self.generatorGUI.isFlatNeededAtBeginning(),
            dims=self.generatorGUI.getFrameDims(),
        )
        thread.start()
        return thread

    def _loadSettings(self):
        self.generatorGUI.setConfiguration(self._settings)

    def _saveSettings(self):
        self._settings = self.generatorGUI.getConfiguration()


class _DatasetGeneratorThread(threading.Thread):
    def init(
        self,
        type_to_generate,
        scan_path,
        callback,
        n_proj,
        create_ini_dark,
        create_ini_flat,
        dims,
    ):
        self.type_to_generate = type_to_generate
        self.callback = callback
        self.scan_path = scan_path
        self.n_proj = n_proj
        self.create_ini_dark = create_ini_dark
        self.create_ini_flat = create_ini_flat
        self.dims = dims

    def run(self):
        if self.type_to_generate == EDFTomoScan.__name__:
            scan = MockEDF.mockScan(
                scanID=self.scan_path, nRadio=self.n_proj, dim=self.dims[0]
            )
        elif self.type_to_generate == HDF5TomoScan.__name__:
            scan = MockHDF5(
                scan_path=self.scan_path,
                n_proj=self.n_proj,
                n_ini_proj=self.n_proj,
                create_ini_dark=self.create_ini_dark,
                create_ini_ref=self.create_ini_flat,
                dim=self.dims[0],
            ).scan
        elif self.type_to_generate == BlissScan.__name__:
            n_darks = 10 if self.create_ini_dark else 0
            n_flats = 10 if self.create_ini_flat else 0
            mock = MockBlissAcquisition(
                n_sample=1,
                n_sequence=1,
                n_scan_per_sequence=1,
                n_darks=n_darks,
                n_flats=n_flats,
                output_dir=self.scan_path,
            )
            scan = mock.create_bliss_scan()
        else:
            raise ValueError(
                "type to generate {} not recognized".format(self.type_to_generate)
            )
        concurrent.submitToQtMainThread(self.callback, scan)
