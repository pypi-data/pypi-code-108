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
__date__ = "04/08/2020"


from silx.gui import qt
from tomwer.core.process.reconstruction.nabu.utils import (
    ConfigurationLevel,
    _NabuStages,
)
from tomwer.gui.reconstruction.nabu.action import (
    BasicConfigurationAction,
    ExpertConfigurationAction,
    MinimalisticConfigurationAction,
)
from tomwer.gui.reconstruction.nabu.nabuconfig.base import _NabuStageConfigBase
from tomwer.gui import icons


class _SliceSelector(qt.QWidget):
    """
    Widget to select a value for defining a ROI to reconstruction (start or
    end)
    """

    valueChanged = qt.Signal()

    def __init__(
        self, label, auto_alias, is_end, grid_layout, index_layout, parent=None
    ):
        qt.QWidget.__init__(self, parent=parent)
        self._label = qt.QLabel(label, parent=self)
        grid_layout.addWidget(self._label, index_layout, 0, 1, 1)
        self._qcb = qt.QCheckBox(auto_alias)
        grid_layout.addWidget(self._qcb, index_layout, 1, 1, 1)
        grid_layout.addWidget(qt.QLabel("or", self), index_layout, 2, 1, 1)
        self._qle = qt.QLineEdit("0", self)
        self._validator = qt.QIntValidator()
        self._qle.setValidator(self._validator)
        grid_layout.addWidget(self._qle, index_layout, 3, 1, 1)
        self._is_end = is_end
        if is_end is True:
            self._qle.setToolTip("-1 will be the last slice")
            self._validator.setBottom(-1)
        else:
            self._validator.setBottom(0)

        # set up
        self._qcb.setChecked(True)
        self._qle.setEnabled(False)
        if is_end:
            self._qle.setText("-1")

        # connect signal / slot
        self._qcb.toggled.connect(self._qle.setDisabled)
        self._qcb.toggled.connect(self._triggerValueChanged)
        self._qle.editingFinished.connect(self._triggerValueChanged)

    def _triggerValueChanged(self, *args, **kwargs):
        self.valueChanged.emit()

    def setMaximum(self, maximum):
        self._validator.setTop(maximum)

    def value(self):
        if self._qcb.isChecked():
            return -1 if self._is_end else 0
        else:
            return int(self._qle.text())

    def setValue(self, value):
        self._qle.setText(str(value))
        if self._is_end:
            self._qcb.setChecked(value == -1)
        else:
            self._qcb.setChecked(value == 0)


