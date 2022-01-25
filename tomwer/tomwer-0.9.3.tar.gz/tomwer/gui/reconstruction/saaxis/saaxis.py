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
"""
contains gui relative to semi-automatic axis calculation
"""


__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "01/02/2021"


from silx.gui import qt
from tomwer.gui import icons
from tomwer.gui.reconstruction.nabu.slices import NabuWindow
from tomwer.gui.reconstruction.axis.radioaxis import _CalculationWidget
from tomwer.synctools.axis import QAxisRP
from tomwer.core.process.reconstruction.nabu.utils import _NabuMode
from tomwer.core.process.reconstruction.saaxis.params import SAAxisParams
from tomwer.gui.reconstruction.scores.scoreplot import ScorePlot as _ScorePlot
from tomwer.gui.reconstruction.scores.scoreplot import CorSelection
from tomwer.gui.reconstruction.saaxis.corrangeselector import SliceAndCorWidget
from tomwer.gui.utils.buttons import TabBrowsersButtons
from tomwer.gui.reconstruction.scores.control import ControlWidget
from tomwer.core.process.reconstruction.saaxis.saaxis import SAAxisProcess
from tomwer.core.process.reconstruction.axis import mode as axis_mode
import numpy
from typing import Union
import logging


_logger = logging.getLogger(__file__)


class ScorePlot(_ScorePlot, constructor=CorSelection):
    """Score plot dedicated to center of rotation.
    Redefine the current score value to display both the absolute
    and the relative values
    """

    def _updateScores(self):
        scan = self.__scan() if self.__scan else None
        if scan is not None:
            if scan.saaxis_params:
                scan.saaxis_params.score_method = self.getScoreMethod()
                img_width = scan.dim_1
                # update autofocus
                SAAxisProcess.autofocus(scan)
        else:
            img_width = None
        self.setVarScores(
            scores=self._scores,
            score_method=self.getScoreMethod(),
            img_width=img_width,
            update_only_scores=True,
        )

    def _applyAutofocus(self):
        scan = self.__scan() if self.__scan else None
        if scan is None:
            return
        if scan.saaxis_params:
            best_cor = scan.saaxis_params.autofocus
            if best_cor:
                self._varSlider.setVarValue(best_cor)


class NabuAutoCorDiag(qt.QDialog):
    """
    GUI to compute an estimation of the Center Of Rotation
    """

    class CalculationWidget(_CalculationWidget):
        def _modeChanged(self, *args, **kwargs):
            super()._modeChanged()
            self.getMethodLockPB().hide()

    sigRequestAutoCor = qt.Signal()

    def __init__(self, parent=None, qarixrp=None):
        assert qarixrp is not None, "An instance of QAxisRP should be provided"
        qt.QDialog.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self._automatic_cor = NabuAutoCorDiag.CalculationWidget(
            parent=self,
            axis_params=qarixrp,
        )
        self._automatic_cor.getMethodLockPB().hide()

        qcb = self._automatic_cor._qcbPosition
        for mode in (axis_mode.AxisMode.manual, axis_mode.AxisMode.read):
            idx = qcb.findText(mode.value)
            if idx >= 0:
                qcb.removeItem(idx)

        self.layout().addWidget(self._automatic_cor)
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        # buttons
        types = qt.QDialogButtonBox.Ok
        self._buttons = qt.QDialogButtonBox(parent=self)
        self._buttons.setStandardButtons(types)
        self.layout().addWidget(self._buttons)

        self._buttons.button(qt.QDialogButtonBox.Ok).clicked.connect(
            self._requestAutomaticCor
        )
        self._buttons.button(qt.QDialogButtonBox.Ok).setText("compute")

    def _requestAutomaticCor(self, *args, **kwargs):
        self.sigRequestAutoCor.emit()


