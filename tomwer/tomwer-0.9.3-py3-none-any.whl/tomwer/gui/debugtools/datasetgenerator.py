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
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.blissscan import BlissScan


class DatasetGeneratorDialog(qt.QDialog):

    sigGenerationStarted = qt.Signal()
    """signal emitted when the generation is started"""

    sigGenerationStopped = qt.Signal()
    """signal emitted when the generation is stopped"""

    sigCreateOne = qt.Signal()
    """signal emitted when user ask to create one dataset"""

    def __init__(self, parent=None):
        qt.QDialog.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        self.mainWidget = DatasetGeneratorConfig(parent=self)
        self.layout().addWidget(self.mainWidget)

        # add a spacer for style
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        self._loopControlPB = qt.QPushButton("start creation in loop", self)
        self._loopControlPB.setCheckable(True)
        self._loopControlPB.setCheckable(True)
        self._createOnePB = qt.QPushButton("create one", self)

        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.addButton(self._loopControlPB, qt.QDialogButtonBox.ActionRole)
        self._buttons.addButton(self._createOnePB, qt.QDialogButtonBox.ActionRole)
        self.layout().addWidget(self._buttons)

        # expose API
        self.getTimeout = self.mainWidget.getTimeout
        self.getTypeToGenerate = self.mainWidget.getTypeToGenerate
        self.getRootDir = self.mainWidget.getRootDir
        self.getNProj = self.mainWidget.getNProj
        self.getFrameDims = self.mainWidget.getFrameDims
        self.isDarkNeededAtBeginning = self.mainWidget.isDarkNeededAtBeginning
        self.isFlatNeededAtBeginning = self.mainWidget.isFlatNeededAtBeginning
        self.sigConfigChanged = self.mainWidget.sigConfigChanged
        # connect signal / slot
        self._loopControlPB.clicked.connect(self._updateControlPB)
        self._createOnePB.clicked.connect(self._creationOneDatasetReq)

    def _updateControlPB(self, *args, **kwargs):
        if self._loopControlPB.isChecked():
            self._loopControlPB.setText("stop creation in loop")
            self.sigGenerationStarted.emit()
        else:
            self._loopControlPB.setText("start creation in loop")
            self.sigGenerationStopped.emit()

    def _creationOneDatasetReq(self):
        self.sigCreateOne.emit()

    def getConfiguration(self):
        return self.mainWidget.getConfiguration()

    def setConfiguration(self, config):
        return self.mainWidget.setConfiguration(config)


