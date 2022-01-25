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
__date__ = "13/08/2021"

from silx.gui import qt
from silx.utils.enum import Enum as _Enum
from silx.gui.utils.signal import SignalProxy
import weakref
import logging
from silx.gui.plot.ImageStack import UrlLoader, ImageStack as _ImageStack
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.utils.ftseriesutils import get_vol_file_shape
from silx.io.url import DataUrl
from tomwer.gui.visualization.reconstructionparameters import ReconstructionParameters
from tomwer.gui.visualization.scanoverview import ScanOverviewWidget
from tomwer.io.utils.utils import get_slice_data

try:
    from PIL import Image
except ImportError:
    has_PIL = False
else:
    has_PIL = True
try:
    import cv2
except ImportError:
    has_cv2 = False
else:
    has_cv2 = True
import numpy
import numpy.lib.npyio
import time
import os

_logger = logging.getLogger(__name__)


class DataViewer(qt.QMainWindow):
    """
    Widget used to browse through data and reconstructed slices
    """

    sigConfigChanged = qt.Signal()
    """Signal emitted when the settings (display mode, options...) changed. """

    def __init__(self, parent):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        self._scan = None

        # viewer
        self._viewer = ImageStack(parent=self)
        # set an UrlLoader managing .npy and .vol
        self._viewer.getPlotWidget().setKeepDataAspectRatio(True)
        self.setCentralWidget(self._viewer)

        # signal / slot
        # add a signal proxy on the QSlider
        self._viewer._slider.sigCurrentUrlIndexChanged.disconnect(
            self._viewer.setCurrentUrlIndex
        )
        self._proxySig = SignalProxy(
            self._viewer._slider.sigCurrentUrlIndexChanged,
            delay=0.3,
            slot=self._urlIndexDelayed,
        )

        # display control
        self._controls = DisplayControl(parent=self)
        self._controlsDW = qt.QDockWidget(self)
        self._controlsDW.setWidget(self._controls)
        self._controlsDW.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.TopDockWidgetArea, self._controlsDW)

        # connect signal / slot
        self._controls.sigDisplayModeChanged.connect(self._updateDisplay)
        self._controls.sigDisplayModeChanged.connect(self._reportSettingsUpdate)

    def getPlotWidget(self):
        return self._viewer.getPlotWidget()

    def getCurrentUrl(self):
        return self._viewer.getCurrentUrl()

    def cleanBeforeQuit(self):
        self._viewer._plot.updateThread.stop()

    def close(self):
        self.stop()
        self._viewer.close()
        self._viewer = None
        super().close()

    def _urlIndexDelayed(self, *args, **kwargs):
        self._viewer.setCurrentUrlIndex(args[0][0])

    def getScan(self):
        if self._scan:
            return self._scan()

    def setScan(self, scan):
        if scan is not None:
            self._scan = weakref.ref(scan)
        else:
            self._scan = None
        # update scan name
        self._viewer.setScan(scan=scan)
        self._controls.setScanName(str(scan))
        self._updateDisplay()
        # has the display is post pone we can only set expected dimensions
        # for the viewer
        self._viewer.setResetZoomOnNextIteration(True)

    def getDisplayMode(self):
        return self._controls.getDisplayMode()

    def setDisplayMode(self, mode):
        self._controls.setDisplayMode(mode)

    def getRadioOption(self):
        return self._controls.getRadioOption()

    def setRadioOption(self, opt):
        self._controls.setRadioOption(opt)

    def getSliceOption(self):
        return self._controls.getSliceOption()

    def setSliceOption(self, opt):
        self._controls.setSliceOption(opt)

    def _updateDisplay(self):
        """Update display of the viewer"""
        # TODO: add a param visible for frames
        self._viewer.setSliceReconsParamsVisible(
            self.getDisplayMode() is _DisplayMode.SLICES
        )
        self._viewer.setScanOverviewVisible(
            self.getDisplayMode() is not _DisplayMode.SLICES
        )
        if self._scan is None or self._scan() is None:
            self._viewer.reset()
        else:
            assert isinstance(self._scan(), TomwerScanBase)
            if self.getDisplayMode() is _DisplayMode.RADIOS:
                # update the normalization function from the viewer if needed
                if self.getRadioOption() is _RadioMode.NORMALIZED:
                    url_to_index = {
                        v.path(): k for k, v in self._scan().projections.items()
                    }
                    self._viewer.setNormalizationFct(
                        self._scan().data_flat_field_correction,
                        url_indexes=url_to_index,
                    )
                else:
                    self._viewer.setNormalizationFct(None)

                slices = self._scan().projections
            elif self.getDisplayMode() is _DisplayMode.SLICES:
                self._viewer.setNormalizationFct(None)
                if self.getSliceOption() is _SliceMode.LATEST:
                    slices = self._scan().latest_reconstructions
                else:
                    slices = self._scan().get_reconstructions_urls()
            elif self.getDisplayMode() is _DisplayMode.DARKS:
                self._viewer.setNormalizationFct(None)
                slices = self._scan().darks
            elif self.getDisplayMode() is _DisplayMode.FLATS:
                self._viewer.setNormalizationFct(None)
                slices = self._scan().flats
            else:
                raise ValueError("DisplayMode should be RADIOS or SLICES")

            if isinstance(slices, dict):
                slices = [
                    value
                    for key, value in sorted(slices.items(), key=lambda item: item[0])
                ]
            if slices is not None and len(slices) > 0:
                self._viewer.setUrls(slices)
            else:
                self._viewer.reset()

    def _reportSettingsUpdate(self):
        self.sigConfigChanged.emit()

    def clear(self):
        self._scan = None
        self._viewer.reset()
        self._viewer.setUrls(list())
        self._controls.clear()

    def stop(self):
        # insure we call self._viewer._freeLoadingThreads()
        self._viewer.reset()


