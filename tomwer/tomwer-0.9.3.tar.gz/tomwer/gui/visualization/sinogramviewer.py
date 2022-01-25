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
contains gui relative to axis calculation using sinogram
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "26/03/2020"


from silx.gui import qt
from silx.gui.plot.ImageStack import _PlotWithWaitingLabel
import logging
import weakref

_logger = logging.getLogger(__name__)


class SinogramViewer(qt.QMainWindow):
    """
    Widget to display a sinogram
    """

    sigSinoLoadStarted = qt.Signal()
    """Signal emitted when some computation is started. For this widget
    some computation can be time consuming when creating the sinogram"""
    sigSinoLoadEnded = qt.Signal()
    """Signal emitted when a computation is ended"""

    def __init__(self, parent=None, scan=None, opts_orientation=qt.Qt.Vertical):
        qt.QMainWindow.__init__(self, parent)
        self._scan = None
        self._sinoInfoCache = None
        # used to memorize sinogram properties when load it.
        # Contains (str(scan), line, oversampling)

        self._plot = _PlotWithWaitingLabel(parent=self)
        plot = self._plot.getPlotWidget()
        plot.getDefaultColormap().setVRange(None, None)
        plot.setAxesDisplayed(False)
        plot.setKeepDataAspectRatio(True)
        self._plot.setWaiting(False)
        self._dockOpt = qt.QDockWidget(self)
        self._options = SinogramOpts(parent=self, orientation=opts_orientation)
        self._dockOpt.setWidget(self._options)

        self.setCentralWidget(self._plot)
        self._dockOpt.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._dockOpt)

        # prepare processing
        self._loadingThread = _LoadSinoThread()

        # connect signal / slot
        self._options.sigUpdateRequested.connect(self.updateSinogram)
        self._loadingThread.finished.connect(self._sinogram_loaded)

        # expose API
        self.getActiveImage = plot.getActiveImage

        # set up
        if scan is not None:
            self.setScan(scan=scan)

    def getOptionsDockWidget(self):
        return self._dockOpt

    def setReconsParams(self, axis):
        self._axis_params = axis
        # TODO: update according to axis paramters

    def setScan(self, scan, update=True):
        if self._scan is None or self._scan() != scan:
            self._scan = weakref.ref(scan)
            self._options.setScan(scan)
            if update:
                self.updateSinogram()
            else:
                self.clear()

    def setLine(self, line: int):
        """

        :param int line: define the line we want to compute
        """
        self._options.setRadioLine(line)

    def setSubsampling(self, value):
        self._options.setSubsampling(value)

    def _updatePlot(self, sinogram):
        self._plot.getPlotWidget().addImage(data=sinogram)
        self._plot.getPlotWidget().replot()

    def _editionLocked(self, locked):
        self.sigAxisEditionLocked.emit(locked)

    def _applyRequested(self):
        self.sigApply.emit()

    def _sinogram_loaded(self):
        """callback when the sinogram is loaded"""
        self._plot.setWaiting(False)
        if self._scan is None or self._scan() is None:
            return
        assert self._sinoInfoCache is not None

        scan_id, line, subsampling = self._sinoInfoCache
        # if the scan changed since the load started, skip this update
        if scan_id != str(self._scan()):
            return

        # note: cache avoid reading data twice here.
        sinogram = self._scan().get_sinogram(line=line, subsampling=subsampling)
        self._updatePlot(sinogram=sinogram)
        self.sigSinoLoadEnded.emit()
        self._options.setEnabled(True)

    def updateSinogram(self):
        if self._scan is None or self._scan() is None:
            return
        if self._loadingThread.isRunning():
            _logger.warning(
                "a sinogram is already beeing computing, please wait until it" " ends"
            )
            return
        # update scan
        self._plot.setWaiting(True)
        self.sigSinoLoadStarted.emit()
        self._sinoInfoCache = (
            str(self._scan()),
            self._options.getRadioLine(),
            self._options.getSubsampling(),
        )
        self._loadingThread.init(
            scan=self._scan(),
            line=self._options.getRadioLine(),
            subsampling=int(self._options.getSubsampling()),
        )
        self._loadingThread.start()

    def clear(self):
        self._plot.getPlotWidget().clear()

    def close(self):
        self._stopAnimationThread()
        self._plot.close()
        self._plot = None
        super().close()

    def _stopAnimationThread(self):
        self._plot.stopUpdateThread()


class _LoadSinoThread(qt.QThread):
    def init(self, scan, line, subsampling):
        self._scan = scan
        self._line = line
        self._subsampling = subsampling

    def run(self):
        try:
            self._scan.get_sinogram(line=self._line, subsampling=self._subsampling)
        except ValueError as e:
            _logger.error(e)


class SinogramOpts(qt.QDialog):
    """
    Define the options to compute and display the sinogram
    """

    sigUpdateRequested = qt.Signal()
    """signal emitted when an update of the sinogram (with different
    parameters) is requested"""

    def __init__(self, parent, orientation=qt.Qt.Vertical):
        qt.QDialog.__init__(self, parent)
        if orientation is qt.Qt.Vertical:
            self.setLayout(qt.QVBoxLayout())
        elif orientation is qt.Qt.Horizontal:
            self.setLayout(qt.QHBoxLayout())
        else:
            raise TypeError(
                "orientation should be either qt.Qt.Vertical or " "qt.Qt.Horizontal"
            )
        self._scan = None

        # add line
        self._lineSelWidget = qt.QWidget(parent=self)
        self._lineSelWidget.setLayout(qt.QHBoxLayout())
        self._lineSelWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._lineSB = qt.QSpinBox(parent=self)
        self._lineSB.setMaximum(999999)
        self._lineSelWidget.layout().addWidget(qt.QLabel("radio line", self))
        self._lineSelWidget.layout().addWidget(self._lineSB)
        self.layout().addWidget(self._lineSelWidget)

        # add subsampling option
        self._subsamplingWidget = qt.QWidget(parent=self)
        self._subsamplingWidget.setLayout(qt.QHBoxLayout())
        self._subsamplingWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._subsamplingSB = qt.QSpinBox(parent=self)
        self._subsamplingSB.setMinimum(1)
        self._subsamplingSB.setValue(4)
        self._subsamplingSB.setMaximum(100)
        self._subsamplingLabel = qt.QLabel("subsampling", self)
        self._subsamplingWidget.layout().addWidget(self._subsamplingLabel)
        self._subsamplingWidget.setToolTip(
            "if you like you can only take a "
            "subsample of the sinogram to "
            "speed up process"
        )
        self._subsamplingWidget.layout().addWidget(self._subsamplingSB)
        self.layout().addWidget(self._subsamplingWidget)

        # add spacer
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        types = qt.QDialogButtonBox.Apply
        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.setStandardButtons(types)

        self.layout().addWidget(self._buttons)

        # connect signal / slot
        self._buttons.button(qt.QDialogButtonBox.Apply).clicked.connect(
            self._updateSinogram
        )

    def setLineSelectionVisible(self, visible):
        self._lineSelWidget.setVisible(visible)

    def _updateSinogram(self):
        self.sigUpdateRequested.emit()

    def setScan(self, scan):
        old = self.blockSignals(True)
        # update line max and value
        n_line = scan.dim_2
        if n_line is None:
            n_line = 0
        self._lineSB.setMaximum(n_line)
        self.blockSignals(old)

    def getRadioLine(self):
        return self._lineSB.value()

    def setRadioLine(self, line):
        self._lineSB.setValue(line)

    def getSubsampling(self):
        return self._subsamplingSB.value()

    def setSubsampling(self, value):
        self._subsamplingSB.setValue(value)
