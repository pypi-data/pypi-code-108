# /*##########################################################################
# Copyright (C) 2016-2017 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
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
#############################################################################*/

__author__ = ["P. Paleo", "H. Payno"]
__license__ = "MIT"
__date__ = "24/05/2016"

from silx.gui import qt
from silx.gui.plot import Plot2D
from . import utils
from tomwer.gui import settings
import numpy
import os
from collections import OrderedDict
import tomwer.resources
from .imagefromfile import ImageFromFile, FileWithImage, _Image
from silx.gui.plot.actions import PlotAction
from silx.gui.plot.actions.control import YAxisInvertedAction
from silx.io.url import DataUrl
import logging
from tomwer.gui import icons
import functools
import time
from collections import namedtuple, Iterable

logger = logging.getLogger(__name__)


class _QImageStackPlot(qt.QWidget):
    """
    Widget to display a stack of image

    :param parent: the Qt parent widget
    """

    _sizeHint = qt.QSize(400, 400)

    IMG_LOADING = numpy.load(
        tomwer.resources._resource_filename(
            "%s.%s" % ("hourglass", "npy"),
            default_directory=os.path.join("gui", "icons"),
        )
    )

    def __init__(self, parent, sliderVertical=False):
        qt.QWidget.__init__(self, parent)
        self._transpose = False
        """If we want to transpose the image like imagj by default"""

        self.images = self.createStackImageInstance()
        layout = qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        mainwidget = qt.QWidget(self)
        mainLayout = qt.QHBoxLayout() if sliderVertical else qt.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainwidget.setLayout(mainLayout)
        layout.addWidget(mainwidget)

        self._plot = Plot2D(self)

        def find_y_inverted(actions):
            for act in actions:
                if isinstance(act, YAxisInvertedAction):
                    return act
            return None

        y_inverted = find_y_inverted(self._plot.toolBar().actions())
        if y_inverted is None:
            # temporary, XAxisInverted should be embed into silx.
            pos = min(8, len(self._plot.toolBar().actions()))
            y_inverted = self._plot.toolBar().actions()[-pos]
        self.axis_invert = XAxisInvertedAction(plot=self._plot)
        self._plot.toolBar().insertAction(y_inverted, self.axis_invert)

        self._plot.setYAxisInverted(settings.Y_AXIS_DOWNWARD)
        if hasattr(self._plot, "setAxesDisplayed"):
            # by default we want to have a full screen display
            self._plot.setAxesDisplayed(False)

        colormap = self._plot.getDefaultColormap()
        if type(colormap) is dict:
            colormap["autoscale"] = True
        else:
            assert hasattr(colormap, "setVRange")
            colormap.setVRange(None, None)
        self._plot.setDefaultColormap(colormap)
        self._plot.setKeepDataAspectRatio(True)

        # removing some plot action to clear toolbar
        self._plot.getMaskAction().setVisible(False)
        self._plot.getCopyAction().setVisible(False)
        # if has the option medianFilter, active it
        if hasattr(self._plot, "getMedianFilter2DAction"):
            self._plot.getMedianFilter2DAction().setVisible(True)

        mainLayout.addWidget(self._plot)

        if sliderVertical is True:
            lLayout = qt.QVBoxLayout()
        else:
            lLayout = qt.QHBoxLayout()

        self._controlWidget = qt.QWidget(self)
        self._controlWidget.setLayout(lLayout)
        lLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self._controlWidget)

        self._qspinbox = qt.QSpinBox(parent=self._controlWidget)
        self._qslider = qt.QSlider(
            qt.Qt.Vertical if sliderVertical is True else qt.Qt.Horizontal,
            parent=self._controlWidget,
        )
        self.setRange(0, 0)
        self._qslider.setTickPosition(qt.QSlider.TickPosition(0))
        if sliderVertical:
            lLayout.addWidget(self._qspinbox)
            lLayout.addWidget(self._qslider)
        else:
            lLayout.addWidget(self._qslider)
            lLayout.addWidget(self._qspinbox)
        self._connectControls()
        self.setLayout(layout)

        self.setImages(None)
        self.getActiveImage = self._plot.getActiveImage

    def _disconnectControls(self):
        self._qspinbox.valueChanged.disconnect(self.showImage)
        self._qslider.valueChanged.disconnect(self.showImage)

    def setTranspose(self, value):
        if self._transpose != value:
            self._transpose = value
            img = self._plot.getActiveImage()
            if img is not None:
                data = numpy.transpose(img.getData())
                img.setData(data)

    def _connectControls(self):
        self._qspinbox.valueChanged.connect(self.showImage)
        self._qslider.valueChanged.connect(self.showImage)

    def sizeHint(self):
        """Return a reasonable default size for usage in :class:`PlotWindow`"""
        return self._sizeHint

    def setImages(self, images):
        """
        Set the images to display
        """
        self._qslider.blockSignals(True)
        self._qspinbox.blockSignals(True)

        self.images.clear()
        if images is None:
            self._plot.clear()
            if self._qslider:
                self._qslider.setRange(0, 0)
                self._qspinbox.setRange(0, 0)
            return
        else:
            if isinstance(images, (list, tuple)):
                self.images.setImages(images)
            else:
                assert isinstance(images, (dict, OrderedDict))
                _images = OrderedDict(sorted(images.items(), key=lambda t: t[0]))
                self.images.setImages(_images.values())
            if self.images.size() > 0:
                self.showImage(0)

            if self._qslider:
                if self.images.size() > 0:
                    self.setRange(0, self.images.size())
                else:
                    self.setRange(0, 0)
            if self.images.size() > 0:
                self.showImage(self._qspinbox.value())

        self._qslider.blockSignals(False)
        self._qspinbox.blockSignals(False)

    def createStackImageInstance(self):
        return _StackImage()

    def showImage(self, index):
        """
        Show the image of index 'index' as the current image displayed

        :param int index: the index of the image to display.
        """
        self._qspinbox.blockSignals(True)
        self._qslider.blockSignals(True)
        # update gui
        self._qspinbox.setValue(index)
        self._qslider.setValue(index)
        image = self.images.getImage(index)
        if image is not None:
            if image.data is not None:
                data = image.data
                if self._transpose is True:
                    data = numpy.transpose(data)
                if self.axis_invert.isInverted() is True:
                    data = numpy.fliplr(data)
                self._plot.addImage(data=data, legend=str(index), replace=True)
                self._updateImageInfo()
            else:
                image.load()
        self._qspinbox.blockSignals(False)
        self._qslider.blockSignals(False)

    def setImage(self, index, data):
        """
        Set the given data as the image for the given index

        :param int index: the index of the image to set
        :param numpy.ndarray data: the image
        """
        _data = data
        if data is None:
            _data = self.IMG_NOT_FOUND
        self.images[index] = _data

    def isEmpty(self):
        """

        :return bool: True if no reconstruction has been set yet
        """
        return self.images.empty()

    def clear(self):
        self.setImages(None)

    def setRange(self, _min, _max):
        """Set the range of the spin box

        :param _min: the minimal value of the slice. If equal None, not set
        :param _max: the maximal value of the slice. If equal None, not set
        """
        self._qslider.setRange(_min, _max)
        self._qspinbox.setRange(_min, _max)

    def getControlWidget(self):
        return self._controlWidget

    def _updateImageInfo(self):
        pass