class _SAAxisTabWidget(qt.QTabWidget):

    sigConfigurationChanged = qt.Signal()
    """signal emitted each time the 'input' configuration changed.
    like slice to reconstruct, number of reconstruction, research width,
    nabu reconstruction parameters..."""

    def __init__(self, parent):
        qt.QTabWidget.__init__(self, parent)
        # select slice & cor range

        self._sliceAndCorWidget = SliceAndCorWidget(self)
        sinogram_icon = icons.getQIcon("sinogram")
        self.addTab(self._sliceAndCorWidget, sinogram_icon, "slice && cor range")
        # nabu reconstruction parameters
        self._nabuSettings = NabuWindow(self)
        self._nabuSettings.setConfigurationLevel(level="required")
        self._nabuSettings.hideSlicesInterface()
        nabu_icon = icons.getQIcon("nabu")
        self.addTab(self._nabuSettings, nabu_icon, "reconstruction settings")
        # results
        self._resultsViewer = ScorePlot(self, variable_name="cor")
        results_icon = icons.getQIcon("results")
        self.addTab(self._resultsViewer, results_icon, "reconstructed slices")

        # connect signal / slot
        self._nabuSettings.sigConfigChanged.connect(self._configurationChanged)
        self._sliceAndCorWidget.sigConfigurationChanged.connect(
            self._configurationChanged
        )
        self._resultsViewer.sigConfigurationChanged.connect(self._configurationChanged)
        self.sigReconstructionSliceChanged = (
            self._sliceAndCorWidget.sigReconstructionSliceChanged
        )
        self.sigAutoCorRequested = self._sliceAndCorWidget.sigAutoCorRequested
        self.sigReconstructionRangeChanged = (
            self._sliceAndCorWidget.sigReconstructionRangeChanged
        )

        # expose function API
        self.setCorScores = self._resultsViewer.setVarScores
        self.setImgWidth = self._resultsViewer.setImgWidth
        self.setVoxelSize = self._resultsViewer.setVoxelSize
        self.setVolumeSize = self._resultsViewer.setVolumeSize
        self.setCurrentCorValue = self._resultsViewer.setCurrentVarValue
        self.getCurrentCorValue = self._resultsViewer.getCurrentVarValue
        self.getScoreMethod = self._resultsViewer.getScoreMethod
        self.getEstimatedCorPosition = self._sliceAndCorWidget.getEstimatedCorPosition
        self.setEstimatedCorPosition = self._sliceAndCorWidget.setEstimatedCorPosition
        self.getNReconstruction = self._sliceAndCorWidget.getNReconstruction
        self.setNReconstruction = self._sliceAndCorWidget.setNReconstruction
        self.getResearchWidth = self._sliceAndCorWidget.getResearchWidth
        self.setResearchWidth = self._sliceAndCorWidget.setResearchWidth
        self.getReconstructionSlices = self._sliceAndCorWidget.getReconstructionSlices
        self.setReconstructionSlices = self._sliceAndCorWidget.setReconstructionSlices
        self.getReconstructionMode = self._sliceAndCorWidget.getReconstructionMode
        self.setReconstructionMode = self._sliceAndCorWidget.setReconstructionMode
        self.getFrameWidth = self._sliceAndCorWidget.getFrameWidth
        self.setFrameWidth = self._sliceAndCorWidget.setFrameWidth
        self.setNabuReconsParams = self._nabuSettings.setConfiguration
        self.getNabuReconsParams = self._nabuSettings.getConfiguration
        self.getSlicesRange = self._sliceAndCorWidget.getSlicesRange
        self.setSlicesRange = self._sliceAndCorWidget.setSlicesRange
        self.loadSinogram = self._sliceAndCorWidget.loadSinogram
        # expose signals
        self.sigStartSinogramLoad = self._sliceAndCorWidget.sigStartSinogramLoad
        self.sigEndSinogramLoad = self._sliceAndCorWidget.sigEndSinogramLoad

    def showResults(self):
        self.setCurrentWidget(self._resultsViewer)

    def _configurationChanged(self, *args, **kwargs):
        self.sigConfigurationChanged.emit()

    def lockAutoFocus(self, lock):
        self._resultsViewer.lockAutoFocus(lock=lock)

    def isAutoFocusLock(self):
        return self._resultsViewer.isAutoFocusLock()

    def hideAutoFocusButton(self):
        self._resultsViewer.hideAutoFocusButton()

    def getSinogramViewer(self):
        return self._sliceAndCorWidget._sinogramViewer

    def getCors(self, reference: str = "relative"):
        """Return cors to be computed"""
        if reference not in ("relative", "absolute"):
            raise ValueError("reference should be 'absolute' or 'relative'")
        return SAAxisParams.compute_cors(
            estimated_cor=self.getEstimatedCorPosition(reference),
            research_width=self.getResearchWidth(),
            n_reconstruction=self.getNReconstruction(),
        )

    def loadPreprocessingParams(self):
        """load reconstruction nabu if tomwer has already process this
        dataset. Not done for now"""
        return False

    def setScan(self, scan):
        self._resultsViewer.setScan(scan)
        self._nabuSettings.setScan(scan)
        if self.loadPreprocessingParams() and scan.axis_params is not None:
            self._nabuSettings.setConfiguration(scan.axis_params)
        self._sliceAndCorWidget.setScan(scan)

    def getConfiguration(self):
        nabu_config = self.getNabuReconsParams()
        enable_ht = int(self._nabuSettings.getMode() is _NabuMode.HALF_ACQ)
        nabu_config["reconstruction"]["enable_halftomo"] = enable_ht
        return {
            "research_width": self.getResearchWidth(),
            "n_reconstruction": self.getNReconstruction(),
            "slice_indexes": self.getReconstructionSlices(),
            "nabu_params": nabu_config,
            "mode": self.getReconstructionMode().value,
            "score_method": self.getScoreMethod().value,
            "estimated_cor": self.getEstimatedCorPosition(),
        }

    def setConfiguration(self, config):
        if isinstance(config, SAAxisParams):
            config = config.to_dict()
        if not isinstance(config, dict):
            raise TypeError(
                "config should be a dictionary or a SAAxisParams. "
                "Not {}".format(type(config))
            )

        research_width = config.get("research_width", None)
        if research_width is not None:
            self.setResearchWidth(research_width)
        n_reconstruction = config.get("n_reconstruction", None)
        if n_reconstruction is not None:
            self.setNReconstruction(n_reconstruction)
        estimated_cor = config.get("estimated_cor", None)
        if estimated_cor is not None:
            self.setEstimatedCorPosition(estimated_cor)
        slice_indexes = config.get("slice_indexes", None)
        if slice_indexes is not None:
            self.setReconstructionSlices(slice_indexes)
        if "nabu_params" in config:
            self.setNabuReconsParams(config["nabu_params"])
        if "mode" in config:
            self.setReconstructionMode(config["mode"])
        if "score_method" in config:
            self.setScoreMethod(config["score_method"])

    def getScoreMethod(self):
        return self._resultsViewer.getScoreMethod()

    def setScoreMethod(self, method):
        self._resultsViewer.setScoreMethod(method)

    def close(self):
        self._resultsViewer.close()
        self._resultsViewer = None
        self._sliceAndCorWidget.close()
        self._sliceAndCorWidget = None
        self._nabuSettings.close()
        self._nabuSettings = None
        super().close()

    def _stopAnimationThread(self):
        self._resultsViewer._stopAnimationThread()
        self._sliceAndCorWidget._sinogramViewer._stopAnimationThread()


