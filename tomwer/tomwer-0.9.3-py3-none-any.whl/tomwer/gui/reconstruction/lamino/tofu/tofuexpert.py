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
__date__ = "01/06/2018"


import subprocess
from silx.gui import qt
import tomwer.core.utils.gpu
from tomwer.core.process.reconstruction.lamino.tofu import has_tofu
import logging
from .TofuOptionLoader import _TofuOptionLoader, _getterSetter

_logger = logging.getLogger(__name__)


class ExpertTofuWidget(_TofuOptionLoader, qt.QWidget):
    """
    Widget used to define the parameters for the tofu script
    """

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent=parent)
        self.setLayout(qt.QVBoxLayout())

        self._verbose = qt.QCheckBox("verbose", parent=self)
        self._verbose.setChecked(True)
        self.layout().addWidget(self._verbose)

        # retries group
        self._retriesGB = qt.QGroupBox("retries parameters", parent=self)
        self._retriesGB.setLayout(qt.QGridLayout())
        self._retriesGB.layout().addWidget(
            qt.QLabel("n retries:", parent=self._retriesGB), 0, 0
        )
        self._retriesSP = qt.QSpinBox(parent=self._retriesGB)
        self._retriesSP.setMinimum(0)
        self._retriesGB.layout().addWidget(self._retriesSP, 0, 1)
        self._retriesGB.layout().addWidget(
            qt.QLabel("timeout:", parent=self._retriesGB), 1, 0
        )
        self._timeoutLE = qt.QLineEdit("0", parent=self._retriesGB)
        validator = qt.QDoubleValidator(parent=self._timeoutLE)
        validator.setBottom(0.0)
        self._timeoutLE.setValidator(validator)
        self._retriesGB.layout().addWidget(self._timeoutLE, 1, 1)
        self.layout().addWidget(self._retriesGB)

        # GPU group
        self._gpuGrp = GpuGroupBox(parent=self)
        self.layout().addWidget(self._gpuGrp)

        # options text edit
        self._qteOptions = OptionEdit(parent=self)
        self.layout().addWidget(self._qteOptions)

        # expose API
        self.getAdditionalRecoOptions = self._qteOptions.getAdditionalRecoOptions
        self.addAdditionalRecoOption = self._qteOptions.addAdditionalRecoOption
        self.setAdditionalRecoOptions = self._qteOptions.setAdditionalRecoOptions
        self.getAdditionalPreprocessOptions = (
            self._qteOptions.getAdditionalPreprocessOptions
        )
        self.addAdditionalPreprocessOption = (
            self._qteOptions.addAdditionalPreprocessOption
        )
        self.setAdditionalPreprocessOptions = (
            self._qteOptions.setAdditionalPreprocessOptions
        )
        self.getHighLimit = self._gpuGrp.getHighLimit

        options = {
            "verbose": _getterSetter(
                getter=self.requireVerbose, setter=self.setVerbose
            ),
            "retries": _getterSetter(getter=self.getNRetries, setter=self.setNRetries),
            "retry-timeout": _getterSetter(
                getter=self.getNRetries, setter=self.setRetriesTimeout
            ),
            "slices-per-device": _getterSetter(
                getter=self.getSlicePerDevice, setter=self.setSlicePerDevice
            ),
            "slice-memory-coeff": _getterSetter(
                getter=self.getSliceMemoryCoeff, setter=self.setSliceMemoryCoeff
            ),
        }
        _TofuOptionLoader.__init__(self, options=options)

    def getNRetries(self):
        """

        :return: return number of retry before avoiding the reconstruction
        """
        return self._retriesSP.value()

    def setNRetries(self, value):
        """ """
        try:
            self._retriesSP.setValue(int(value))
        except Exception as error:
            _logger.warning("Fails to set N tries, error is", error)

    def getRetriesTimeout(self):
        """

        :return: return time (in second) of the time out for the tofu
                 reconstruction
        """
        return float(self._timeoutLE.text())

    def setRetriesTimeout(self, value):
        """ """
        if value is None:
            return
        try:
            self._timeoutLE.setText(str(value))
        except Exception as error:
            _logger.warning("Fails to set N tries, error is", error)

    def getSliceMemoryCoeff(self):
        """

        :return: None if want default, otherwise value between 0.01 and 0.9
        """
        return self._gpuGrp.getSliceMemoryCoeff()

    def getSlicePerDevice(self):
        """

        :return: None if we don't want to activate this option. Otherwise int
                 from 1 to inf
        """
        return self._gpuGrp.getSlicePerDevice()

    def setSlicePerDevice(self, nslice):
        if nslice is not None:
            self._gpuGrp.setSlicePerDevice(nslice)

    def setSliceMemoryCoeff(self, value):
        if value is not None:
            self._gpuGrp.setSliceMemoryCoeff(value)

    def requireVerbose(self):
        """

        :return: True if the user require verbose for reconstruction
        """
        return self._verbose.isChecked()

    def setVerbose(self, value=True):
        _value = value
        if _value == "":
            _value = True
        self._verbose.setChecked(_value)

    def loadFromScan(self, scanID):
        # nothing to be done here
        pass

    def resetAdditionalRecoOptions(self):
        self._qteOptions.resetAdditionalRecoOptions()

    def resetAdditionalPreprocessOptions(self):
        self._qteOptions.resetAdditionalPreprocessOptions()


