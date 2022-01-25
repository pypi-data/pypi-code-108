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
__date__ = "12/02/2020"

import typing
import functools
from tomwer.utils import docstring
from silx.gui import qt
from tomwer.core.process.reconstruction.nabu.utils import (
    _NabuStages,
    _NabuReconstructionMethods,
    _NabuFBPFilterType,
    _NabuPaddingType,
)
from tomwer.core.process.reconstruction.nabu.nabuslices import NabuSliceMode
from tomwer.gui.reconstruction.nabu.nabuconfig.base import _NabuStageConfigBase
from tomwer.gui.utils.inputwidget import SelectionLineEdit
from tomwer.gui.utils.scrollarea import QComboBoxIgnoreWheel
from tomwer.gui.utils.scrollarea import QDoubleSpinBoxIgnoreWheel
from tomwer.gui.utils.scrollarea import QSpinBoxIgnoreWheel
from silx.utils.enum import Enum as _Enum
from silx.gui.dialog.DataFileDialog import DataFileDialog

import logging

_logger = logging.getLogger(__name__)


class SliceGroupBox(qt.QGroupBox):
    """GroupBox to define slice to be reconstructed"""

    sigSlicesChanged = qt.Signal()
    """Signal emitted when the selected slices change"""

    def __init__(self, parent, scrollArea):
        qt.QGroupBox.__init__(self, "slices", parent)
        self.setCheckable(True)

        self.setLayout(qt.QHBoxLayout())
        self._modeCB = QComboBoxIgnoreWheel(parent=self, scrollArea=scrollArea)
        for mode in NabuSliceMode:
            self._modeCB.addItem(mode.value)
        self.layout().addWidget(self._modeCB)
        self._modeCB.setFocusPolicy(qt.Qt.FocusPolicy.NoFocus)

        self._sliceQLE = SelectionLineEdit(parent=self)
        self.layout().addWidget(self._sliceQLE)

        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        # set up
        self.setChecked(True)
        self.setMode(NabuSliceMode.MIDDLE)
        self._sliceQLE.setVisible(False)

        # connect signal / slot
        self._modeCB.currentIndexChanged.connect(self._updateSliceQLEVisibilty)
        self._modeCB.currentIndexChanged.connect(self._triggerSlicesChanged)
        self._sliceQLE.editingFinished.connect(self._triggerSlicesChanged)
        self.toggled.connect(self._triggerSlicesChanged)

    def _updateSliceQLEVisibilty(self, *args, **kwargs):
        self._sliceQLE.setVisible(self.getMode() == NabuSliceMode.OTHER)

    def _triggerSlicesChanged(self):
        self.sigSlicesChanged.emit()

    def setMode(self, mode: NabuSliceMode):
        mode = NabuSliceMode.from_value(mode)
        item_index = self._modeCB.findText(mode.value)
        self._modeCB.setCurrentIndex(item_index)
        old = self.blockSignals(True)
        self._updateSliceQLEVisibilty()
        self.blockSignals(old)

    def getMode(self) -> NabuSliceMode:
        mode = NabuSliceMode.from_value(self._modeCB.currentText())
        return mode

    def _getSliceSelected(self):
        if self.getMode() is NabuSliceMode.MIDDLE:
            return NabuSliceMode.MIDDLE.value
        else:
            return self._sliceQLE.text()

    def getSlices(self):
        """Slice selected"""
        if self.isChecked():
            return self._getSliceSelected()
        else:
            return None

    def setSlices(self, slices):
        if slices is None:
            self.setChecked(False)
        else:
            self.setChecked(True)
            if slices != NabuSliceMode.MIDDLE.value:
                self._sliceQLE.setText(slices)
                self.setMode(NabuSliceMode.OTHER)
            else:
                self.setMode(NabuSliceMode.MIDDLE)