class _QImageFileStackPlot(_QImageStackPlot):
    """
    Widget based on QImageStackPlot but managing images from a stack of path to
    file
    """

    def __init__(self, parent):
        """
        Constructor

        :param parent: the Qt parent widget
        """
        _QImageStackPlot.__init__(self, parent)

        self._loadingMode = _LoadingModeToolButton(parent=self)
        self.getControlWidget().layout().addWidget(self._loadingMode)
        self.addFolderName(False)
        self.clear()

        # connect the qslider with the GUI
        self._sliderConnected = False

        style = qt.QApplication.style()
        self.waitingIcon = style.standardIcon(qt.QStyle.SP_BrowserReload)

        # add some toolbar information
        self._qslider.setToolTip(
            "The loading of the image will start when the \
            slider will be released"
        )
        self._qspinbox.setToolTip(
            "To start the loading press enter on the spin\
             box or release the slider"
        )

        self.layout().addWidget(self.__buildFileInfo())

        self._loadingMode.sigLoadModeChanged.connect(self.setLoadingMode)
        self.setImages(None)

        # expose API
        self.setForceSync = self.images.setForceSync

        # connect signal / slot
        self.images.sigImageLoaded.connect(self._updateIfCurrent)
        self.images.sigLoadingModeChanged.connect(self._loadingModeChanged)
        self._openWithImjButton.released.connect(self._openCurrentInImagej)

    def getLoadingMode(self):
        return self.images.getLoadingMode()

    def setLoadingMode(self, mode):
        self._loadingMode.blockSignals(True)
        self._loadingMode.setLoadingMode(mode)
        self.images.setLoadingMode(mode)
        self.showImage(self._qslider.value())
        self._loadingMode.blockSignals(False)

    def _loadingModeChanged(self, mode, old_mode):
        self._loadingMode.blockSignals(True)
        self._disconnectModeControl(old_mode)
        self._loadingMode.setLoadingMode(mode)
        self._connectModeControl(mode)
        self._loadingMode.blockSignals(False)

    def __buildFileInfo(self):
        self._fileInfoWidget = qt.QWidget(parent=self)
        layout = qt.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._fileInfoWidget.setLayout(layout)

        # file name label
        layout.addWidget(qt.QLabel("file :", self._fileInfoWidget), 0, 0, 1, 1)
        self._qlFileName = qt.QLabel("", parent=self._fileInfoWidget)
        layout.addWidget(self._qlFileName, 0, 1, 1, 2)

        # open in image j button
        style = qt.QApplication.style()
        open_icon = style.standardIcon(qt.QStyle.SP_FileLinkIcon)
        self._openWithImjButton = qt.QPushButton(
            open_icon, "open with ImageJ", parent=self
        )
        self._openWithImjButton.setSizePolicy(
            qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum
        )
        layout.addWidget(self._openWithImjButton, 0, 3, 1, 1)

        # date last modification
        layout.addWidget(
            qt.QLabel("last modification :", self._fileInfoWidget), 1, 0, 1, 1
        )
        self._qlLastModifications = qt.QLabel("", parent=self._fileInfoWidget)
        layout.addWidget(self._qlLastModifications, 1, 1, 1, 2)

        return self._fileInfoWidget

    def _disconnectControls(self):
        self._disconnectModeControl(self.getLoadingMode())

    def _connectControls(self):
        self._connectModeControl(self.getLoadingMode())

    def _disconnectModeControl(self, mode):
        if mode == LAZY_LOADING:
            self._qslider.sliderReleased.disconnect(self.changeActiveImageFrmQSlider)
            self._qspinbox.editingFinished.disconnect(self.changeActiveImageFrmQSpinBox)
        else:
            self._qslider.valueChanged.disconnect(self.changeActiveImageFrmQSlider)
            self._qspinbox.valueChanged.disconnect(self.changeActiveImageFrmQSpinBox)

    def _connectModeControl(self, mode):
        if mode == LAZY_LOADING:
            self._qslider.sliderReleased.connect(self.changeActiveImageFrmQSlider)
            self._qspinbox.editingFinished.connect(self.changeActiveImageFrmQSpinBox)
        elif mode in (ON_SHOW_LOADING, ASAP_LOADING):
            self._qslider.valueChanged.connect(self.changeActiveImageFrmQSlider)
            self._qspinbox.valueChanged.connect(self.changeActiveImageFrmQSpinBox)

    def setLoadingImage(self, sliceNb):
        """Set the status of the image to not loaded"""
        self.setImage(sliceNb, _QImageFileStackPlot.IMG_LOADING)

    def setImages(self, imagesFiles):
        """
        Set the stack of images files

        :param _imagesFiles: the list of images path to be displayed
        """
        self._qslider.blockSignals(True)
        self._qspinbox.blockSignals(True)
        _QImageStackPlot.setImages(self, imagesFiles)

        self._qslider.setRange(0, self.images.size() - 1)
        self._qspinbox.setMaximum(self.images.size() - 1)

        self._qslider.blockSignals(False)
        self._qspinbox.blockSignals(False)

    def _openCurrentInImagej(self):
        active_image = self._getActiveImageInfo()
        if active_image is None:
            logger.warning("No active image defined")
        else:
            try:
                utils.open_url_with_image_j(active_image.url)
            except OSError as e:
                msg = qt.QMessageBox(self)
                msg.setIcon(qt.QMessageBox.Warning)
                msg.setWindowTitle("Unable to open image in imagej")
                msg.setText(str(e))
                msg.exec_()

    def _getActiveImageInfo(self):
        imageIndex = self._qslider.value()
        return self.images.getImage(imageIndex)

    def _updateImageInfo(self):
        def slice_to_string(data_slice):
            if data_slice == Ellipsis:
                return "..."
            elif data_slice == slice(None):
                return ":"
            elif isinstance(data_slice, int):
                return str(data_slice)
            else:
                raise TypeError("Unexpected slicing type. Found %s" % type(data_slice))

        image = self._getActiveImageInfo()
        if image is not None:
            imageName = image.url.file_path()
            if self._joinFolderName is True:
                firstFolder = os.path.split(os.path.dirname(imageName))[-1]
                imageName = os.path.join(firstFolder, os.path.basename(imageName))
            else:
                imageName = os.path.basename(imageName)
            if image.url.data_path() is not None:
                imageName = imageName + "&path=" + image.url.data_path()
            if image.url.data_slice() is not None:
                if isinstance(image.url.data_slice(), Iterable):
                    data_slice = [slice_to_string(s) for s in image.url.data_slice()]
                else:
                    data_slice = slice_to_string(image.url.data_slice())
                imageName = imageName + "&slice=" + ",".join(data_slice)

            self._qlFileName.setText(imageName)
            self._qlFileName.setToolTip(image.url.path())
            try:
                last_mod = time.ctime(os.path.getmtime(image.url.file_path()))
            except Exception:
                last_mod = ""
            self._qlLastModifications.setText(last_mod)

    def addFolderName(self, b):
        """

        :param bool val: If true then will join the folder name of the file in
                         addition of the file name.
        """
        self._joinFolderName = b

    def _updateIfCurrent(self, url):
        indexFile = self._qslider.value()
        index = self.images.getUrlIndex(url)
        if index == indexFile:
            self.changeActiveImageFrmQSlider()

    def changeActiveImageFrmQSlider(self):
        indexFile = self._qslider.value()
        self.showImage(indexFile)

    def changeActiveImageFrmQSpinBox(self):
        indexFile = self._qspinbox.value()
        self.showImage(indexFile)

    def getImage(self, index):
        return self._imagesFiles[index]

    def createStackImageInstance(self):
        return _StackImageToLoad()

    def clear(self):
        if hasattr(self, "_qlFileName"):
            self._qlFileName.setText("")
        super(_QImageFileStackPlot, self).clear()