class NabuVolumeWidget(_NabuStageConfigBase, qt.QWidget):
    """
    Widget dedicated to manage the volume reconstruction from nabu
    """

    sigConfigChanged = qt.Signal()
    """Signal emitted when the configuration change"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent=parent)
        _NabuStageConfigBase.__init__(self, stage=_NabuStages.VOLUME)
        self.setLayout(qt.QGridLayout())

        # warning about requires parameters from a nabu slice reconstruction
        self._warning_widget = qt.QWidget(parent=self)
        self._warning_widget.setLayout(qt.QHBoxLayout())
        self._warningIconL = qt.QLabel("", parent=self)
        self._warningIconL.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self._warningIconL.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self._warningIconR = qt.QLabel("", parent=self)
        self._warningIconR.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self._warningIconR.setAlignment(qt.Qt.AlignLeft | qt.Qt.AlignVCenter)
        warning_icon = icons.getQIcon("warning")
        self._warningIconL.setPixmap(warning_icon.pixmap(20, 20))
        self._warningIconR.setPixmap(warning_icon.pixmap(20, 20))
        self._warning_widget.layout().addWidget(self._warningIconL)

        self._labelWarning = qt.QLabel(
            "Requires parameters from nabu slice reconstruction.", parent=self
        )
        self._labelWarning.setToolTip(
            'This mean that a "nabu slice '
            'reconstruction" widget should exist upstream'
        )
        self._warning_widget.layout().addWidget(self._labelWarning)
        self._warning_widget.layout().addWidget(self._warningIconR)
        self.layout().addWidget(self._warning_widget, 0, 0, 1, 2)

        # volume from and to option
        self._groupBox = qt.QGroupBox("volume to reconstruct", parent=self)
        self._groupBox.setLayout(qt.QGridLayout())
        self.layout().addWidget(self._groupBox, 2, 0, 1, 2)

        self._fromSlice = _SliceSelector(
            label="from slice",
            auto_alias="start",
            is_end=False,
            parent=self,
            grid_layout=self._groupBox.layout(),
            index_layout=0,
        )
        self._groupBox.layout().addWidget(self._fromSlice)
        self.registerWidget(self._groupBox, "required")

        self._toSlice = _SliceSelector(
            label="to slice",
            auto_alias="end",
            is_end=True,
            parent=self,
            grid_layout=self._groupBox.layout(),
            index_layout=1,
        )
        self._groupBox.layout().addWidget(self._toSlice)

        # option to compute histogram
        self._histogramCB = qt.QCheckBox("compute volume values histogram", self)
        self.layout().addWidget(self._histogramCB, 3, 0, 1, 2)
        self.registerWidget(self._histogramCB, "required")

        # gpu percentage
        self._labelGPUFract = qt.QLabel("GPU percentage usage", self)
        self.layout().addWidget(self._labelGPUFract, 4, 0, 1, 1)
        self.registerWidget(self._labelGPUFract, "advanced")
        self._spbGPUFract = qt.QSpinBox(self)
        self._spbGPUFract.setSingleStep(10)
        self._spbGPUFract.setSuffix("%")
        self._spbGPUFract.setMinimum(1)
        self._spbGPUFract.setMaximum(100)
        self.layout().addWidget(self._spbGPUFract, 4, 1, 1, 1)
        self._spbGPUFract.setToolTip("Which fraction of GPU memory to use.")
        self.registerWidget(self._spbGPUFract, "advanced")

        # cpu percentage
        self._labelCPUFract = qt.QLabel("CPU percentage usage", self)
        self.layout().addWidget(self._labelCPUFract, 5, 0, 1, 1)
        self.registerWidget(self._labelCPUFract, "advanced")
        self._spbCPUFract = qt.QSpinBox(self)
        self._spbCPUFract.setSingleStep(10)
        self._spbCPUFract.setSuffix("%")
        self._spbCPUFract.setMinimum(1)
        self._spbCPUFract.setMaximum(100)
        self.layout().addWidget(self._spbCPUFract, 5, 1, 1, 1)
        self._spbCPUFract.setToolTip("Which fraction of CPU memory to use.")
        self.registerWidget(self._spbCPUFract, "advanced")

        # opt use phase paganin
        self._usePhaseQCB = qt.QCheckBox("Use phase paganin")
        self.layout().addWidget(self._usePhaseQCB, 6, 0, 1, 2)
        self.registerWidget(self._usePhaseQCB, "advanced")
        self._usePhaseQCB.setToolTip(
            "Whether to use a margin when " "performing phase retrieval."
        )

        # spacer for style
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer, 99, 0, 1, 1)

        # set up
        self._spbGPUFract.setValue(90)
        self._spbCPUFract.setValue(90)
        self._usePhaseQCB.setChecked(True)
        self.setConfigurationLevel("required")

        # connect signal / slot
        self._fromSlice.valueChanged.connect(self._triggerSigConfChanged)
        self._toSlice.valueChanged.connect(self._triggerSigConfChanged)
        self._spbGPUFract.valueChanged.connect(self._triggerSigConfChanged)
        self._spbCPUFract.valueChanged.connect(self._triggerSigConfChanged)
        self._usePhaseQCB.toggled.connect(self._triggerSigConfChanged)

    def _triggerSigConfChanged(self, *args, **kwargs):
        self.sigConfigChanged.emit()

    def getCPUFract(self):
        return self._spbCPUFract.value() / 100.0

    def setCPUFract(self, value):
        return self._spbCPUFract.setValue(value * 100.0)

    def getGPUFract(self):
        return self._spbGPUFract.value() / 100.0

    def setGPUFract(self, value):
        return self._spbGPUFract.setValue(value * 100.0)

    def getStartZ(self):
        return self._fromSlice.value()

    def setStartZ(self, value):
        self._fromSlice.setValue(value)

    def getEndZ(self):
        return self._toSlice.value()

    def setEndZ(self, value):
        self._toSlice.setValue(value)

    def phasePaganinRequested(self):
        return self._usePhaseQCB.isChecked()

    def setPhasePaganinRequested(self, checked):
        self._usePhaseQCB.setChecked(checked)

    def setScan(self, scan):
        if len(scan.projections) > 0:
            self._fromSlice.setMaximum(len(scan.projections))
        else:
            self._fromSlice.setMaximum(999999999)

    def isHistogramRequested(self):
        return self._histogramCB.isChecked()

    def setHistogramRequested(self, requested):
        self._histogramCB.setChecked(requested)

    def getConfiguration(self):
        return {
            "start_z": self.getStartZ(),
            "end_z": self.getEndZ(),
            "gpu_mem_fraction": self.getGPUFract(),
            "cpu_mem_fraction": self.getCPUFract(),
            "use_phase_margin": self.phasePaganinRequested(),
            "postproc": {
                "output_histogram": int(self.isHistogramRequested()),
            },
        }

    def setConfiguration(self, config):
        if "start_z" in config:
            self.setStartZ(config["start_z"])
        if "end_z" in config:
            self.setEndZ(config["end_z"])
        if "gpu_mem_fraction" in config:
            self.setGPUFract(config["gpu_mem_fraction"])
        if "cpu_mem_fraction" in config:
            self.setCPUFract(config["cpu_mem_fraction"])
        if "use_phase_margin" in config:
            self.setPhasePaganinRequested(config["use_phase_margin"])
        if "postproc" in config:
            self.setPostProcConfiguration(config["postproc"])

    def setPostProcConfiguration(self, config):
        if "output_histogram" in config:
            self.setHistogramRequested(requested=bool(config["output_histogram"]))

    def setConfigurationLevel(self, level):
        level = ConfigurationLevel.from_value(level)
        _NabuStageConfigBase.setConfigurationLevel(self, level)

    def getConfigurationLevel(self):
        return self._configuration_level


class NabuVolumeWindow(qt.QMainWindow):
    """
    Widget to define settings for a volume reconstruction
    """

    sigConfigChanged = qt.Signal()
    """Signal emitted when configuration change"""

    def __init__(self, parent):
        qt.QMainWindow.__init__(self, parent=parent)

        self.setWindowFlags(qt.Qt.Widget)

        self._mainWidget = NabuVolumeWidget(parent=self)
        self.setCentralWidget(self._mainWidget)

        # add toolbar
        toolbar = qt.QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(qt.Qt.TopToolBarArea, toolbar)

        # add configuration mode
        self.__configurationModesAction = qt.QAction(self)
        self.__configurationModesAction.setCheckable(False)
        menu = qt.QMenu(self)
        self.__configurationModesAction.setMenu(menu)
        toolbar.addAction(self.__configurationModesAction)

        self.__configurationModesGroup = qt.QActionGroup(self)
        self.__configurationModesGroup.setExclusive(True)
        self.__configurationModesGroup.triggered.connect(self._userModeChanged)

        self._minimalisticAction = MinimalisticConfigurationAction(toolbar)
        menu.addAction(self._minimalisticAction)
        self._basicConfigAction = BasicConfigurationAction(toolbar)
        menu.addAction(self._basicConfigAction)
        self.__configurationModesGroup.addAction(self._basicConfigAction)
        self._expertConfiguration = ExpertConfigurationAction(toolbar)
        menu.addAction(self._expertConfiguration)
        self.__configurationModesGroup.addAction(self._expertConfiguration)

        # expose API
        self.getConfiguration = self._mainWidget.getConfiguration
        self.setConfiguration = self._mainWidget.setConfiguration
        self.setConfigurationLevel = self._mainWidget.setConfigurationLevel
        self.getConfigurationLevel = self._mainWidget.getConfigurationLevel
        self.setScan = self._mainWidget.setScan

        # set up
        self._basicConfigAction.setChecked(True)
        self._userModeChanged(action=self._basicConfigAction)

        # connect signal / slot
        self._mainWidget.sigConfigChanged.connect(self._triggerSigConfigChanged)

    def _triggerSigConfigChanged(self, *args, **kwargs):
        self.sigConfigChanged.emit()

    def _userModeChanged(self, action):
        self.__configurationModesAction.setIcon(action.icon())
        self.__configurationModesAction.setToolTip(action.tooltip())
        if action is self._basicConfigAction:
            level = ConfigurationLevel.OPTIONAL
        elif action is self._expertConfiguration:
            level = ConfigurationLevel.ADVANCED
        else:
            raise ValueError("unknow configuration level")
        self._mainWidget.setConfigurationLevel(level)

    def getConfigurationLevel(self):
        self._mainWidget.getConfigurationLevel()