class TranslationMvtFileWidget(qt.QWidget):
    """Widget used to define a .cvs or a DataUrl"""

    class Mode(_Enum):
        HDF5 = "hdf5"
        TEXT = "text"

    fileChanged = qt.Signal()
    """Signal emitted when the file change"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())

        self._checkBox = qt.QCheckBox(self)
        self.layout().addWidget(self._checkBox)

        self._translationFileQLE = qt.QLineEdit("", self)
        self._translationFileQLE.setReadOnly(True)
        self.layout().addWidget(self._translationFileQLE)

        self._grpBox = qt.QGroupBox("file type", self)
        self._grpBox.setLayout(qt.QVBoxLayout())
        self._grpBox.layout().setContentsMargins(0, 0, 0, 0)
        self._grpBox.layout().setSpacing(0)

        self._hdf5FileRB = qt.QRadioButton(self.Mode.HDF5.value, self)
        self._grpBox.layout().addWidget(self._hdf5FileRB)
        self._textFileRB = qt.QRadioButton(self.Mode.TEXT.value, self)
        self._grpBox.layout().addWidget(self._textFileRB)
        self.layout().addWidget(self._grpBox)

        self._selectButton = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectButton)

        # set up
        self._grpBox.setEnabled(False)
        self._translationFileQLE.setEnabled(False)
        self._selectButton.setEnabled(False)
        self._textFileRB.setChecked(True)

        # connect signal / slot
        self._selectButton.released.connect(self._selectCallback)
        self._checkBox.toggled.connect(self._toggleSelection)

    def _selectCallback(self, *args, **kwargs):
        if self.getSelectionMode() is self.Mode.HDF5:
            file_or_url = self._selectHDF5()
        elif self.getSelectionMode() is self.Mode.TEXT:
            file_or_url = self._selectTextFile()
        else:
            raise ValueError("")
        if file_or_url is not None:
            self.setFile(file_or_url)

    def _selectHDF5(self):
        dialog = DataFileDialog()
        dialog.setFilterMode(DataFileDialog.FilterMode.ExistingDataset)

        if not dialog.exec_():
            dialog.close()
            return
        else:
            return dialog.selectedUrl()

    def _selectTextFile(self):
        dialog = qt.QFileDialog(self)
        dialog.setFileMode(qt.QFileDialog.ExistingFile)

        if not dialog.exec_():
            dialog.close()
            return
        if len(dialog.selectedFiles()) > 0:
            return dialog.selectedFiles()[0]

    def isChecked(self):
        return self._checkBox.isChecked()

    def setChecked(self, checked):
        self._checkBox.setChecked(checked)

    def getSelectionMode(self):
        if self._hdf5FileRB.isChecked():
            return self.Mode.HDF5
        else:
            return self.Mode.TEXT

    def setFile(self, file_):
        if file_ in (None, ""):
            self.setChecked(False)
        else:
            self.setChecked(True)
            self._translationFileQLE.setText(file_)
            self.fileChanged.emit()

    def getFile(self):
        if self.isChecked():
            return self._translationFileQLE.text()
        else:
            return None

    def _toggleSelection(self):
        self._translationFileQLE.setEnabled(self._checkBox.isChecked())
        self._grpBox.setEnabled(self._checkBox.isChecked())
        self._selectButton.setEnabled(self._checkBox.isChecked())


class _NabuReconstructionConfig(qt.QWidget, _NabuStageConfigBase):
    """
    Widget to define the configuration of nabu reconstruction processing
    """

    sigConfChanged = qt.Signal(str)
    """Signal emitted when the configuration change. Parameter is the option
    modified
    """

    def __init__(self, parent, scrollArea):
        qt.QWidget.__init__(self, parent, stage=_NabuStages.PRE)
        _NabuStageConfigBase.__init__(self, stage=_NabuStages.PRE)
        self.setLayout(qt.QGridLayout())

        self.__angle_files = ""
        self.__optimizationIteAlgo = "chambolle-pock"

        # slices to be reconstructed online
        self._slicesWidget = SliceGroupBox(parent=self, scrollArea=scrollArea)
        self.layout().addWidget(self._slicesWidget, 0, 0, 1, 2)
        # ignore listener of the mouse for the slice widget, can
        # come with an issue as we are on a scroll area
        self._slicesWidget.setFocusPolicy(qt.Qt.FocusPolicy.NoFocus)

        # method
        self._methodLabel = qt.QLabel("method", self)
        self.layout().addWidget(self._methodLabel, 1, 0, 1, 1)
        self._methodQCB = QComboBoxIgnoreWheel(parent=self, scrollArea=scrollArea)
        for method in _NabuReconstructionMethods:
            self._methodQCB.addItem(method.value)
        self.layout().addWidget(self._methodQCB, 1, 1, 1, 1)
        self.registerWidget(self._methodLabel, "required")
        self.registerWidget(self._methodQCB, "required")

        # angle_offset
        self._labelOffsetLabel = qt.QLabel("angle offset (in degree)", self)
        self.layout().addWidget(self._labelOffsetLabel, 2, 0, 1, 1)
        self._angleOffsetQDSB = QDoubleSpinBoxIgnoreWheel(self, scrollArea)
        self._angleOffsetQDSB.setMaximum(-180)
        self._angleOffsetQDSB.setMaximum(180)
        self.layout().addWidget(self._angleOffsetQDSB, 2, 1, 1, 1)
        self.registerWidget(self._labelOffsetLabel, "advanced")
        self.registerWidget(self._angleOffsetQDSB, "advanced")

        # fbp filter type
        self._fbpFilterCB = qt.QCheckBox("fbp filter", self)
        self.layout().addWidget(self._fbpFilterCB, 3, 0, 1, 1)
        self._fbpFilterType = QComboBoxIgnoreWheel(self, scrollArea)
        for filter_type in _NabuFBPFilterType:
            self._fbpFilterType.addItem(filter_type.value)
        self.layout().addWidget(self._fbpFilterType, 3, 1, 1, 1)
        self.registerWidget(self._fbpFilterCB, "advanced")
        self.registerWidget(self._fbpFilterType, "advanced")

        # padding type
        self._paddingTypeLabel = qt.QLabel("padding type", self)
        self.layout().addWidget(self._paddingTypeLabel, 4, 0, 1, 1)
        self._paddingType = QComboBoxIgnoreWheel(self, scrollArea)
        for fbp_padding_type in _NabuPaddingType:
            self._paddingType.addItem(fbp_padding_type.value)
        self.layout().addWidget(self._paddingType, 4, 1, 1, 1)
        self.registerWidget(self._paddingTypeLabel, "optional")
        self.registerWidget(self._paddingType, "optional")

        # sub region
        self._subRegionSelector = _NabuReconstructionSubRegion(parent=self)
        self.layout().addWidget(self._subRegionSelector, 6, 0, 1, 2)

        # iterations
        self._iterationsLabel = qt.QLabel("iterations", self)
        self.layout().addWidget(self._iterationsLabel, 7, 0, 1, 1)
        self._iterationSB = qt.QSpinBox(parent=self)
        self.layout().addWidget(self._iterationSB, 7, 1, 1, 1)
        self._iterationSB.setMinimum(1)
        self._iterationSB.setMaximum(9999)
        # not supported for now so hidden
        self._iterationsLabel.hide()
        self._iterationSB.hide()

        # binning - subsampling
        self._binSubSamplingGB = _BinSubSampling(
            "binning and subsampling", parent=self, scrollArea=scrollArea
        )
        self.layout().addWidget(self._binSubSamplingGB, 8, 0, 1, 2)

        # optimization algorithm:
        # set has default value for now, because has only one at the moment

        # weight total variation
        self._tvLabel = qt.QLabel("total variation weight", self)
        self.layout().addWidget(self._tvLabel, 9, 0, 1, 1)
        self._totalVariationWeight = qt.QDoubleSpinBox(self)
        self._totalVariationWeight.setMinimum(0.0)
        self._totalVariationWeight.setMaximum(1.0)
        self._totalVariationWeight.setDecimals(4)
        self._totalVariationWeight.setSingleStep(0.002)
        self.layout().addWidget(self._totalVariationWeight, 9, 1, 1, 1)
        # not supported for now so hidden
        self._tvLabel.hide()
        self._totalVariationWeight.hide()

        # preconditioning filter
        self._preconditioningFilter = qt.QCheckBox("preconditioning_filter", self)
        self._preconditioningFilter.setToolTip(
            'Whether to enable "filter ' 'preconditioning" for iterative' " methods"
        )
        self.layout().addWidget(self._preconditioningFilter, 9, 0, 1, 2)
        # not supported for now so hidden
        self._preconditioningFilter.hide()

        # positivity constraint
        self._positivityConstraintCB = qt.QCheckBox("positivity constraint", self)
        self._positivityConstraintCB.setToolTip(
            "Whether to enforce a " "positivity constraint in the " "reconstruction."
        )
        self.layout().addWidget(self._positivityConstraintCB, 10, 0, 1, 2)
        # not supported for now so hidden
        self._positivityConstraintCB.hide()

        # translation movement file
        self._transMvtFileLabel = qt.QLabel("translation movement file", self)
        self.layout().addWidget(self._transMvtFileLabel, 11, 0, 1, 1)
        self._transMvtFileWidget = TranslationMvtFileWidget(self)
        self.layout().addWidget(self._transMvtFileWidget, 11, 1, 1, 1)
        self.registerWidget(self._transMvtFileLabel, "advanced")
        self.registerWidget(self._transMvtFileWidget, "advanced")

        # spacer for style
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer, 200, 1, 1, 1)

        # expose API
        self.getSlices = self._slicesWidget.getSlices
        self.setSlices = self._slicesWidget.setSlices

        # set up
        self._fbpFilterCB.setChecked(True)
        fbp_item = self._methodQCB.findText(_NabuReconstructionMethods.FBP.value)
        self._methodQCB.setCurrentIndex(fbp_item)
        self._angleOffsetQDSB.setValue(0)
        ramlak_item = self._fbpFilterType.findText(_NabuFBPFilterType.RAMLAK.value)
        self._fbpFilterType.setCurrentIndex(ramlak_item)
        padding_type_item = self._paddingType.findText(_NabuPaddingType.ZEROS.value)
        self._fbpFilterType.setCurrentIndex(padding_type_item)
        self._iterationSB.setValue(200)
        self._totalVariationWeight.setValue(1.0e-2)
        self._preconditioningFilter.setChecked(True)
        self._positivityConstraintCB.setChecked(True)

        # connect signal / slot
        self._methodQCB.currentIndexChanged.connect(self._methodChanged)
        self._angleOffsetQDSB.editingFinished.connect(self._angleOffsetChanged)
        self._fbpFilterCB.toggled.connect(self._FBPFilterTypeChanged)
        self._fbpFilterType.currentIndexChanged.connect(self._FBPFilterTypeChanged)
        self._paddingType.currentTextChanged.connect(self._paddingTypeChanged)
        self._subRegionSelector.sigConfChanged.connect(self._signalConfChanged)
        self._iterationSB.valueChanged.connect(self._nbIterationChanged)
        self._totalVariationWeight.valueChanged.connect(self._weightTvChanged)
        self._preconditioningFilter.toggled.connect(self._preconditionningFilterChanged)
        self._positivityConstraintCB.toggled.connect(self._positivityConstraintChanged)
        self._transMvtFileWidget.fileChanged.connect(self._mvtFileChanged)
        self._slicesWidget.sigSlicesChanged.connect(self._slicesChanged)
        self._binSubSamplingGB.binningChanged.connect(self._binningChanged)

    def hideSlicesInterface(self):
        self._slicesWidget.hide()

    def setConfigurationLevel(self, level):
        _NabuStageConfigBase.setConfigurationLevel(self, level)
        self._subRegionSelector.setConfigurationLevel(level=level)

    def _slicesChanged(self, *args, **kwargs):
        self._signalConfChanged("tomwer_slices")

    def _methodChanged(self, *args, **kwargs):
        self._signalConfChanged("method")

    def _angleOffsetChanged(self, *args, **kwargs):
        self._signalConfChanged("angle_offset")

    def _FBPFilterTypeChanged(self, *args, **kwargs):
        self._signalConfChanged("fbp_filter_type")

    def _paddingTypeChanged(self, *args, **kwargs):
        self._signalConfChanged("padding_type")

    def _nbIterationChanged(self, *args, **kwargs):
        self._signalConfChanged("iterations")

    def _weightTvChanged(self, *args, **kwargs):
        self._signalConfChanged("weight_tv")

    def _preconditionningFilterChanged(self, *args, **kwargs):
        self._signalConfChanged("preconditioning_filter")

    def _positivityConstraintChanged(self, *args, **kwargs):
        self._signalConfChanged("positivity_constraint")

    def _mvtFileChanged(self, *args, **kwargs):
        self._signalConfChanged("translation_movements_file")

    def _binningChanged(self, *args, **kwargs):
        self._signalConfChanged("binning")
        self._signalConfChanged("binning_z")

    def setScan(self, scan):
        raise NotImplementedError()

    def getMethod(self) -> _NabuReconstructionMethods:
        return _NabuReconstructionMethods.from_value(self._methodQCB.currentText())

    def setMethod(self, method):
        method = _NabuReconstructionMethods.from_value(method)
        item_index = self._methodQCB.findText(method.value)
        self._methodQCB.setCurrentIndex(item_index)

    def getAngleOffset(self) -> float:
        return self._angleOffsetQDSB.value()

    def setAngleOffset(self, value: typing.Union[str, float]):
        self._angleOffsetQDSB.setValue(float(value))

    def getFBPFilterType(self) -> typing.Union[_NabuFBPFilterType, None]:
        if self._fbpFilterCB.isChecked():
            return _NabuFBPFilterType.from_value(self._fbpFilterType.currentText())
        else:
            return None

    def setFBPFilterType(self, filter):
        if type(filter) is str and filter.lower() == "none":
            filter = None
        if filter is None:
            self._fbpFilterCB.setChecked(False)
        else:
            self._fbpFilterCB.setChecked(True)
            filter = _NabuFBPFilterType(filter)
            filter_index = self._fbpFilterType.findText(filter.value)
            self._fbpFilterType.setCurrentIndex(filter_index)

    def getFBPPaddingType(self) -> _NabuPaddingType:
        return _NabuPaddingType.from_value(self._paddingType.currentText())

    def setFBPPaddingType(self, padding):
        padding = _NabuPaddingType.from_value(padding)
        padding_index = self._paddingType.findText(padding.value)
        self._paddingType.setCurrentIndex(padding_index)

    def getNIterations(self):
        return self._iterationSB.value()

    def setNIterations(self, n_iterations):
        self._iterationSB.setValue(n_iterations)

    def getTotalVariationWeight(self) -> float:
        return self._totalVariationWeight.value()

    def setTotalVariationWeight(self, weight: float):
        self._totalVariationWeight.setValue(float(weight))

    def isPreconditioningFilterEnable(self):
        return self._preconditioningFilter.isChecked()

    def setPreconditioningFilterEnable(self, enable: typing.Union[bool, int]):
        self._preconditioningFilter.setChecked(bool(enable))

    def isPositivityConstraintEnable(self):
        return self._positivityConstraintCB.isChecked()

    def setPositivityConstraintEnable(self, enable: typing.Union[bool, int]):
        self._positivityConstraintCB.setChecked(bool(enable))

    def getTranslationMvtFile(self):
        return self._transMvtFileWidget.getFile()

    def setTranslationMvtFile(self, file_):
        self._transMvtFileWidget.setFile(file_)

    def getHorizontalBinning(self):
        return self._binSubSamplingGB.getHorizontalBinning()

    def setHorizontalBinning(self, binning):
        return self._binSubSamplingGB.setHorizontalBinning(binning=binning)

    def getVerticalBinning(self):
        return self._binSubSamplingGB.getVerticalBinning()

    def setVerticalBinning(self, binning):
        return self._binSubSamplingGB.getVerticalBinning(binning=binning)

    def getProjSubsampling(self):
        return self._binSubSamplingGB.getProjSubsampling()

    def setProjSubsampling(self, subsampling):
        return self._binSubSamplingGB.setProjSubsampling(subsampling=subsampling)

    @docstring(_NabuStageConfigBase)
    def getConfiguration(self) -> dict:
        fbp_filter_type = self.getFBPFilterType()
        if fbp_filter_type is None:
            fbp_filter_type = "none"
        else:
            fbp_filter_type = fbp_filter_type.value
        config = {
            "method": self.getMethod().value,
            "angles_file": self.__angle_files,
            # 'rotation_axis_position'  # if setted should be done upstream because managed by 'tomwer' axis
            "axis_correction_file": "",  # not managed for now
            "angle_offset": self.getAngleOffset(),
            "fbp_filter_type": fbp_filter_type,
            "padding_type": self.getFBPPaddingType().value,
            "iterations": self.getNIterations(),
            "optim_algorithm": self.__optimizationIteAlgo,
            "weight_tv": self.getTotalVariationWeight(),
            "preconditioning_filter": int(self.isPreconditioningFilterEnable()),
            "positivity_constraint": int(self.isPositivityConstraintEnable()),
            "rotation_axis_position": "",
            "translation_movements_file": self.getTranslationMvtFile() or "",
        }
        config.update(self._subRegionSelector.getConfiguration())
        return config

    def getDatasetConfiguration(self) -> dict:
        return self._binSubSamplingGB.getConfiguration()

    def setDatasetConfiguration(self, config):
        return self._binSubSamplingGB.setConfiguration(config)

    @docstring(_NabuStageConfigBase)
    def setConfiguration(self, config):
        if "method" in config:
            self.setMethod(config["method"])
        if "angles_file" in config:
            self.__angle_files = config["angles_file"]
        if "angle_offset" in config:
            self.setAngleOffset(value=config["angle_offset"])
        if "fbp_filter_type" in config:
            self.setFBPFilterType(config["fbp_filter_type"])
        if "padding_type" in config:
            self.setFBPPaddingType(config["padding_type"])
        if "iterations" in config:
            self.setNIterations(int(config["iterations"]))
        if "optim_algorithm" in config:
            self.__optimizationIteAlgo = config["optim_algorithm"]
        if "weight_tv" in config:
            self.setTotalVariationWeight(weight=config["weight_tv"])
        if "preconditioning_filter" in config:
            self.setPreconditioningFilterEnable(int(config["preconditioning_filter"]))
        if "positivity_constraint" in config:
            self.setPositivityConstraintEnable(int(config["positivity_constraint"]))
        if "translation_movements_file" in config:
            self.setTranslationMvtFile(config["translation_movements_file"])
        self._subRegionSelector.setConfiguration(config=config)

    def _signalConfChanged(self, param):
        self.sigConfChanged.emit(param)


class _SubRegionEditor(qt.QObject):

    sigConfChanged = qt.Signal(str)
    """Signal emitted each type a parameter is edited"""

    def __init__(
        self, parent, layout, layout_row: int, name: str, min_param: str, max_param: str
    ):
        assert type(layout_row) is int
        qt.QObject.__init__(self)
        self._layout = layout
        self.__minParam = min_param
        self.__maxParam = max_param

        validator = qt.QIntValidator()
        validator.setBottom(0)

        self._subRegionLabel = qt.QLabel(name, parent)
        self.layout().addWidget(self._subRegionLabel, layout_row, 0, 1, 1)

        # min
        self._minCB = qt.QCheckBox("min", parent)
        self.layout().addWidget(self._minCB, layout_row, 1, 1, 1)
        self._minQLE = qt.QLineEdit("0", parent)
        self._minQLE.setValidator(validator)
        self.layout().addWidget(self._minQLE, layout_row, 2, 1, 1)

        # max
        self._maxCB = qt.QCheckBox("max", parent)
        self.layout().addWidget(self._maxCB, layout_row, 3, 1, 1)
        self._maxQLE = qt.QLineEdit("0", parent)
        self._maxQLE.setValidator(validator)
        self.layout().addWidget(self._maxQLE, layout_row, 4, 1, 1)

        # spacer for style
        self._spacer = qt.QWidget(parent)
        self._spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self.layout().addWidget(self._spacer, layout_row, 5, 1, 1)

        # set up
        self._minCB.setChecked(False)
        self._minQLE.setEnabled(False)
        self._maxCB.setChecked(False)
        self._maxQLE.setEnabled(False)

        # connect signal / slot
        self._minCB.toggled.connect(self._minQLE.setEnabled)
        self._maxCB.toggled.connect(self._maxQLE.setEnabled)
        self._minCB.toggled.connect(
            functools.partial(self._signalConfChanged, self.__minParam)
        )
        self._maxCB.toggled.connect(
            functools.partial(self._signalConfChanged, self.__maxParam)
        )
        self._minQLE.editingFinished.connect(
            functools.partial(self._signalConfChanged, self.__minParam)
        )
        self._maxQLE.editingFinished.connect(
            functools.partial(self._signalConfChanged, self.__maxParam)
        )

    def layout(self):
        return self._layout

    def getSubRegionMin(self) -> typing.Union[None, int]:
        """

        :return: None if region is unbounded else the value of the bound
        """
        if self._minCB.isChecked():
            return int(self._minQLE.text())
        else:
            return None

    def getSubRegionMax(self) -> typing.Union[None, int]:
        """

        :return: None if region is unbounded else the value of the bound
        """
        if self._maxCB.isChecked():
            return int(self._maxQLE.text())
        else:
            return None

    def setSubRegionMin(self, min: typing.Union[None, int]) -> None:
        """

        :param min: if min is None or -1 wr will expand it to - infinity
        """
        if min in (-1, 0):
            min = None
        if min is None:
            self._minCB.setChecked(False)
        else:
            self._minCB.setChecked(True)
            self._minQLE.setText(str(min))

    def setSubRegionMax(self, max) -> None:
        """

        :param max: if max is None or -1 wr will expand it to infinity
        """
        if type(max) is str:
            max = int(max)
        if max == -1:
            max = None
        if max is None:
            self._maxCB.setChecked(False)
        else:
            self._maxCB.setChecked(True)
            self._maxQLE.setText(str(max))

    def getSubRegion(self) -> tuple:
        """

        :return: min, max
        :rtype: tuple
        """
        return self.getSubRegionMin(), self.getSubRegionMax()

    def setSubRegion(self, min: typing.Union[None, int], max: typing.Union[None, int]):
        """

        :param tuple min:
        :param tuple max:
        """
        self.setSubRegionMin(min)
        self.setSubRegionMax(max)

    def _signalConfChanged(self, param):
        self.sigConfChanged.emit(param)

    def setVisible(self, visible):
        for widget in (
            self._subRegionLabel,
            self._minCB,
            self._minQLE,
            self._maxCB,
            self._maxQLE,
            self._spacer,
        ):
            widget.setVisible(visible)


class _NabuReconstructionSubRegion(qt.QGroupBox, _NabuStageConfigBase):
    """Widget to select a sub region to reconstruct"""

    sigConfChanged = qt.Signal(str)
    """Signal emitted each type a parameter is edited"""

    def __init__(self, parent):
        qt.QGroupBox.__init__(self, parent, stage=_NabuStages.PROC)
        _NabuStageConfigBase.__init__(self, stage=_NabuStages.PROC)
        self.setTitle("sub region")

        self.setLayout(qt.QGridLayout())

        self._xSubRegion = _SubRegionEditor(
            parent=self,
            layout=self.layout(),
            layout_row=0,
            name="x",
            min_param="start_x",
            max_param="end_x",
        )
        self.registerWidget(self._xSubRegion, "optional")

        self._ySubRegion = _SubRegionEditor(
            parent=self,
            layout=self.layout(),
            layout_row=1,
            name="y",
            min_param="start_y",
            max_param="end_y",
        )
        self.registerWidget(self._ySubRegion, "optional")

        self._zSubRegion = _SubRegionEditor(
            parent=self,
            layout=self.layout(),
            layout_row=2,
            name="z",
            min_param="start_z",
            max_param="end_z",
        )
        self.registerWidget(self._zSubRegion, "optional")

        # set up

        # connect signal / slot
        self._xSubRegion.sigConfChanged.connect(self._signalConfChanged)
        self._ySubRegion.sigConfChanged.connect(self._signalConfChanged)
        self._zSubRegion.sigConfChanged.connect(self._signalConfChanged)

    def getConfiguration(self) -> dict:
        return {
            "start_x": self._xSubRegion.getSubRegionMin() or 0,
            "end_x": self._xSubRegion.getSubRegionMax() or -1,
            "start_y": self._ySubRegion.getSubRegionMin() or 0,
            "end_y": self._ySubRegion.getSubRegionMax() or -1,
            "start_z": self._zSubRegion.getSubRegionMin() or 0,
            "end_z": self._zSubRegion.getSubRegionMax() or -1,
        }

    def setConfiguration(self, config):
        if "start_x" in config:
            self._xSubRegion.setSubRegionMin(int(config["start_x"]))
        if "end_x" in config:
            self._xSubRegion.setSubRegionMax(int(config["end_x"]))
        if "start_y" in config:
            self._ySubRegion.setSubRegionMin(int(config["start_y"]))
        if "end_y" in config:
            self._ySubRegion.setSubRegionMax(int(config["end_y"]))
        if "start_z" in config:
            self._zSubRegion.setSubRegionMin(int(config["start_z"]))
        if "end_z" in config:
            self._zSubRegion.setSubRegionMax(int(config["end_z"]))

    def _signalConfChanged(self, param):
        self.sigConfChanged.emit(param)


class _BinSubSampling(qt.QGroupBox):

    binningChanged = qt.Signal()
    """signal emitted when binning change"""

    def __init__(self, text, parent, scrollArea):
        qt.QGroupBox.__init__(self, text)
        self.setLayout(qt.QFormLayout())
        # horizontal binning
        self._hBinningSB = QSpinBoxIgnoreWheel(self, scrollArea=scrollArea)
        self._hBinningSB.setMinimum(1)
        self._hBinningSB.setMaximum(3)
        self.layout().addRow("horizontal binning", self._hBinningSB)
        # vertical binning
        self._vBinningSB = qt.QSpinBox(self)
        self._vBinningSB.setMinimum(1)
        self._vBinningSB.setMaximum(100)
        # self.layout().addRow('vertical binning', self._vBinningSB)
        self._vBinningSB.setVisible(False)
        # projection subsampling
        self._projSubsamplingSB = QSpinBoxIgnoreWheel(self, scrollArea=scrollArea)
        self._projSubsamplingSB.setMinimum(1)
        self._projSubsamplingSB.setMaximum(100)
        self.layout().addRow("projection subsampling", self._projSubsamplingSB)

        # connect signal / slot
        self._vBinningSB.valueChanged.connect(self._valueUpdated)
        self._hBinningSB.valueChanged.connect(self._valueUpdated)

    def getHorizontalBinning(self):
        return self._hBinningSB.value()

    def setHorizontalBinning(self, binning):
        return self._hBinningSB.setValue(int(binning))

    def getVerticalBinning(self):
        return self._vBinningSB.value()

    def setVerticalBinning(self, binning):
        return self._vBinningSB.setValue(int(binning))

    def getProjSubsampling(self):
        return self._projSubsamplingSB.value()

    def setProjSubsampling(self, subsampling):
        return self._projSubsamplingSB.setValue(int(subsampling))

    def getConfiguration(self):
        return {
            "binning": self.getHorizontalBinning(),
            "binning_z": self.getVerticalBinning(),
            "projections_subsampling": self.getProjSubsampling(),
        }

    def setConfiguration(self, config):
        if "binning" in config:
            self.setHorizontalBinning(config["binning"])
        if "binning_z" in config:
            self.setVerticalBinning(config["binning_z"])
        if "projections_subsampling" in config:
            self.setProjSubsampling(subsampling=config["projections_subsampling"])

    def _valueUpdated(self, *args, **kwargs):
        self.binningChanged.emit()


if __name__ == "__main__":
    app = qt.QApplication([])
    widget = _NabuReconstructionConfig(None, None)
    widget.show()
    print(widget.getConfiguration())
    app.exec_()