class _StackImage(object):
    def __init__(self, images):
        _images = images
        if _images is None:
            _images = {}
        self._images = OrderedDict(_images)
        """Key: unique index or label or path, Value: _Image"""
        self.nextIndex = 0

    def addImage(self, image):
        assert isinstance(image, _Image)
        self._images[self.nextIndex] = image
        self.nextIndex = self.nextIndex + 1

    def getImage(self, index):
        if index not in self._images:
            return None
        else:
            return self._images[index]

    def size(self):
        return len(self._images)

    def clear(self):
        self._images.clear()
        self.nextIndex = 0


LAZY_LOADING = "lazy loading"
ASAP_LOADING = "load ASAP"
ON_SHOW_LOADING = "load when show requested"

LOADING_MODES = (LAZY_LOADING, ASAP_LOADING, ON_SHOW_LOADING)


class _StackImageToLoad(_StackImage, qt.QObject):
    """
    Define a set of images that can be already loaded or that can be loaded on
    demand
    """

    sigImageLoaded = qt.Signal(str)
    """Signal emitted when an image is loaded. Param is url_path"""
    sigLoadingModeChanged = qt.Signal(str, str)
    """Signal emitted when the loading mode is changed. Parameter are new mode,
    old mode"""

    def __init__(self, loadingMode=LAZY_LOADING):
        assert loadingMode in (LAZY_LOADING, ASAP_LOADING, ON_SHOW_LOADING)
        _StackImage.__init__(self, images=None)
        qt.QObject.__init__(self)
        self._mode = loadingMode
        self._url_to_index = {}
        self._force_sync = False

    def getUrlIndex(self, _url):
        """return the url position on the stack if registred"""
        _url_path = _url
        if isinstance(_url_path, DataUrl):
            _url_path = _url_path.path()
        if _url_path in self._url_to_index:
            return self._url_to_index[_url_path]
        else:
            return None

    def clear(self):
        for img in self._images.values():
            img.sigLoaded.disconnect(self._loaded)
        _StackImage.clear(self)
        self._url_to_index.clear()

    def addImage(self, image):
        if isinstance(image, ImageFromFile):
            image_ = image
        elif isinstance(image, DataUrl):
            image_ = ImageFromFile(url=image)
        else:
            raise TypeError("Unmanaged type:" + type(image))
        self._url_to_index[image_.url.path()] = self.nextIndex
        _StackImage.addImage(self, image_)
        image_.sigLoaded.connect(self._loaded)
        if self._mode == ASAP_LOADING:
            image_.load(self._force_sync)

    def setImages(self, images):
        """

        :param list or tuple images: manage ImageFromFile or file pats (as str)
        """
        self.clear()
        for img in images:
            if type(img) is str:
                self.addFile(_file=img)
            else:
                self.addImage(img)

    def setFiles(self, files):
        self.clear()
        for _file in files:
            self.addFile(_file=_file)

    def addFile(self, _file):
        _fileWithImage = FileWithImage(_file)
        _imagesFiles = _fileWithImage.getImages(_load=self._mode == ASAP_LOADING)
        if _imagesFiles is None:
            return
        for imgFile in _imagesFiles:
            self.addImage(imgFile)

    def setLoadingMode(self, mode):
        assert mode in LOADING_MODES
        old = self._mode
        self._mode = mode
        self.sigLoadingModeChanged.emit(mode, old)
        if self._mode == ASAP_LOADING:
            self._loadAllImages()

    def getLoadingMode(self):
        return self._mode

    def _loadAllImages(self):
        for imgIndex, img in self._images.items():
            img.load_recons_params(self._force_sync)

    def _loaded(self, url_path):
        self.sigImageLoaded.emit(url_path)

    def setForceSync(self, value):
        self._force_sync = value


