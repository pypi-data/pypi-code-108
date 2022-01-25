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
__date__ = "05/08/2020"


from silx.gui import qt
from tomoscan.io import HDF5File
from silx.gui.data.DataViewerFrame import DataViewerFrame
from silx.gui.dialog.ColormapDialog import ColormapDialog
from silx.gui.data.DataViews import DataViewHooks
from silx.io.utils import get_data
from silx.gui.data.DataViews import IMAGE_MODE
import os
from tomwer.core.scan.scanbase import TomwerScanBase
import logging
from tomwer.core.utils.ftseriesutils import get_vol_file_shape
import weakref
from tomwer.gui.visualization.reconstructionparameters import ReconstructionParameters
import silx
from silx.gui.colors import Colormap
import numpy
import numpy.lib.npyio

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

_logger = logging.getLogger(__name__)


class _ScanInfo(qt.QWidget):
    """Display information about the reconstruction currently displayed"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QFormLayout())
        self._scanQLE = qt.QLineEdit("", self)
        self._scanQLE.setReadOnly(True)
        self.layout().addRow("scan", self._scanQLE)

        self._volumeQLE = qt.QLineEdit("", self)
        self._volumeQLE.setReadOnly(True)
        self.layout().addRow("volume", self._volumeQLE)

    def setScan(self, scan):
        if scan is None:
            self._scanQLE.setText("")
            self._volumeQLE.setText("")
        else:
            assert isinstance(scan, TomwerScanBase)
            self._scanQLE.setText(str(scan))
            if len(scan.latest_vol_reconstructions) == 0:
                self._volumeQLE.setText("")
            else:
                self._volumeQLE.setText(str(scan.latest_vol_reconstructions[0]))

    def clear(self):
        self.setScan(None)


class _TomoApplicationContext(DataViewHooks):
    """
    Store the context of the application

    It overwrites the DataViewHooks to custom the use of the DataViewer for
    the silx view application.

    - Create a single colormap shared with all the views
    - Create a single colormap dialog shared with all the views
    """

    def __init__(self, parent, settings=None):
        self.__parent = weakref.ref(parent)
        self.__defaultColormap = Colormap(name="gray")
        self.__defaultColormapDialog = None
        self.__settings = settings
        self.__recentFiles = []

    def getSettings(self):
        """Returns actual application settings.

        :rtype: qt.QSettings
        """
        return self.__settings

    def restoreLibrarySettings(self):
        """Restore the library settings, which must be done early"""
        settings = self.__settings
        if settings is None:
            return
        settings.beginGroup("library")
        plotBackend = settings.value("plot.backend", "")
        plotImageYAxisOrientation = settings.value("plot-image.y-axis-orientation", "")
        settings.endGroup()

        if plotBackend != "":
            silx.config.DEFAULT_PLOT_BACKEND = plotBackend
        if plotImageYAxisOrientation != "":
            silx.config.DEFAULT_PLOT_IMAGE_Y_AXIS_ORIENTATION = (
                plotImageYAxisOrientation
            )

    def restoreSettings(self):
        """Restore the settings of all the application"""
        settings = self.__settings
        if settings is None:
            return
        parent = self.__parent()
        parent.restoreSettings(settings)

        settings.beginGroup("colormap")
        byteArray = settings.value("default", None)
        if byteArray is not None:
            try:
                colormap = Colormap()
                colormap.restoreState(byteArray)
                self.__defaultColormap = colormap
            except Exception:
                _logger.debug("Backtrace", exc_info=True)
        settings.endGroup()

        self.__recentFiles = []
        settings.beginGroup("recent-files")
        for index in range(1, 10 + 1):
            if not settings.contains("path%d" % index):
                break
            filePath = settings.value("path%d" % index)
            self.__recentFiles.append(filePath)
        settings.endGroup()

    def saveSettings(self):
        """Save the settings of all the application"""
        settings = self.__settings
        if settings is None:
            return
        parent = self.__parent()
        parent.saveSettings(settings)

        if self.__defaultColormap is not None:
            settings.beginGroup("colormap")
            settings.setValue("default", self.__defaultColormap.saveState())
            settings.endGroup()

        settings.beginGroup("library")
        settings.setValue("plot.backend", silx.config.DEFAULT_PLOT_BACKEND)
        settings.setValue(
            "plot-image.y-axis-orientation",
            silx.config.DEFAULT_PLOT_IMAGE_Y_AXIS_ORIENTATION,
        )
        settings.endGroup()

        settings.beginGroup("recent-files")
        for index in range(0, 11):
            key = "path%d" % (index + 1)
            if index < len(self.__recentFiles):
                filePath = self.__recentFiles[index]
                settings.setValue(key, filePath)
            else:
                settings.remove(key)
        settings.endGroup()

    def getRecentFiles(self):
        """Returns the list of recently opened files.

        The list is limited to the last 10 entries. The newest file path is
        in first.

        :rtype: List[str]
        """
        return self.__recentFiles

    def pushRecentFile(self, filePath):
        """Push a new recent file to the list.

        If the file is duplicated in the list, all duplications are removed
        before inserting the new filePath.

        If the list becan bigger than 10 items, oldest paths are removed.

        :param filePath: File path to push
        """
        # Remove old occurencies
        self.__recentFiles[:] = (f for f in self.__recentFiles if f != filePath)
        self.__recentFiles.insert(0, filePath)
        while len(self.__recentFiles) > 10:
            self.__recentFiles.pop()

    def clearRencentFiles(self):
        """Clear the history of the rencent files."""
        self.__recentFiles[:] = []

    def getColormap(self, view):
        """Returns a default colormap.

        Override from DataViewHooks

        :rtype: Colormap
        """
        if self.__defaultColormap is None:
            self.__defaultColormap = Colormap(name="viridis")
        return self.__defaultColormap

    def getColormapDialog(self, view):
        """Returns a shared color dialog as default for all the views.

        Override from DataViewHooks

        :rtype: ColorDialog
        """
        if self.__defaultColormapDialog is None:
            parent = self.__parent()
            if parent is None:
                return None
            dialog = ColormapDialog(parent=parent)
            dialog.setModal(False)
            self.__defaultColormapDialog = dialog
        return self.__defaultColormapDialog


class VolumeViewer(qt.QMainWindow):
    def __init__(self, parent):
        qt.QMainWindow.__init__(self, parent)
        self._centralWidget = DataViewerFrame(parent=self)
        self.__context = _TomoApplicationContext(self)
        self._centralWidget.setGlobalHooks(self.__context)
        self._centralWidget.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding
        )
        self.setCentralWidget(self._centralWidget)
        self._infoWidget = _ScanInfo(parent=self)

        # top level dock widget to display information regarding the scan
        # and volume
        self._dockInfoWidget = qt.QDockWidget(parent=self)
        self._dockInfoWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._dockInfoWidget.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self._dockInfoWidget.setWidget(self._infoWidget)
        self.addDockWidget(qt.Qt.TopDockWidgetArea, self._dockInfoWidget)

        # add dock widget for reconstruction parameters
        self._reconsInfoDockWidget = qt.QDockWidget(parent=self)
        self._reconsWidgetScrollArea = qt.QScrollArea(self)
        self._reconsWidget = ReconstructionParameters(self)
        self._reconsWidgetScrollArea.setWidget(self._reconsWidget)
        self._reconsInfoDockWidget.setWidget(self._reconsWidgetScrollArea)
        self._reconsInfoDockWidget.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._reconsInfoDockWidget)

        self._h5_file = None
        """pointer to the hdf5 file since we want to set the HDF5Dataset for
        loading data on the fly and avoid loading everything into memory for
        hdf5."""
        self.__first_load = True
        self.__last_mode = None

    def _close_h5_file(self):
        if self._h5_file is not None:
            self._h5_file.close()
        self._h5_file = None

    def close(self):
        self._close_h5_file()
        super().close()

    def setScan(self, scan):
        if scan is None:
            self.clear()
        elif len(scan.latest_vol_reconstructions) == 0:
            _logger.warning("No reconstructed volume for {}".format(scan))
            self.clear()
            self._infoWidget.setScan(scan)
        else:
            self._set_data_urls(urls=scan.latest_vol_reconstructions)
            self._infoWidget.setScan(scan)

    def _get_data(self, url):
        if url.file_path().endswith(".vol"):
            data = self._load_vol(url)
        elif url.scheme() == "numpy":
            data = numpy.load(url.file_path())
            if isinstance(data, numpy.lib.npyio.NpzFile):
                data = data["result"]
        elif url.scheme() == "cv2":
            if has_cv2:
                data = cv2.imread(url.file_path(), -1)
            else:
                data = None
                _logger.warning(
                    f"need to install cv2 to read cast file {url.file_path()} because fabio fails to read float16"
                )
        elif url.scheme() == "tomwer":
            if has_PIL:
                data = numpy.array(Image.open(url.file_path()))
                if url.data_slice() is not None:
                    data = data[url.data_slice()]
            else:
                _logger.warning(
                    "need to install Pillow to read file " + url.file_path()
                )
                data = None
        elif url.scheme() == "silx":
            self._h5_file = HDF5File(url.file_path(), mode="r", swmr=True)
            if url.data_path() in self._h5_file:
                data = self._h5_file[url.data_path()]
            else:
                data = None
        else:
            data = get_data(url)
        return data

    def _set_data_urls(self, urls):
        self.clear()
        if len(urls) == 1:
            # for hdf5 we have to be carreful to use the dataset to
            # insure loading on the fly
            url = urls[0]
            data = self._get_data(url)
            # set volume dataset
            if data is not None:
                self._set_volume(data)
            # set reconstruction parameters
            try:
                self._reconsWidget.setUrl(url)
            except Exception as e:
                _logger.info(
                    "Unable to set reconstruction parameters from"
                    " {}. Not handled for pyhst reconstructions. "
                    "Error is {}".format(url, str(e))
                )
        else:
            data = [self._get_data(url) for url in urls]
            data = numpy.array(data)
            self._set_volume(data)

    def _set_volume(self, volume):
        self._centralWidget.setData(volume)
        if self.__first_load:
            self._centralWidget.setDisplayMode(IMAGE_MODE)
            self.__first_load = False
        elif self.__last_mode is not None:
            self._centralWidget.setDisplayMode(self.__last_mode)

    def clear(self):
        self.__last_mode = self._centralWidget.displayMode()
        self._close_h5_file()
        self._centralWidget.setData(None)
        self._infoWidget.clear()

    def sizeHint(self):
        return qt.QSize(600, 600)

    # TODO: should be merged with dataviewer._load_vol function ?
    def _load_vol(self, url):
        """
        load a .vol file
        """
        if url.file_path().lower().endswith(".vol.info"):
            info_file = url.file_path()
            raw_file = url.file_path().replace(".vol.info", ".vol")
        else:
            assert url.file_path().lower().endswith(".vol")
            raw_file = url.file_path()
            info_file = url.file_path().replace(".vol", ".vol.info")

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
                    _logger.warning(f"Raw file {raw_file} is too large for being read")
                else:
                    data = numpy.fromfile(
                        raw_file, dtype=numpy.float32, count=-1, sep=""
                    )
                    try:
                        data = data.reshape(shape)
                    except ValueError:
                        _logger.warning(
                            f"unable to fix shape for raw file {raw_file}. "
                            "Look for information in {info_file}"
                        )
                        try:
                            sqr = int(numpy.sqrt(len(data)))
                            shape = (1, sqr, sqr)
                            data = data.reshape(shape)
                        except ValueError:
                            _logger.info(
                                f"deduction of shape size for {raw_file} " "failed"
                            )
                            data = None
                        else:
                            _logger.warning(
                                f"try deducing shape size for {raw_file} "
                                "might be an incorrect interpretation"
                            )
        if url.data_slice() is None:
            return data
        else:
            return data[url.data_slice()]