class OptionEdit(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(qt.QLabel("options:"))
        self._tabWidget = qt.QTabWidget(parent=self)

        # recons opt
        self._qteAddReconsOptions = qt.QTextEdit(parent=self._tabWidget)
        self._addAdditionalReconsOptions()
        self._tabWidget.addTab(self._qteAddReconsOptions, "Additional reco options")
        self._addAdditionalReconsOptions()
        # ffc options
        self._qteAddPreprocessOptions = qt.QTextEdit(parent=self._tabWidget)
        self._addAdditionalReconsOptions()
        self._tabWidget.addTab(
            self._qteAddPreprocessOptions, "Additional preprocess options"
        )
        self._addAdditionalPreprocessOptions()
        # fixed options
        self._qteFixedOptions = qt.QTextEdit(parent=self._tabWidget)
        self._qteFixedOptions.setDisabled(True)
        self._addFixedOptions()
        self._tabWidget.addTab(self._qteFixedOptions, "Options managed by the GUI")
        self.layout().addWidget(self._tabWidget)
        # reco help
        self._recoHelpScrollArea = qt.QScrollArea(parent=self)
        self._qteTofuRecoHelp = qt.QLabel("", parent=self._recoHelpScrollArea)
        self._addTofuRecoHelp()
        self._recoHelpScrollArea.setWidget(self._qteTofuRecoHelp)
        self._tabWidget.addTab(self._recoHelpScrollArea, "See tofu reco help")
        # ffc help
        self._preprocessHelpScrollArea = qt.QScrollArea(parent=self)
        self._qteTofuPreprocessHelp = qt.QLabel(
            "", parent=self._preprocessHelpScrollArea
        )
        self._addTofuPreprocessHelp()
        self._preprocessHelpScrollArea.setWidget(self._qteTofuPreprocessHelp)
        self._tabWidget.addTab(
            self._preprocessHelpScrollArea, "See tofu preprocess help"
        )

        # add some tooltip
        self._qteAddReconsOptions.setToolTip(
            "If you want some options to be "
            "passed to tofu reco which are not "
            "present in 'options managed' "
            "then add the option and value if "
            "necessary in the list"
        )
        self._qteAddPreprocessOptions.setToolTip(
            "If you want some options to be "
            "passed to tofu preprocess which are not "
            "present in 'options managed' "
            "then add the option and value if "
            "necessary in the list"
        )
        self._qteFixedOptions.setToolTip(
            "This list all the options "
            "that are generated automatically "
            "with there values (if necessary) "
            "by the interface"
        )
        self._qteTofuRecoHelp.setToolTip("See help from the used tofu version")

    def _addFixedOptions(self):
        """
        Add information about the fixed option (the one always generated
        in the tofu reco call)
        :return:
        """
        options = [
            "z-parameter []",
            "retry-timeout []",
            "retries []",
            "verbose",
            "slices-per-device []",
            "slice-memory-coeff []",
            "projections []",
            "darks []",
            "flats []",
            "flats2 []",
            "fix-nan-and-inf",
            "number []",
            "pixel-size []",
            "volume-angle-x []",
            "volume-angle-y []",
            "volume-angle-z []",
            "region []",
            "output []",
            "dry-run (activated if no output specify)",
            "center-position-x []",
            "center-position-z []",
            "overall-angle []",
            "axis-angle-x []",
            "axis-angle-y []",
            "x-region []",
            "y-region []",
            "regularization-rate",
            "absorptivity",
            "thresholding-rate",
            "retrieval-method",
            "energy",
            "propagation-distance",
        ]
        self._qteFixedOptions.setText(" --".join(options))

    def _addAdditionalReconsOptions(self):
        self._qteAddReconsOptions.setText(
            " ".join(
                (
                    "--resize 0",
                    "--projection-padding-mode clamp_to_edge",
                    "--genreco-padding-mode clamp_to_edge",
                )
            )
        )

    def _addAdditionalPreprocessOptions(self):
        self._qteAddPreprocessOptions.setText(
            " ".join(
                (
                    "--resize 0",
                    "--projection-padding-mode clamp_to_edge",
                    "--fix-nan-and-inf",
                    "--projection-filter none",
                )
            )
        )

    def addAdditionalRecoOption(self, option, value):
        self._qteAddReconsOptions.setText(
            " ".join(
                (
                    self._qteAddReconsOptions.toPlainText(),
                    "--" + option + " " + str(value),
                )
            )
        )

    def addAdditionalPreprocessOption(self, option, value):
        self._qteAddPreprocessOptions.setText(
            " ".join(
                (
                    self._qteAddPreprocessOptions.toPlainText(),
                    "--" + option + " " + str(value),
                )
            )
        )

    def setAdditionalRecoOptions(self, text):
        self._qteAddReconsOptions.setText(text)

    def setAdditionalPreprocessOptions(self, text):
        self._qteAddPreprocessOptions.setText(text)

    def getAdditionalRecoOptions(self):
        return self._qteAddReconsOptions.toPlainText().replace("\n", " ")

    def getAdditionalPreprocessOptions(self):
        return self._qteAddPreprocessOptions.toPlainText().replace("\n", " ")

    def resetAdditionalRecoOptions(self):
        self._qteAddReconsOptions.clear()

    def resetAdditionalPreprocessOptions(self):
        self._qteAddPreprocessOptions.clear()

    def _getNodeParameters(self):
        """Add the value of the detain options + some extra parameters to be
        passed as 'free string'

        :return:
        :rtype: tuple (dict, list)
        """
        _ddict = {}
        for option in self._options:
            _ddict[option] = self._options[option].getter()
        return _ddict, self.getAdditionalRecoOptions()

    def _addTofuRecoHelp(self):
        if has_tofu() is True:
            try:
                process = subprocess.Popen(
                    ["tofu", "reco", "--help"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = process.communicate()
                if (len(stdout.decode("utf-8"))) > 0:
                    self._qteTofuRecoHelp.setText(stdout.decode("utf-8"))
                else:
                    self._qteTofuRecoHelp.setText(stderr.decode("utf-8"))
            except Exception:
                try:
                    process.kill()
                    process.wait()
                except Exception:
                    self._qteTofuRecoHelp.setText("Tofu reco help not found")
        else:
            self._qteTofuRecoHelp.setText("Tofu not found")
        self._qteTofuRecoHelp.setTextInteractionFlags(qt.Qt.TextSelectableByMouse)
        self._qteTofuRecoHelp.setAlignment(qt.Qt.AlignTop)

    def _addTofuPreprocessHelp(self):
        if has_tofu() is True:
            try:
                process = subprocess.Popen(
                    ["tofu", "preprocess", "--help"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = process.communicate()
                if (len(stdout.decode("utf-8"))) > 0:
                    self._qteTofuPreprocessHelp.setText(stdout.decode("utf-8"))
                else:
                    self._qteTofuPreprocessHelp.setText(stderr.decode("utf-8"))
            except Exception:
                try:
                    process.kill()
                    process.wait()
                except Exception:
                    self._qteTofuPreprocessHelp.setText(
                        "Tofu preprocess help not found"
                    )
        else:
            self._qteTofuPreprocessHelp.setText("Tofu not found")
        self._qteTofuPreprocessHelp.setTextInteractionFlags(qt.Qt.TextSelectableByMouse)
        self._qteTofuPreprocessHelp.setAlignment(qt.Qt.AlignTop)


class GpuGroupBox(qt.QGroupBox):
    """
    Class grouping all the options relative to GPU
    """

    gpuOptionChanged = qt.Signal()
    """Signal emitted when the option of the gpu are modified"""

    class SlicePerDeviceWidget(qt.QWidget):
        def __init__(self, parent):
            qt.QWidget.__init__(self, parent)
            self.setLayout(qt.QVBoxLayout())
            self.layout().setContentsMargins(0, 0, 0, 0)
            self._noneLabel = qt.QLabel("None", parent=self)
            self.layout().addWidget(self._noneLabel)
            self._slicePerDevice = qt.QSpinBox(parent=self)
            self._slicePerDevice.setMinimum(1)
            self._slicePerDevice.setMaximum(1000000)
            self.layout().addWidget(self._slicePerDevice)
            self._slicePerDevice.setVisible(False)

        def setValue(self, value):
            self._slicePerDevice.setVisible(value is not None)
            self._noneLabel.setVisible(value is None)

            if value is not None:
                self._slicePerDevice.setValue(value)

        def getValue(self):
            if self._noneLabel.isVisible():
                return None
            else:
                return self._slicePerDevice.value()

        def activeValueMode(self, b):
            self._slicePerDevice.setVisible(b is True)
            self._slicePerDevice.setEnabled(b is True)
            self._noneLabel.setVisible(b is False)
            self.setVisible(True)

    def __init__(self, parent):
        qt.QGroupBox.__init__(self, "GPU optional parameters", parent)
        self.setLayout(qt.QGridLayout())

        self._sliceMemoryCoeffRB = qt.QRadioButton("slice memory coeff", parent=self)

        self.layout().addWidget(self._sliceMemoryCoeffRB, 0, 0)

        self._sliceMemoryCoeff = qt.QLineEdit("0.8", parent=self)
        validator = qt.QDoubleValidator(parent=self._sliceMemoryCoeff)
        validator.setBottom(0.01)
        validator.setTop(0.9)
        self._sliceMemoryCoeff.setValidator(validator)

        self.layout().addWidget(self._sliceMemoryCoeff, 0, 2)
        self._sliceMemoryCoeffRB.toggled.connect(self._mvToMemoCoeff)

        self._slicePerDeviceRB = qt.QRadioButton("slices per device", parent=self)
        self.layout().addWidget(self._slicePerDeviceRB, 1, 0)

        self._slicePerDevice = self.SlicePerDeviceWidget(parent=self)
        self.layout().addWidget(self._slicePerDevice, 1, 2)
        self._slicePerDevice.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum
        )

        self._slicePerDeviceRB.toggled.connect(self._mvToSlicePerDevice)

        self._autoRB = qt.QRadioButton("auto", parent=self)
        self.layout().addWidget(self._autoRB, 2, 0)
        self._autoRB.toggled.connect(self._mvToAuto)
        self._autoRB.setChecked(True)

        for _radioButton in (
            self._slicePerDeviceRB,
            self._sliceMemoryCoeffRB,
            self._autoRB,
        ):
            _radioButton.toggled.connect(self.__gpuOptionChange)
        self._slicePerDevice._slicePerDevice.valueChanged.connect(
            self.__gpuOptionChange
        )
        self._sliceMemoryCoeff.textChanged.connect(self.__gpuOptionChange)

    def _mvToAuto(self):
        """Move to auto mode"""
        self._sliceMemoryCoeff.setText("0.8")
        self._sliceMemoryCoeff.setVisible(True)
        self._sliceMemoryCoeff.setEnabled(False)
        self._slicePerDevice.setValue(None)
        self._slicePerDevice.setVisible(True)
        self._slicePerDevice.setEnabled(False)

    def _mvToMemoCoeff(self):
        self._slicePerDevice.setEnabled(False)
        self._sliceMemoryCoeff.setVisible(True)
        self._sliceMemoryCoeff.setEnabled(True)
        self._slicePerDevice.setValue(None)
        self._slicePerDevice.setVisible(False)

    def _mvToSlicePerDevice(self):
        self._slicePerDevice.setEnabled(True)
        self._sliceMemoryCoeff.setVisible(False)
        self._sliceMemoryCoeff.setEnabled(False)
        self._slicePerDevice.activeValueMode(True)

    def getSliceMemoryCoeff(self):
        if self._sliceMemoryCoeff.isVisible():
            return float(self._sliceMemoryCoeff.text())
        else:
            return None

    def getSlicePerDevice(self):
        if self._slicePerDevice.isVisible():
            return self._slicePerDevice.getValue()
        else:
            return None

    def setSlicePerDevice(self, value):
        self._slicePerDevice.setEnabled(True)
        self._slicePerDevice.setVisible(True)
        try:
            self._slicePerDevice.setValue(int(value))
        except Exception as error:
            _logger.warning("Fails to set slice per device, error is", error)

    def setSliceMemoryCoeff(self, value):
        self._sliceMemoryCoeff.setVisible(True)
        self._sliceMemoryCoeff.setEnabled(True)
        try:
            self._sliceMemoryCoeff.setText(value)
        except Exception as error:
            _logger.warning("Fails to set memory coefficient, error is", error)

    def getHighLimit(self):
        if self._slicePerDeviceRB.isChecked():
            n_gpu = tomwer.core.utils.gpu.getNumberOfDevice() or 1
            return self._slicePerDevice._slicePerDevice.value() * n_gpu
        else:
            return None

    def __gpuOptionChange(self, *args, **kwargs):
        self.gpuOptionChanged.emit()