_loadingModeState = namedtuple("_loadingModeState", ["icon", "state", "action"])


class _LoadingModeToolButton(qt.QToolButton):
    """Tool button to switch keep aspect ratio of a plot"""

    sigLoadModeChanged = qt.Signal(str)

    def __init__(self, parent=None):
        super(_LoadingModeToolButton, self).__init__(parent=parent)

        self._states = {
            ON_SHOW_LOADING: _loadingModeState(
                icon=icons.getQIcon("low_speed"),
                state="load data only when requiring",
                action="will load data only when requiring",
            ),
            LAZY_LOADING: _loadingModeState(
                icon=icons.getQIcon("medium_low_speed"),
                state="load data when seems convenient",
                action="will load data when seems convenient",
            ),
            ASAP_LOADING: _loadingModeState(
                icon=icons.getQIcon("high_speed"),
                state="load data as soon as possible",
                action="will load data as soon as possible",
            ),
        }

        onShowLoadingMode = self._createAction(ON_SHOW_LOADING)
        fctOSL = functools.partial(self.setLoadingMode, ON_SHOW_LOADING)
        onShowLoadingMode.triggered.connect(fctOSL)

        lazyLoadingMode = self._createAction(LAZY_LOADING)
        fctLL = functools.partial(self.setLoadingMode, LAZY_LOADING)
        lazyLoadingMode.triggered.connect(fctLL)

        asapLoadingMode = self._createAction(ASAP_LOADING)
        fctAL = functools.partial(self.setLoadingMode, ASAP_LOADING)
        asapLoadingMode.triggered.connect(fctAL)

        menu = qt.QMenu(self)
        menu.addAction(onShowLoadingMode)
        menu.addAction(lazyLoadingMode)
        menu.addAction(asapLoadingMode)
        self.setMenu(menu)
        self.setPopupMode(qt.QToolButton.InstantPopup)

        self.setLoadingMode(ON_SHOW_LOADING)

    def _createAction(self, loadingMode):
        icon = self._states[loadingMode].icon
        text = self._states[loadingMode].action
        return qt.QAction(icon, text, self)

    def setLoadingMode(self, loadingMode):
        assert loadingMode in LOADING_MODES
        icon = self._states[loadingMode].icon
        toolTip = self._states[loadingMode].state
        self.setIcon(icon)
        self.setToolTip(toolTip)
        self.sigLoadModeChanged.emit(loadingMode)