class _DisplayMode(_Enum):
    RADIOS = "radios"
    SLICES = "slices"
    DARKS = "darks"
    FLATS = "flats"


class _RadioMode(_Enum):
    NORMALIZED = "normalized"
    RAW = "raw"


class _SliceMode(_Enum):
    LATEST = "latest"
    ALL = "all"


class DisplayControl(qt.QWidget):
    """
    Widget used to define what we want to display from the viewer
    """

    sigDisplayModeChanged = qt.Signal()
    """Signal emitted when the configuration of the display change"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self._lastConfig = None, None
        self.setLayout(qt.QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # scan information
        scanLab = qt.QLabel("scan:", self)
        scanLab.setFixedWidth(40)
        scanLab.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.layout().addWidget(scanLab, 0, 0, 1, 1)
        self._scanQLE = qt.QLineEdit("", self)
        self._scanQLE.setReadOnly(True)
        self.layout().addWidget(self._scanQLE, 0, 1, 1, 3)

        # display information
        displayLab = qt.QLabel("display:", self)
        displayLab.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.layout().addWidget(displayLab, 1, 0, 1, 1)
        self._displayMode = qt.QComboBox(self)
        for mode in _DisplayMode:
            self._displayMode.addItem(mode.value)
        self.layout().addWidget(self._displayMode, 1, 1, 1, 1)

        # option information
        self._modeLab = qt.QLabel("mode:", self)
        self._modeLab.setFixedWidth(60)
        self._modeLab.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.layout().addWidget(self._modeLab, 1, 2, 1, 1)
        self._widget_options = qt.QWidget(self)
        self._widget_options.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self._widget_options, 1, 3, 1, 1)

        self._radioMode = qt.QComboBox(self)
        for mode in _RadioMode:
            self._radioMode.addItem(mode.value)
        self._widget_options.layout().addWidget(self._radioMode)

        self._sliceMode = qt.QComboBox(self)
        for mode in _SliceMode:
            self._sliceMode.addItem(mode.value)
        self._widget_options.layout().addWidget(self._sliceMode)

        # set up
        # by default propose slices to avoid useless processing on radios
        idx = self._displayMode.findText(_DisplayMode.SLICES.value)
        self._displayMode.setCurrentIndex(idx)
        self._updateOptions()

        # connect signal and slot
        self._displayMode.currentTextChanged.connect(self._updateOptions)
        self._radioMode.currentTextChanged.connect(self._updateOptions)
        self._sliceMode.currentTextChanged.connect(self._updateOptions)

    def getDisplayMode(self) -> _DisplayMode:
        """

        :return: selected mode: display slices or radios
        """
        return _DisplayMode.from_value(self._displayMode.currentText())

    def setDisplayMode(self, mode):
        mode = _DisplayMode.from_value(mode)
        idx = self._displayMode.findText(mode.value)
        self._displayMode.setCurrentIndex(idx)

    def getRadioOption(self) -> _RadioMode:
        return _RadioMode.from_value(self._radioMode.currentText())

    def setRadioOption(self, opt):
        opt = _RadioMode.from_value(opt)
        idx = self._radioMode.findText(opt.value)
        self._radioMode.setCurrentIndex(idx)

    def getSliceOption(self) -> _SliceMode:
        return _SliceMode.from_value(self._sliceMode.currentText())

    def setSliceOption(self, opt):
        opt = _SliceMode.from_value(opt)
        idx = self._sliceMode.findText(opt.value)
        self._sliceMode.setCurrentIndex(idx)

    def _updateOptions(self, *args, **kwargs):
        mode = self.getDisplayMode()
        self._radioMode.setVisible(mode == _DisplayMode.RADIOS)
        self._sliceMode.setVisible(mode == _DisplayMode.SLICES)
        self._modeLab.setVisible(mode in (_DisplayMode.RADIOS, _DisplayMode.SLICES))
        if mode is _DisplayMode.RADIOS:
            config = mode, self.getRadioOption()
        elif mode is _DisplayMode.SLICES:
            config = mode, self.getSliceOption()
        elif mode is _DisplayMode.DARKS:
            config = mode, None
        elif mode is _DisplayMode.FLATS:
            config = mode, None
        else:
            raise ValueError("mode should be RADIOS or SLICES")
        if config != self._lastConfig:
            self._lastConfig = config
            self.sigDisplayModeChanged.emit()

    def setScanName(self, scan_name: str):
        self._scanQLE.setText(scan_name)

    def clear(self):
        self._scanQLE.clear()


class ImageStack(_ImageStack):
    def __init__(self, parent, show_overview=True):
        self._normFct = None
        self._url_indexes = None
        super(ImageStack, self).__init__(parent)
        self.setUrlLoaderClass(_TomwerUrlLoader)
        # hide axis to be display
        self._plot.getPlotWidget().setAxesDisplayed(False)
        self._loadSliceParams = False
        self._resetZoom = True

        # add dock widget for reconstruction parameters
        self._reconsInfoDockWidget = qt.QDockWidget(parent=self)
        self._reconsWidgetScrollArea = qt.QScrollArea(self)
        self._reconsWidget = ReconstructionParameters(self)
        self._reconsWidgetScrollArea.setWidget(self._reconsWidget)
        self._reconsInfoDockWidget.setWidget(self._reconsWidgetScrollArea)
        self._reconsInfoDockWidget.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._reconsInfoDockWidget)

        # add scan overview dock widget
        self._scanOverviewDockerWidget = qt.QDockWidget(parent=self)
        self._scanOverviewDockerWidget.setMaximumHeight(300)
        self._scanOverviewWidget = ScanOverviewWidget(self)
        self._scanOverviewDockerWidget.setWidget(self._scanOverviewWidget)
        self._scanOverviewDockerWidget.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._scanOverviewDockerWidget)

        # for now hide the "control"
        self._urlsTable._toggleButton.hide()

        # set up
        self.setAutoResetZoom(False)
        if not show_overview:
            self._scanOverviewDockerWidget.hide()

    def setScan(self, scan):
        self._scanOverviewWidget.setScan(scan=scan)

    def resetZoom(self):
        self._plot.getPlotWidget().resetZoom()

    def setLimits(self, x_min, x_max, y_min, y_max):
        plot = self._plot.getPlotWidget()
        plot.setLimits(xmin=x_min, ymin=y_min, xmax=x_max, ymax=y_max)

    def getLimits(self):
        plot = self._plot.getPlotWidget()
        limits = []
        limits.extend(plot.getGraphXLimits())
        limits.extend(plot.getGraphYLimits())
        return tuple(limits)

    def setSliceReconsParamsVisible(self, visible):
        """show or not information regarding the slice reconstructed"""
        self._reconsInfoDockWidget.setVisible(visible)
        self._loadSliceParams = visible

    def setScanOverviewVisible(self, visible):
        """show or not overview of the scan"""
        self._scanOverviewDockerWidget.setVisible(visible)

    def setNormalizationFct(self, fct, url_indexes=None):
        self._normFct = fct
        self._url_indexes = url_indexes

    def _urlLoaded(self) -> None:
        """

        :param url: result of DataUrl.path() function
        :return:
        """
        sender = self.sender()
        url = sender.url.path()
        if self._urlIndexes is not None and url in self._urlIndexes:
            data = sender.data
            if data is None:
                _logger.warning("no data found (is the url valid ?) " + url)
                return

            if data.ndim != 2:
                if data.ndim == 3 and data.shape[0] == 1:
                    data = data.reshape((data.shape[1], data.shape[2]))
                else:
                    _logger.warning(
                        "Image Stack only manage 2D data. Url: {}" "".format(url)
                    )
                    return
            if self._normFct is None:
                self._urlData[url] = data
            else:
                norm_data = self._normFct(data, index=self._urlIndexes[url])
                self._urlData[url] = norm_data

            if self.getCurrentUrl().path() == url:
                self._plot.setData(self._urlData[url])
                if self._resetZoom:
                    self._resetZoom = False
                    self._plot.getPlotWidget().resetZoom()

            if sender in self._loadingThreads:
                self._loadingThreads.remove(sender)
            self.sigLoaded.emit(url)

    def setResetZoomOnNextIteration(self, reset):
        self._resetZoom = reset

    def setCurrentUrl(self, url):
        if self._loadSliceParams:
            try:
                self._reconsWidget.setUrl(url)
            except Exception as e:
                _logger.info(
                    "Unable to set reconstruction parameters from"
                    " {}. Not handled for pyhst reconstructions. "
                    "Error is {}".format(url, str(e))
                )
        super().setCurrentUrl(url)

    def setUrls(self, urls: list):
        _ImageStack.setUrls(self, urls)
        listWidget = self._urlsTable._urlsTable._listWidget
        items = []
        for i in range(listWidget.count()):
            # TODO: do this on the fly
            item = listWidget.item(i)
            try:
                url = DataUrl(path=item.text())
            except Exception:
                _logger.info(
                    "fail to deduce data of last modification for "
                    "{}".format(item.text())
                )
            else:
                if os.path.exists(url.file_path()):
                    lst_m = time.ctime(os.path.getmtime(url.file_path()))
                    item.setToolTip("last modification : {}".format(lst_m))
            items.append(listWidget.item(i))


class _TomwerUrlLoader(UrlLoader):
    """
    Thread use to load DataUrl
    """

    def __init__(self, parent, url):
        super(UrlLoader, self).__init__(parent=parent)
        assert isinstance(url, DataUrl)
        self.url = url
        self.data = None

    def run(self):
        if self.url.file_path().endswith(".vol"):
            self.data = self._load_vol()
        elif self.url.scheme() == "cv2":
            if has_cv2:
                self.data = cv2.imread(self.url.file_path(), -1)
            else:
                self.data = None
                _logger.warning(
                    f"need to install cv2 to read cast file {self.url.file_path()} because fabio fails to read float16"
                )
        elif self.url.scheme() == "numpy":
            data = numpy.load(self.url.file_path())
            if isinstance(data, numpy.lib.npyio.NpzFile):
                data = data["result"]
            self.data = data
        elif self.url.scheme() == "tomwer":
            if has_PIL:
                self.data = numpy.array(Image.open(self.url.file_path()))
                if self.url.data_slice() is not None:
                    self.data = self.data[self.url.data_slice()]
            else:
                _logger.warning(
                    "need to install Pillow to read file " + self.url.file_path()
                )
                self.data = None
        else:
            try:
                self.data = get_slice_data(self.url)
            except IOError:
                self.data = None
            except ValueError:
                self.data = None
                _logger.warning(
                    "Fail to open {}. Maybe the reconstruction failed.".format(
                        self.url.path()
                    )
                )

    def _load_vol(self):
        """
        load a .vol file
        """
        if self.url.file_path().lower().endswith(".vol.info"):
            info_file = self.url.file_path()
            raw_file = self.url.file_path().replace(".vol.info", ".vol")
        else:
            assert self.url.file_path().lower().endswith(".vol")
            raw_file = self.url.file_path()
            info_file = self.url.file_path().replace(".vol", ".vol.info")

        if not os.path.exists(raw_file):
            data = None
            mess = f"Can't find raw data file {raw_file} associated with {info_file}"
            _logger.warning(mess)
        elif not os.path.exists(info_file):
            mess = f"Can't find info file {info_file} associated with {raw_file}"
            _logger.warning(mess)
            data = None
        else:
            shape = get_vol_file_shape(info_file)
            if None in shape:
                _logger.warning(f"Fail to retrieve data shape for {info_file}.")
                data = None
            else:
                try:
                    numpy.zeros(shape)
                except MemoryError:
                    data = None
                    _logger.warning(
                        f"Raw file %s is too large for being read {raw_file}"
                    )
                else:
                    data = numpy.fromfile(
                        raw_file, dtype=numpy.float32, count=-1, sep=""
                    )
                    try:
                        data = data.reshape(shape)
                    except ValueError:
                        _logger.warning(
                            "unable to fix shape for raw file {}. "
                            "Look for information in {}"
                            "".format(raw_file, info_file)
                        )
                        try:
                            sqr = int(numpy.sqrt(len(data)))
                            shape = (1, sqr, sqr)
                            data = data.reshape(shape)
                        except ValueError:
                            _logger.info(
                                "deduction of shape size for {} "
                                "failed".format(raw_file)
                            )
                            data = None
                        else:
                            _logger.warning(
                                f"try deducing shape size for {raw_file} "
                                "might be an incorrect "
                                "interpretation"
                            )
        if self.url.data_slice() is None:
            return data
        else:
            return data[self.url.data_slice()]
