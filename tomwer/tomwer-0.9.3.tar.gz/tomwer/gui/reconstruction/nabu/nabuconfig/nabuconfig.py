# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
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
__date__ = "11/02/2020"


from silx.gui import qt
from tomwer.gui.reconstruction.nabu.nabuconfig.preprocessing import (
    _NabuPreProcessingConfig,
)
from tomwer.gui.reconstruction.nabu.nabuconfig.phase import _NabuPhaseConfig
from tomwer.gui.reconstruction.nabu.nabuconfig.reconstruction import (
    _NabuReconstructionConfig,
)
from tomwer.gui.reconstruction.nabu.nabuconfig.output import _NabuOutputConfig
from tomwer.core.process.reconstruction.nabu.utils import _NabuStages


class NabuConfiguration(qt.QWidget):
    """
    Top level widget for defining the nabu configuration
    """

    sigConfChanged = qt.Signal(str, str)
    """Signal emitted when the configuration change. Parameters are
    (stage, index option modified)
    """

    def __init__(self, parent, scrollArea):
        qt.QWidget.__init__(self, parent=parent)
        self._stageHided = []
        # list of hided stage. Not taking into account the filter

        self.setLayout(qt.QVBoxLayout())

        # pre processing options
        self._preProcessingGB = qt.QGroupBox("pre processing", self)
        self._preProcessingGB.setLayout(qt.QVBoxLayout())

        self._preProcessingWidget = _NabuPreProcessingConfig(
            parent=self, scrollArea=scrollArea
        )
        self._preProcessingGB.layout().addWidget(self._preProcessingWidget)
        self.layout().addWidget(self._preProcessingGB)

        # phase options
        self._phaseGB = qt.QGroupBox("phase", self)
        self._phaseGB.setLayout(qt.QVBoxLayout())

        self._phaseWidget = _NabuPhaseConfig(parent=self, scrollArea=scrollArea)
        self._phaseGB.layout().addWidget(self._phaseWidget)
        self._phaseGB.setCheckable(True)
        self.layout().addWidget(self._phaseGB)

        # reconstruction opts
        self._reconstructionGB = qt.QGroupBox("reconstruction", self)
        self._reconstructionGB.setLayout(qt.QVBoxLayout())

        self._reconstructionWidget = _NabuReconstructionConfig(
            parent=self, scrollArea=scrollArea
        )
        self._reconstructionGB.layout().addWidget(self._reconstructionWidget)
        self.layout().addWidget(self._reconstructionGB)

        # output information
        self._outputGB = qt.QGroupBox("output", self)
        self._outputGB.setLayout(qt.QVBoxLayout())

        self._outputWidget = _NabuOutputConfig(parent=self)
        self._outputGB.layout().addWidget(self._outputWidget)
        self.layout().addWidget(self._outputGB)

        # set up
        self._phaseGB.setChecked(True)

        # connect signal / slot
        self._preProcessingWidget.sigConfChanged.connect(
            self._signalConfChangedPreProcessing
        )
        self._phaseGB.toggled.connect(self._signalPhaseActivationChanged)
        self._phaseWidget.sigConfChanged.connect(self._signalConfChangedPhase)
        self._reconstructionWidget.sigConfChanged.connect(
            self._signalConfChangedReconstruction
        )
        self._outputWidget.sigConfChanged.connect(self._signalConfChangedOutput)

        # expose API
        self.getSlices = self._reconstructionWidget.getSlices
        self.setOutputDir = self._outputWidget.setOutputDir

    def setDeltaBetaValue(self, value):
        self._phaseWidget.setDeltaBetaValue(value)

    def hideSlicesInterface(self):
        self._reconstructionWidget.hideSlicesInterface()

    def hidePaganinInterface(self):
        self._stageHided.append(self._phaseGB)
        self._phaseGB.hide()

    def _signalPhaseActivationChanged(self, *args, **kwargs):
        self.sigConfChanged.emit(self._phaseWidget.getStage().value, "method")

    def _signalConfChangedPhase(self, param):
        self.sigConfChanged.emit(self._phaseWidget.getStage().value, param)

    def _signalConfChangedPreProcessing(self, param):
        self.sigConfChanged.emit(self._preProcessingWidget.getStage().value, param)

    def _signalConfChangedReconstruction(self, param):
        self.sigConfChanged.emit(self._reconstructionWidget.getStage().value, param)

    def _signalConfChangedOutput(self, param):
        self.sigConfChanged.emit(self._outputWidget.getStage().value, param)

    def getConfiguration(self):
        config = {
            "preproc": self._preProcessingWidget.getConfiguration(),
            "reconstruction": self._reconstructionWidget.getConfiguration(),
            "dataset": self._reconstructionWidget.getDatasetConfiguration(),
            "tomwer_slices": self._reconstructionWidget.getSlices(),
            "output": self._outputWidget.getConfiguration(),
            "phase": self._phaseWidget.getConfiguration(),
        }
        if not self._phaseGB.isChecked():
            config["phase"]["method"] = ""
        return config

    def setConfiguration(self, config):
        if "preproc" in config:
            self._preProcessingWidget.setConfiguration(config["preproc"])
        if "phase" in config:
            self._phaseWidget.setConfiguration(config["phase"])
            if config["phase"]["method"] == "":
                self._phaseGB.setChecked(False)
            else:
                self._phaseGB.setChecked(True)
        else:
            self._phaseGB.setChecked(False)
        if "reconstruction" in config:
            self._reconstructionWidget.setConfiguration(config["reconstruction"])
        if "tomwer_slices" in config:
            self._reconstructionWidget.setSlices(config["tomwer_slices"])
        if "dataset" in config:
            self._reconstructionWidget.setDatasetConfiguration(config["dataset"])
        if "output" in config:
            self._outputWidget.setConfiguration(config["output"])

    def applyFilter(self, stage, option):
        if stage is None:
            for widget in (
                self._preProcessingGB,
                self._reconstructionGB,
                self._outputGB,
                self._phaseGB,
            ):
                widget.setVisible(True)
        else:
            stage = _NabuStages.from_value(stage)
            self._preProcessingGB.setVisible(stage is _NabuStages.PRE)
            self._reconstructionGB.setVisible(stage is _NabuStages.PROC)
            self._outputGB.setVisible(stage is _NabuStages.POST)
            self._phaseGB.setVisible(stage is _NabuStages.PHASE)

        # handle _stageHided list
        for widget in (
            self._preProcessingGB,
            self._reconstructionGB,
            self._outputGB,
            self._phaseGB,
        ):
            if widget in (self._stageHided):
                self._phaseGB.setVisible(False)

    def setConfigurationLevel(self, level):
        for widget in (
            self._preProcessingWidget,
            self._reconstructionWidget,
            self._outputWidget,
            self._phaseWidget,
        ):
            widget.setConfigurationLevel(level)