class SAAxisWindow(qt.QMainWindow):
    """
    Widget used to determine half-automatically the center of rotation
    """

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)
        self._scan = None
        self._automaticCorWidget = None
        self._qaxis_rp = QAxisRP()
        self.setWindowFlags(qt.Qt.Widget)
        # central widget
        self._tabWidget = _SAAxisTabWidget(self)
        self.setCentralWidget(self._tabWidget)
        # next and previous buttons for browsing the tab widget
        self._browserButtons = TabBrowsersButtons(self)
        self._dockWidgetBrwButtons = qt.QDockWidget(self)
        self._dockWidgetBrwButtons.setWidget(self._browserButtons)
        self.addDockWidget(qt.Qt.BottomDockWidgetArea, self._dockWidgetBrwButtons)
        self._dockWidgetBrwButtons.setFeatures(qt.QDockWidget.DockWidgetMovable)
        # control widget (validate, compute, cor positions)
        self._saaxisControl = ControlWidget(self)
        self._dockWidgetCtrl = qt.QDockWidget(self)
        self._dockWidgetCtrl.setWidget(self._saaxisControl)
        self.addDockWidget(qt.Qt.BottomDockWidgetArea, self._dockWidgetCtrl)
        self._dockWidgetCtrl.setFeatures(qt.QDockWidget.DockWidgetMovable)

        # expose API
        self.setCorScores = self._tabWidget.setCorScores
        self.setImgWidth = self._tabWidget.setImgWidth
        self.setVoxelSize = self._tabWidget.setVoxelSize
        self.setVolumeSize = self._tabWidget.setVolumeSize
        self.setCurrentCorValue = self._tabWidget.setCurrentCorValue
        self.getCurrentCorValue = self._tabWidget.getCurrentCorValue
        self.getEstimatedCorPosition = self._tabWidget.getEstimatedCorPosition
        self.setEstimatedCorPosition = self._tabWidget.setEstimatedCorPosition
        self.getNReconstruction = self._tabWidget.getNReconstruction
        self.setNReconstruction = self._tabWidget.setNReconstruction
        self.getResearchWidth = self._tabWidget.getResearchWidth
        self.setResearchWidth = self._tabWidget.setResearchWidth
        self.getReconstructionSlices = self._tabWidget.getReconstructionSlices
        self.setReconstructionSlices = self._tabWidget.setReconstructionSlices
        self.getNabuReconsParams = self._tabWidget.getNabuReconsParams
        self.setNabuReconsParams = self._tabWidget.setNabuReconsParams
        self.getSlicesRange = self._tabWidget.getSlicesRange
        self.setSlicesRange = self._tabWidget.setSlicesRange
        self.getCors = self._tabWidget.getCors
        self.getMode = self._tabWidget.getReconstructionMode
        self.loadSinogram = self._tabWidget.loadSinogram
        self.isAutoFocusLock = self._tabWidget.isAutoFocusLock
        # expose signals
        self.sigValidated = self._saaxisControl.sigValidateRequest
        self.sigStartSinogramLoad = self._tabWidget.sigStartSinogramLoad
        self.sigEndSinogramLoad = self._tabWidget.sigEndSinogramLoad
        self.sigConfigurationChanged = self._tabWidget.sigConfigurationChanged

        # connect signal / slot
        self._tabWidget.sigReconstructionSliceChanged.connect(self._updateSinogramLine)
        self._tabWidget.sigAutoCorRequested.connect(self._autoCorRequested)
        self._tabWidget.sigReconstructionRangeChanged.connect(
            self._estimatedCorValueChanged
        )
        self._browserButtons.sigNextReleased.connect(self._showNextPage)
        self._browserButtons.sigPreviousReleased.connect(self._showPreviousPage)
        self._saaxisControl.sigComputationRequest.connect(self._launchReconstructions)
        self._saaxisControl.sigValidateRequest.connect(self._validate)

    def stop(self):
        self._stopAnimationThread()

    def showResults(self):
        self._tabWidget.showResults()

    def getAutomaticCorWindow(self):
        if self._automaticCorWidget is None:
            self._automaticCorWidget = NabuAutoCorDiag(self, qarixrp=self._qaxis_rp)
            self._automaticCorWidget.setWindowTitle(
                "compute estimated center of rotation"
            )
            auto_cor_icon = icons.getQIcon("a")
            self._automaticCorWidget.setWindowIcon(auto_cor_icon)
            self._automaticCorWidget.sigRequestAutoCor.connect(
                self._computeEstimatedCor
            )
        return self._automaticCorWidget

    def compute(self):
        """force compute of the current scan"""
        self._saaxisControl.sigComputationRequest.emit()

    def getConfiguration(self) -> dict:
        return self._tabWidget.getConfiguration()

    def setConfiguration(self, config: dict):
        self._tabWidget.setConfiguration(config)

    def getQAxisRP(self):
        return self._qaxis_rp

    def setScan(self, scan):
        self._scan = scan
        self._tabWidget.setScan(scan)
        self._updateSinogramLine()
        self._loadEstimatedCorFromScan(scan)

    def _loadEstimatedCorFromScan(self, scan):
        if scan.axis_params is not None:
            relative_cor = scan.axis_params.relative_cor_value
        else:
            relative_cor = None
        if relative_cor is None:
            relative_cor = scan.estimated_cor_frm_motor

        if relative_cor is not None and numpy.issubdtype(
            type(relative_cor), numpy.number
        ):
            self.setEstimatedCorPosition(relative_cor)

    def getScan(self):
        return self._scan

    def getScoreMethod(self):
        return self._tabWidget.getScoreMethod()

    def lockAutofocus(self, lock):
        self._tabWidget.lockAutoFocus(lock=lock)

    def isAutoFocusLock(self):
        return self._tabWidget.isAutoFocusLock()

    def hideAutoFocusButton(self):
        return self._tabWidget.hideAutoFocusButton()

    def _updateSinogramLine(self):
        r_slice = self.getReconstructionSlices()
        if r_slice == "middle":
            if self._scan is not None and self._scan.dim_2 is not None:
                line = self._scan.dim_2 // 2
            else:
                line = 1024
        else:
            line = list(r_slice.values())[0]
        self._tabWidget.getSinogramViewer().setLine(line)

    def setEstimatedCorPosition(self, value):
        self.setEstimatedCorPosition(value=value)

    def _autoCorRequested(self):
        window = self.getAutomaticCorWindow()
        window.activateWindow()
        window.raise_()
        window.show()

    def _computeEstimatedCor(self) -> Union[float, None]:
        """callback when calculation of a estimated cor is requested.
        Should be implemted by OrangeWidget or application"""
        raise NotImplementedError("Base class")

    def _launchReconstructions(self):
        """callback when we want to launch the reconstruction of the
        slice for n cor value"""
        raise NotImplementedError("Base class")

    def _validate(self):
        raise NotImplementedError("Base class")

    def _estimatedCorValueChanged(self):
        cors = self.getCors("absolute")
        sino_viewer = self._tabWidget._sliceAndCorWidget._sinogramViewer
        estimated_cor = self.getEstimatedCorPosition("absolute")
        if estimated_cor == "middle":
            estimated_cor = 0

        if len(cors) < 2:
            return
        elif len(cors) > 2:
            other_cors = cors[1:-1]
        else:
            other_cors = ()
        sino_viewer.setCorRange(
            min=cors[0],
            max=cors[-1],
            estimated_cor=estimated_cor,
            other_cors=other_cors,
        )

    def _showNextPage(self, *args, **kwargs):
        idx = self._tabWidget.currentIndex()
        idx += 1
        if idx < self._tabWidget.count():
            self._tabWidget.setCurrentIndex(idx)

    def _showPreviousPage(self, *args, **kwargs):
        idx = self._tabWidget.currentIndex()
        idx -= 1
        if idx >= 0:
            self._tabWidget.setCurrentIndex(idx)

    def _stopAnimationThread(self):
        self._tabWidget._stopAnimationThread()

    def close(self):
        self._tabWidget.close()
        self._tabWidget = None
        super().close()


def _get_circle_plot(center, radius, n_pts=1000):
    pts = numpy.linspace(-numpy.pi, numpy.pi, n_pts)
    x = radius * numpy.cos(pts) + center[0]
    y = radius * numpy.sin(pts) + center[1]
    return x, y
