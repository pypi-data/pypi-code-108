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
__date__ = "15/12/2021"


from silx.gui import qt
from tomwer.core.process.reconstruction.nabu.castvolume import (
    RESCALE_MAX_PERCENTILE,
    RESCALE_MIN_PERCENTILE,
    DataType,
    DEFAULT_OUTPUT_DIR,
)
from tomwer.core.process.reconstruction.nabu.nabucommon import NabuOutputFileFormat
from tomwer.gui.reconstruction.nabu.nabuconfig.output import QNabuFileFormatComboBox
import logging

_logger = logging.getLogger(__name__)


class CastVolumeWidget(qt.QWidget):

    sigConfigChanged = qt.Signal()
    """Signal emit when the configuration changed"""

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)

        self.setLayout(qt.QGridLayout())

        # output data size
        self._castToLabel = qt.QLabel("cast to", self)
        self._castToLabel.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.layout().addWidget(self._castToLabel, 0, 0, 1, 1)
        self._outputDataSizeCB = qt.QComboBox(self)
        for data_size in DataType:
            self._outputDataSizeCB.addItem(data_size.value)
        self.layout().addWidget(self._outputDataSizeCB, 0, 2, 1, 2)
        # output file format
        self._outputFileformatLabel = qt.QLabel("output file format", self)
        self.layout().addWidget(self._outputFileformatLabel, 1, 0, 1, 1)
        self._outputFileformatCB = QNabuFileFormatComboBox(self)
        for file_format in (
            NabuOutputFileFormat.EDF,
            NabuOutputFileFormat.HDF5,
            NabuOutputFileFormat.JP2K,
        ):
            idx = self._outputFileformatCB.findText(file_format.value)
            if idx >= 0:
                self._outputFileformatCB.view().setRowHidden(idx, True)
        self.layout().addWidget(self._outputFileformatCB, 1, 2, 1, 1)
        # rescale percentiles
        self._percentilesLabel = qt.QLabel("rescale percentiles")
        self.layout().addWidget(self._percentilesLabel, 2, 0, 1, 1)
        self._lowPercentileQSB = qt.QSpinBox(self)
        self._lowPercentileQSB.setRange(0, 100)
        self._lowPercentileQSB.setPrefix("min:")
        self._lowPercentileQSB.setValue(RESCALE_MIN_PERCENTILE)
        self.layout().addWidget(self._lowPercentileQSB, 2, 1, 1, 1)
        self._highPercentileQSB = qt.QSpinBox(self)
        self._highPercentileQSB.setRange(0, 100)
        self._highPercentileQSB.setPrefix("max:")
        self._highPercentileQSB.setValue(RESCALE_MAX_PERCENTILE)
        self.layout().addWidget(self._highPercentileQSB, 2, 2, 1, 1)
        # save dir
        self._saveDirLabel = qt.QLabel("output directory", self)
        self.layout().addWidget(self._saveDirLabel, 3, 0, 1, 1)
        self._useDefaultSaveDirQCB = qt.QCheckBox("default", self)
        self._useDefaultSaveDirQCB.setToolTip(
            f"Default directory is: {DEFAULT_OUTPUT_DIR}"
        )
        self._useDefaultSaveDirQCB.setSizePolicy(
            qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum
        )
        self._useDefaultSaveDirQCB.setChecked(True)
        self.layout().addWidget(self._useDefaultSaveDirQCB, 3, 1, 1, 1)
        self._saveDirQLE = qt.QLineEdit(DEFAULT_OUTPUT_DIR, self)
        self._saveDirQLE.setToolTip(
            """
            can contains pattern / keywords. Those should be provided as '{keyword}'. Here are pattern currently handled:
            \n - 'scan_dir_name': returns name of the directory containing the acquisition (! not a path !)"
            \n - 'scan_basename': returns basename of the directory containing the acquisition"
            \n - 'scan_parent_dir_basename': returns basename of the PARENT directory containing the acquisition"
            """
        )
        self._saveDirQLE.setVisible(False)
        self.layout().addWidget(self._saveDirQLE, 3, 2, 1, 1)
        # overwrite
        self._overwriteCB = qt.QCheckBox("overwrite", self)
        self._overwriteCB.setChecked(True)
        self.layout().addWidget(self._overwriteCB, 4, 0, 1, 1)
        # spacer
        self._spacer = qt.QWidget(self)
        self._spacer.setSizePolicy(
            qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Expanding
        )
        self.layout().addWidget(self._spacer, 99, 0, 1, 3)

        # connect signal / slot
        self._outputFileformatCB.currentIndexChanged.connect(self._configChanged)
        self._outputDataSizeCB.currentIndexChanged.connect(self._configChanged)
        self._saveDirQLE.editingFinished.connect(self._configChanged)
        self._useDefaultSaveDirQCB.toggled.connect(self._configChanged)
        self._overwriteCB.toggled.connect(self._configChanged)
        self._useDefaultSaveDirQCB.toggled.connect(self._updateOutputDirVis)

    def getOutputDataSize(self) -> DataType:
        return DataType.from_value(self._outputDataSizeCB.currentText())

    def setOutputDataSize(self, data_size) -> None:
        data_size = DataType.from_value(data_size)
        idx = self._outputDataSizeCB.findText(data_size.value)
        if idx >= 0:
            self._outputDataSizeCB.setCurrentIndex(idx)

    def getOutputDir(self) -> str:
        if self._useDefaultSaveDirQCB.isChecked():
            return DEFAULT_OUTPUT_DIR
        else:
            return self._saveDirQLE.text()

    def setOutputDir(self, output_dir: str) -> None:
        self._useDefaultSaveDirQCB.setChecked(output_dir == DEFAULT_OUTPUT_DIR)
        self._saveDirQLE.setText(output_dir)

    def getOutputFileFormat(self) -> NabuOutputFileFormat:
        return NabuOutputFileFormat.from_value(self._outputFileformatCB.currentText())

    def setOutputFileformat(self, file_format: str) -> None:
        file_format = NabuOutputFileFormat.from_value(file_format)
        idx = self._outputFileformatCB.findText(file_format.value)
        if idx >= 0:
            self._outputFileformatCB.setCurrentIndex(idx)

    def getOverwrite(self) -> bool:
        return self._overwriteCB.isChecked()

    def setOverwrite(self, remove) -> None:
        self._overwriteCB.setChecked(remove)

    def getConfiguration(self) -> dict:
        return {
            "output_data_type": self.getOutputDataSize().value,
            "output_file_format": self.getOutputFileFormat().value,
            "output_dir": self.getOutputDir(),
            "overwrite": self.getOverwrite(),
            "rescale_percentiles": self.getRescalePercentiles(),
        }

    def getRescalePercentiles(self) -> tuple:
        return self._lowPercentileQSB.value(), self._highPercentileQSB.value()

    def setRescalePercentiles(self, low, high) -> tuple:
        self._lowPercentileQSB.setValue(low)
        self._highPercentileQSB.setValue(high)

    def setConfiguration(self, config: dict) -> None:
        output_data_type = config.get("output_data_type", None)
        if output_data_type is not None:
            self.setOutputDataSize(output_data_type)
        output_file_format = config.get("output_file_format", None)
        if output_file_format is not None:
            self.setOutputFileformat(output_file_format)
        output_dir = config.get("output_dir", None)
        if output_dir is not None:
            self.setOutputDir(output_dir)
        overwrite = config.get("overwrite", None)
        if overwrite is not None:
            self.setOverwrite(overwrite)
        rescale_percentiles = config.get("rescale_percentiles", None)
        if rescale_percentiles is not None:
            if not len(rescale_percentiles) == 2:
                _logger.error(
                    f"percentiles is expected to contain two values not {len(rescale_percentiles)}"
                )
            else:
                self.setRescalePercentiles(
                    rescale_percentiles[0], rescale_percentiles[1]
                )

    def _configChanged(self, *args, **kwargs):
        self.sigConfigChanged.emit()

    def _updateOutputDirVis(self, *args, **kwargs):
        self._saveDirQLE.setVisible(not self._useDefaultSaveDirQCB.isChecked())