class XAxisInvertedAction(PlotAction):
    """QAction controlling X orientation on a :class:`.PlotWidget`.

    :param plot: :class:`.PlotWidget` instance on which to operate
    :param parent: See :class:`QAction`
    """

    def __init__(self, plot, parent=None):
        # Uses two images for checked/unchecked states
        self._states = {
            False: (icons.getQIcon("plot-xleft"), "Orient X axis left"),
            True: (icons.getQIcon("plot-xright"), "Orient X axis right"),
        }

        self._inverted = False
        icon, tooltip = self._states[self.isInverted()]
        super(XAxisInvertedAction, self).__init__(
            plot,
            icon=icon,
            text="Invert X Axis",
            tooltip=tooltip,
            triggered=self._actionTriggered,
            checkable=False,
            parent=parent,
        )

    def _xAxisInvertedChanged(self, inverted):
        """Handle Plot set y axis inverted signal"""
        icon, tooltip = self._states[inverted]
        self.setIcon(icon)
        self.setToolTip(tooltip)

    def _actionTriggered(self, checked=False):
        self._inverted = not self._inverted
        icon, tooltip = self._states[self.isInverted()]
        # this only work for images
        self.setIcon(icon)
        self.setToolTip(tooltip)

        # flip the current data
        data = self.plot.getActiveImage()
        if data:
            data_array = numpy.fliplr(data.getData())
            data.setData(data_array)

    def isInverted(self):
        return self._inverted