class DatasetGeneratorConfig(qt.QWidget):
    """
    Interface to define the type of dataset we want to generate
    """

    sigConfigChanged = qt.Signal()
    """Signal emitted when the configuration changed"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        # class type to generate
        self._typeCB = qt.QComboBox(self)
        for _typeClass in (
            EDFTomoScan,
            HDF5TomoScan,
            BlissScan,
        ):
            self._typeCB.addItem(_typeClass.__name__)
        self.layout().addWidget(qt.QLabel("type", self), 0, 0, 1, 1)
        self.layout().addWidget(self._typeCB, 0, 1, 1, 2)
        txt_index = self._typeCB.findText(HDF5TomoScan.__name__)
        self._typeCB.setCurrentIndex(txt_index)

        # generation timeout
        self.layout().addWidget(qt.QLabel("generate each", self), 1, 0, 1, 1)
        self._timeoutLE = qt.QDoubleSpinBox(self)
        self._timeoutLE.setValue(5)
        self._timeoutLE.setRange(0.0002, 9999999999999)
        self._timeoutLE.setSuffix("s")
        self.layout().addWidget(self._timeoutLE, 1, 1, 1, 2)

        # root folder
        self.layout().addWidget(qt.QLabel("root folder", self), 2, 0, 1, 1)
        self._rootFolderLE = qt.QLineEdit("/tmp", self)
        self.layout().addWidget(self._rootFolderLE, 2, 1, 1, 1)
        self._selectRootDirPB = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectRootDirPB, 2, 2, 1, 1)

        # number of projections to include
        self.layout().addWidget(qt.QLabel("number of projections", self), 3, 0, 1, 1)
        self._nbProjQSB = qt.QSpinBox(self)
        self._nbProjQSB.setRange(0, 10000)
        self._nbProjQSB.setValue(120)
        self.layout().addWidget(self._nbProjQSB, 3, 1, 1, 2)

        # frame size
        self.layout().addWidget(qt.QLabel("frame dimension:", self), 4, 0, 1, 1)
        self._dimXQSB = qt.QSpinBox(self)
        self._dimXQSB.setRange(1, 4096)
        self._dimXQSB.setValue(128)
        self._dimXQSB.setPrefix("width:")
        self.layout().addWidget(self._dimXQSB, 4, 1, 1, 1)
        self._dimYQSB = qt.QSpinBox(self)
        self._dimYQSB.setRange(1, 4096)
        self._dimYQSB.setValue(128)
        self._dimYQSB.setPrefix("height:")
        self.layout().addWidget(self._dimYQSB, 4, 2, 1, 1)

        # dark option
        self._darkQCB = qt.QCheckBox("darks at the beginning", self)
        self._darkQCB.setChecked(True)
        self.layout().addWidget(self._darkQCB, 5, 0, 1, 3)

        # flat option
        self._flatQCB = qt.QCheckBox("flats at the beginning", self)
        self._flatQCB.setChecked(True)
        self.layout().addWidget(self._flatQCB, 6, 0, 1, 3)

        # connect signal / slot
        self._selectRootDirPB.released.connect(self._selectRootFolder)
        self._typeCB.currentIndexChanged.connect(self._signalUpdated)
        self._timeoutLE.valueChanged.connect(self._signalUpdated)
        self._rootFolderLE.editingFinished.connect(self._signalUpdated)
        self._darkQCB.toggled.connect(self._signalUpdated)
        self._flatQCB.toggled.connect(self._signalUpdated)
        self._dimXQSB.valueChanged.connect(self._signalUpdated)
        self._dimYQSB.valueChanged.connect(self._signalUpdated)

    def _signalUpdated(self, *args, **kwargs):
        self.sigConfigChanged.emit()

    def _selectRootFolder(self):
        defaultDirectory = self._outputQLE.text()
        dialog = qt.QFileDialog(self, directory=defaultDirectory)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_():
            dialog.close()
            return

        if len(dialog.selectedFiles()) > 0:
            self._selectRootDirPB.setText(dialog.selectedFiles()[0])

    def getTimeout(self, unit: str = "s"):
        if unit == "ms":
            return self._timeoutLE.value()
        elif unit == "s":
            return self._timeoutLE.value() * 1000
        else:
            raise ValueError("unit should be 's' or 'ms'")

    def setTimeout(self, timeout):
        self._timeoutLE.setValue(timeout)

    def getTypeToGenerate(self):
        return self._typeCB.currentText()

    def setTypeToGenerate(self, type_):
        idx = self._typeCB.findText(type_)
        if idx >= 0:
            self._typeCB.setCurrentIndex(idx)

    def getRootDir(self):
        return self._rootFolderLE.text()

    def setRootDir(self, root_dir):
        self._rootFolderLE.setText(root_dir)

    def getNProj(self):
        return self._nbProjQSB.value()

    def setNProj(self, n):
        self._nbProjQSB.setValue(int(n))

    def isDarkNeededAtBeginning(self):
        return self._darkQCB.isChecked()

    def setDarkNeededAtBeginning(self, value):
        self._darkQCB.setChecked(value)

    def isFlatNeededAtBeginning(self):
        return self._flatQCB.isChecked()

    def setFlatNeededAtBeginning(self, value):
        self._flatQCB.setChecked(value)

    def getFrameDims(self):
        """

        :return: (frame width, frame height)
        """
        return self._dimXQSB.value(), self._dimYQSB.value()

    def setFrameDims(self, dims):
        assert len(dims) == 2, "expected two dimensions"
        self._dimXQSB.setValue(int(dims[0]))
        self._dimYQSB.setValue(int(dims[1]))

    def getConfiguration(self) -> dict:
        return {
            "scan_type": self.getTypeToGenerate(),
            "loop_timeout": self.getTimeout("ms"),
            "root_folder": self.getRootDir(),
            "n_proj": self.getNProj(),
            "frame_dimension": self.getFrameDims(),
            "dark_at_beginning": self.isDarkNeededAtBeginning(),
            "flat_at_beginning": self.isFlatNeededAtBeginning(),
        }

    def setConfiguration(self, config: dict):
        old = self.blockSignals(True)
        if "scan_type" in config:
            self.setTypeToGenerate(config["scan_type"])
        if "loop_timeout" in config:
            self.setTimeout(config["loop_timeout"])
        if "root_folder" in config:
            self.setRootDir(config["root_folder"])
        if "n_proj" in config:
            self.setNProj(config["n_proj"])
        if "frame_dimension" in config:
            self.setFrameDims(config["frame_dimension"])
        if "dark_at_beginning" in config:
            self.setDarkNeededAtBeginning(config["dark_at_beginning"])
        if "flat_at_beginning" in config:
            self.setFlatNeededAtBeginning(config["flat_at_beginning"])
        self.blockSignals(old)


if __name__ == "__main__":
    app = qt.QApplication([])
    dialog = DatasetGeneratorDialog(parent=None)
    dialog.show()
    app.exec_()