class NabuConfigurationTab(qt.QTabWidget):
    """
    Top level widget for defining the nabu configuration.
    Same as NabuConfiguration but inside a tab
    """

    sigConfChanged = qt.Signal(str, str)
    """Signal emitted when the configuration change. Parameters are
    (stage, index option modified)
    """

    def __init__(self, parent, scrollArea):
        qt.QTabWidget.__init__(self, parent=parent)

        # pre processing options
        self._preProcessingWidget = _NabuPreProcessingConfig(
            parent=self, scrollArea=scrollArea
        )
        self.addTab(self._preProcessingWidget, "pre processing")

        # phase options
        self._phaseGB = qt.QGroupBox("apply phase", self)
        self._phaseGB.setLayout(qt.QVBoxLayout())

        self._phaseWidget = _NabuPhaseConfig(parent=self, scrollArea=scrollArea)
        self._phaseGB.layout().addWidget(self._phaseWidget)
        self._phaseGB.setCheckable(True)
        self.addTab(self._phaseGB, "phase")

        # reconstruction opts
        self._reconstructionWidget = _NabuReconstructionConfig(
            parent=self, scrollArea=scrollArea
        )
        self.addTab(self._reconstructionWidget, "reconstruction")

        # output information
        self._outputWidget = _NabuOutputConfig(parent=self)
        self.addTab(self._outputWidget, "output")

        # set up
        self._phaseGB.setChecked(True)

        # connect signal / slot
        self._preProcessingWidget.sigConfChanged.connect(
            self._signalConfChangedPreProcessing
        )
        self._phaseWidget.sigConfChanged.connect(self._signalConfChangedPhase)
        self._reconstructionWidget.sigConfChanged.connect(
            self._signalConfChangedReconstruction
        )

        # expose API
        self.getSlices = self._reconstructionWidget.getSlices
        self.setOutputDir = self._outputWidget.setOutputDir

    def _signalConfChangedPhase(self, param):
        self.sigConfChanged.emit(self._phaseWidget.getStage().value, param)

    def _signalConfChangedPreProcessing(self, param):
        self.sigConfChanged.emit(self._preProcessingWidget.getStage().value, param)

    def _signalConfChangedReconstruction(self, param):
        self.sigConfChanged.emit(self._reconstructionWidget.getStage().value, param)

    def getConfiguration(self):
        config = {
            "preproc": self._preProcessingWidget.getConfiguration(),
            "reconstruction": self._reconstructionWidget.getConfiguration(),
            "tomwer_slices": self.getSlices(),
            "output": self._outputWidget.getConfiguration(),
        }
        if self._phaseGB.isChecked():
            config["phase"] = self._phaseWidget.getConfiguration()
        return config

    def setConfiguration(self, config):
        if "preproc" in config:
            self._preProcessingWidget.setConfiguration(config["preproc"])
        if "phase" in config:
            self._phaseWidget.setConfiguration(config["phase"])
            self._phaseGB.setChecked(True)
        else:
            self._phaseGB.setChecked(False)
        if "reconstruction" in config:
            self._reconstructionWidget.setConfiguration(config["reconstruction"])
        if "tomwer_slices" in config:
            self._reconstructionWidget.setSlices(config["tomwer_slices"])


if __name__ == "__main__":
    app = qt.QApplication([])
    widget = NabuConfiguration(None, None)
    widget.show()
    print(widget.getConfiguration())
    print(widget.getSlices())
    app.exec_()
