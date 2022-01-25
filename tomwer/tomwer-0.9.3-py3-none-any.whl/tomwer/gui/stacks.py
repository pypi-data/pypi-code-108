# /*##########################################################################
# Copyright (C) 2017 European Synchrotron Radiation Facility
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
"""Some widget construction to check if a sample moved"""

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "19/03/2018"


from silx.gui import qt
from tomwer.gui.stackplot import _QImageFileStackPlot
from tomwer.core.scan.edfscan import EDFTomoScan
from collections import OrderedDict
from tomwer.gui.qfolderdialog import QScanDialog
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
import logging
import h5py
import os

_logger = logging.getLogger(__name__)


class _ImageStack(qt.QMainWindow):
    """
    This widget will make copy or virtual link to all received *slice* files
    in order to group them all in one place and be able to browse those
    (using the image stack of view in orange or a third software as silx view)

    Options are:
       - copy files or create sym link (set to sym link)
       - overwrite if existing (set to False)

    Behavior:
        When the process receives a new data path ([scanPath]/[scan]) and if
        no output folder has been defined manually them it will try to create
        the folder [scanPath]/slices if not existing in order to redirect
        the slices files.
        If fails will ask for a directory.
        If the output folder is already existing then move directly to the
        copy.
    """

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        self._scans = set()
        self._viewer = _QImageFileStackPlot(parent=self)
        self._viewer.addFolderName(True)
        self.setCentralWidget(self._viewer)

        self._viewer.getControlWidget().hide()

        self._dockWidgetMenu = qt.QDockWidget(parent=self)
        self._dockWidgetMenu.layout().setContentsMargins(0, 0, 0, 0)
        self._dockWidgetMenu.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self._dockWidgetMenu.setWidget(self._viewer.getControlWidget())
        self.addDockWidget(qt.Qt.BottomDockWidgetArea, self._dockWidgetMenu)

        toolbar = qt.QToolBar()
        self.addToolBar(qt.Qt.RightToolBarArea, toolbar)

        self._clearAction = _ClearAction(parent=toolbar)
        toolbar.addAction(self._clearAction)
        self._clearAction.triggered.connect(self.clear)

        self._addAction = _AddAction(parent=toolbar)
        toolbar.addAction(self._addAction)
        self._addAction.triggered.connect(self._addNewFolder)
        # expose API
        self.setLoadingMode = self._viewer.setLoadingMode
        self.setForceSync = self._viewer.setForceSync

        self.setLoadingMode("lazy loading")

    def addLeafScan(self, scanID):
        if isinstance(scanID, TomwerScanBase):
            self._scans.add(scanID.path)
        else:
            assert type(scanID) is str
            self._scans.add(scanID)
        self._update()

    def _addNewFolder(self):
        dialog = QScanDialog(self, multiSelection=True)

        if not dialog.exec_():
            dialog.close()
            return

        for folder in dialog.filesSelected():
            assert os.path.isdir(folder)
            self.addLeafScan(folder)

    def removeLeafScan(self, scanID):
        self._scans.remove(scanID)
        self._update()

    def extractImages(self):
        """
        Parse all self._scans and find the images to be displayed on the widget

        :return: images to display for each scan
        :rtype: dict
        """
        raise NotImplementedError("Base class")

    def _update(self):
        all_images = self.extractImages()
        all_images = OrderedDict(sorted(all_images.items()))
        ordered_imgs = []
        for scan in all_images:
            try:
                oScanSlices = OrderedDict(sorted(all_images[scan].items()))
                for slice in oScanSlices:
                    ordered_imgs.append(all_images[scan][slice])
            except TypeError:
                # in case algorithm could extract recons index
                ordered_imgs = ordered_imgs + list(all_images[scan].values())
        self._viewer.setImages(ordered_imgs)

    def clear(self):
        self._scans = set()
        self._viewer.clear()


class _ClearAction(qt.QAction):
    def __init__(self, parent):
        style = qt.QApplication.instance().style()
        icon = style.standardIcon(qt.QStyle.SP_DialogResetButton)
        qt.QAction.__init__(self, icon, "Clear", parent)


class _AddAction(qt.QAction):
    def __init__(self, parent):
        style = qt.QApplication.instance().style()
        icon = style.standardIcon(qt.QStyle.SP_DirIcon)
        qt.QAction.__init__(self, icon, "Add", parent)


class SliceStack(_ImageStack):
    """
    Widget displaying all slices contained in a list of acquisition folder
    """

    def extractImages(self):
        """
        Parse all self._scans and find the images to be displayed on the widget

        :return: images to display for each scan
        :rtype: dict
        """
        slices = {}
        for scan in self._scans:
            # TODO: should also work for hdf5 files. Call ScanFactory ?
            imgs = EDFTomoScan.get_reconstructions_paths(scan, withIndex=True)
            if len(imgs) > 0:
                slices[scan] = imgs
        return slices


class RadioStack(_ImageStack):
    """
    Widget displaying all radio contained in a list of acquisition folder
    """

    def extractImages(self):
        """
        Parse all self._scans and find the images to be displayed on the widget

        :return: images to display for each scan
        :rtype: dict
        """
        slices = {}
        for scan in self._scans:
            # manage hdf5
            if h5py.is_hdf5(scan):
                try:
                    scans = ScanFactory.create_scan_objects(scan_path=scan)
                except Exception as e:
                    _logger.warning(e)
                else:
                    for scan_ in scans:
                        imgs = scan_.projections
                        if len(imgs) > 0:
                            slices[str(scan_)] = imgs
            else:
                # manage edf
                try:
                    scan_ = ScanFactory.create_scan_object(scan_path=scan)
                except ValueError:
                    pass
                else:
                    imgs = scan_.projections
                    if len(imgs) > 0:
                        slices[scan] = imgs
        return slices
