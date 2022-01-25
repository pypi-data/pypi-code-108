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

__authors__ = ["C. Nemoz", "H. Payno"]
__license__ = "MIT"
__date__ = "23/03/2021"

import logging
import os
from collections import OrderedDict
from silx.gui import qt
from tomwer.core.process.control.scanlist import _ScanList
from tomwer.core.utils import logconfig
from tomwer.gui.qfolderdialog import QScanDialog
from tomwer.gui.control.actions import NXTomomillParamsAction
from tomwer.gui.control.actions import CFGFileActiveLabel
from tomwer.gui.utils.inputwidget import ConfigFileSelector
from tomwer.gui.utils.inputwidget import NXTomomillOutputDirSelector
from nxtomomill import converter as nxtomomill_converter
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.blissscan import BlissScan
from tomwer.core.scan.scanfactory import ScanFactory

try:
    # new HDF5Config class
    from nxtomomill.io.config import TomoHDF5Config as HDF5Config
except ImportError:
    from nxtomomill.io.config import HDF5Config

logger = logging.getLogger(__name__)


class _DataListDialog(qt.QDialog):
    """A simple list of dataset path.BlissHDF5DataListDialog

    .. warning: the widget won't check for scan validity and will only
        emit the path to folders to the next widgets

    :param parent: the parent widget
    """

    sigUpdated = qt.Signal()
    """signal emitted when the list is updated"""

    def __init__(self, parent=None):
        qt.QDialog.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        # add list
        self.datalist = self.createDataList()
        self.layout().addWidget(self.datalist)
        # add buttons
        self._buttons = qt.QDialogButtonBox(parent=self)
        self._addButton = qt.QPushButton("Add", parent=self)
        self._buttons.addButton(self._addButton, qt.QDialogButtonBox.ActionRole)
        self._rmButton = qt.QPushButton("Remove", parent=self)
        self._buttons.addButton(self._rmButton, qt.QDialogButtonBox.ActionRole)
        self._rmAllButton = qt.QPushButton("Remove all", parent=self)
        self._buttons.addButton(self._rmAllButton, qt.QDialogButtonBox.ActionRole)

        self._sendButton = qt.QPushButton("Send", parent=self)
        self._buttons.addButton(self._sendButton, qt.QDialogButtonBox.AcceptRole)
        self.layout().addWidget(self._buttons)

        # expose API
        self._sendList = self.datalist._sendList
        self.setScanIDs = self.datalist.setScanIDs
        self._scheme_title = self.datalist._scheme_title
        self.length = self.datalist.length
        self.selectAll = self.datalist.selectAll
        self.clear = self.datalist.clear

        # connect signal / slot
        self._addButton.clicked.connect(self._callbackAddPath)
        self._rmButton.clicked.connect(self._callbackRemoveFolder)
        self._rmAllButton.clicked.connect(self._callbackRemoveAllFolders)

    def add(self, scan, *args, **kwargs):
        self.datalist.add(scan, *args, **kwargs)
        self.sigUpdated.emit()

    def remove(self, scan):
        self.datalist.remove(scan)
        self.sigUpdated.emit()

    def n_scan(self):
        return len(self.datalist.items)

    def _callbackAddPath(self):
        """ """
        self.sigUpdated.emit()

    def _callbackRemoveFolder(self):
        """ """
        selectedItems = self.datalist.selectedItems()
        toRemove = []
        if selectedItems is not None and len(selectedItems) > 0:
            for item in selectedItems:
                toRemove.append(item.text())
        for scan in toRemove:
            self.remove(scan)
        self.sigUpdated.emit()

    def _callbackRemoveAllFolders(self):
        self.datalist.selectAll()
        self._callbackRemoveFolder()

    def createDataList(self):
        raise NotImplementedError("Base class")


class _BlissConfigDialog(qt.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setLayout(qt.QFormLayout())

        # handle configuration file
        self._configurationWidget = ConfigFileSelector()
        self.layout().addRow("configuration file", self._configurationWidget)
        # handle configuration file
        self._nxTomomillOutputWidget = NXTomomillOutputDirSelector()
        self.layout().addRow("nexus file output dir", self._nxTomomillOutputWidget)

        # buttons
        types = qt.QDialogButtonBox.Ok
        self.__buttons = qt.QDialogButtonBox(parent=self)
        self.__buttons.setStandardButtons(types)
        self.layout().addWidget(self.__buttons)

        self.__buttons.accepted.connect(self.accept)
        self.sigConfigFileChanged = self._configurationWidget.sigConfigFileChanged
        self.sigOutputdirChanged = self._nxTomomillOutputWidget.sigChanged

    def getCFGFilePath(self):
        return self._configurationWidget.getCFGFilePath()

    def setCFGFilePath(self, cfg_file):
        self._configurationWidget.setCFGFilePath(cfg_file)

    def getOutputFolder(self):
        return self._nxTomomillOutputWidget.getOutputFolder()

    def setOutputDialog(self, output_dir):
        self._nxTomomillOutputWidget.setOutputFolder(output_dir)

    def accept(self):
        self.hide()


class BlissHDF5DataListDialog(_DataListDialog):
    """Dialog used to load .h5 only (used when for nxtomomillOW when we need)
    to do a conversion from bliss.h5 to NXtomo"""

    def __init__(self, parent):
        assert isinstance(parent, BlissHDF5DataListMainWindow)
        _DataListDialog.__init__(self, parent)
        self._sendButton.setText("Send all")
        self._sendSelectedButton = qt.QPushButton("Send selected", self)
        self._buttons.addButton(
            self._sendSelectedButton, qt.QDialogButtonBox.AcceptRole
        )

    def createDataList(self):
        return BlissDataList(self)

    def _callbackAddPath(self):
        """ """
        dialog = qt.QFileDialog(self)
        dialog.setNameFilters(["HDF5 file *.h5 *.hdf5 *.nx *.nexus", "nxs"])

        if not dialog.exec_():
            dialog.close()
            return

        filesSelected = dialog.selectedFiles()
        for file_ in filesSelected:
            self.add(file_, configuration=self.parent().getHDF5Config())
        super()._callbackAddPath()


class BlissHDF5DataListMainWindow(qt.QMainWindow):

    sigNXTomoCFGFileChanged = qt.Signal(str)
    """signal emitted when the configuration file change"""

    sigUpdated = qt.Signal()
    """signal emitted when the list of bliss scan to convert change"""

    def __init__(self, parent):
        super().__init__(parent)
        self._widget = BlissHDF5DataListDialog(self)
        # rework BlissHDF5DataListDialog layout
        self._subWidget = qt.QWidget(self)
        self._subWidget.setLayout(qt.QVBoxLayout())
        self._subWidget.layout().addWidget(self._widget.datalist)
        self._subWidget.layout().addWidget(self._widget._buttons)
        self.setCentralWidget(self._subWidget)

        self._dialog = _BlissConfigDialog(self)
        self._dialog.setWindowTitle("Select nxtomomill configuration file")

        # add toolbar
        toolbar = qt.QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(qt.Qt.TopToolBarArea, toolbar)

        # add filtering
        self._parametersAction = NXTomomillParamsAction(toolbar)
        toolbar.addAction(self._parametersAction)
        self._parametersAction.triggered.connect(self._parametersTriggered)

        # toolbar spacer
        spacer = qt.QWidget(toolbar)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        toolbar.addWidget(spacer)

        # add information if cfg file is activate or not
        self._cfgStatusLabel = CFGFileActiveLabel(toolbar)
        toolbar.addWidget(self._cfgStatusLabel)

        # expose API
        self.getCFGFilePath = self._dialog.getCFGFilePath
        self.setCFGFilePath = self._dialog.setCFGFilePath
        self.setScanIDs = self._widget.setScanIDs
        self._sendButton = self._widget._sendButton
        self._sendSelectedButton = self._widget._sendSelectedButton
        self.add = self._widget.add
        self.n_scan = self._widget.n_scan
        self.datalist = self._widget.datalist

        # connect signal / slot
        self._dialog.sigConfigFileChanged.connect(self._cfgFileChanged)
        self._dialog.sigOutputdirChanged.connect(self._propagateUpdateSignal)
        self._widget.sigUpdated.connect(self._propagateUpdateSignal)

    def getOutputFolder(self):
        return self._dialog.getOutputFolder()

    def setOutputFolder(self, output_dir):
        self._dialog.setOutputDialog(output_dir)

    def _propagateUpdateSignal(self):
        self.sigUpdated.emit()

    def _parametersTriggered(self):
        self._dialog.show()
        self._dialog.raise_()

    def _cfgFileChanged(self):
        cfg_file = self._dialog.getCFGFilePath()
        if cfg_file in (None, "") or not os.path.exists(cfg_file):
            self._cfgStatusLabel.setInactive()
        else:
            try:
                HDF5Config.from_cfg_file(cfg_file)
            except Exception:
                self._cfgStatusLabel.setInactive()
            else:
                self._cfgStatusLabel.setActive()
        if cfg_file is None:
            cfg_file = ""
        self.sigNXTomoCFGFileChanged.emit(cfg_file)

    def getHDF5Config(self):
        """Return default HDF5Config or the one created from use input"""
        cfg_file = self._dialog.getCFGFilePath()
        if cfg_file in (None, ""):
            return HDF5Config()
        else:
            try:
                config = HDF5Config.from_cfg_file(cfg_file)
            except Exception:
                return HDF5Config()
            else:
                return config


class GenericDataListDialog(_DataListDialog):
    """Dialog used to load EDFScan or HEDF5 scans"""

    def createDataList(self):
        return GenericDataList(self)

    def _callbackAddPath(self):
        """ """
        dialog = QScanDialog(self, multiSelection=True)
        dialog.setNameFilters(
            [
                "HDF5 files (*.h5 *.hdf5 *.nx *.nexus)",
                "Nexus files (*.nx *.nexus)",
                "Any files (*)",
            ]
        )

        if not dialog.exec_():
            dialog.close()
            return

        files_or_folders = dialog.files_selected()
        for file_or_folder in files_or_folders:
            self.add(file_or_folder)
        super()._callbackAddPath()


class _DataList(_ScanList, qt.QTableWidget):
    def __init__(self, parent):
        _ScanList.__init__(self)
        self._target = None
        qt.QTableWidget.__init__(self, parent)
        self.setRowCount(0)
        self.setColumnCount(1)
        self.setSortingEnabled(True)
        self.verticalHeader().hide()
        if hasattr(self.horizontalHeader(), "setSectionResizeMode"):  # Qt5
            self.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.Stretch)
        else:  # Qt4
            self.horizontalHeader().setResizeMode(0, qt.QHeaderView.Stretch)
        self.setAcceptDrops(True)
        self.items = OrderedDict()

        # QMenu
        self.menu = qt.QMenu(self)
        self._copyAction = qt.QAction("copy")
        self._copyAction.triggered.connect(self._copyRequested)
        self.menu.addAction(self._copyAction)

    def remove_item(self, item):
        """Remove a given folder"""
        del self.items[item.text()]
        itemIndex = self.row(item)
        self.takeItem(itemIndex, 0)
        _ScanList.remove(self, item.text())
        self.removeRow(item.row())
        self.setRowCount(self.rowCount() - 1)
        self._update()

    def remove(self, scan):
        if scan is not None and scan in self.items:
            item = self.items[scan]
            itemIndex = self.row(item)
            self.takeItem(itemIndex, 0)
            _ScanList.remove(self, scan)
            del self.items[scan]
            self.removeRow(item.row())
            self.setRowCount(self.rowCount() - 1)
            self._update()

    def _update(self):
        list_scan = list(self.items.keys())
        self.clear()
        for scan in list_scan:
            self.add(scan)
        self.sortByColumn(0, self.horizontalHeader().sortIndicatorOrder())

    def add(self, d):
        """add the folder or path"""
        raise NotImplementedError("Base class")

    def _addScanIDItem(self, d):
        if "@" not in d and not os.path.isdir(d):
            warning = (
                "Skipping the observation of %s, directory not existing on the system"
                % d
            )
            logger.info(warning, extra={logconfig.DOC_TITLE: self._scheme_title})
        elif d in self.items:
            logger.debug("The path {} is already in the scan list".format(d))
        else:
            row = self.rowCount()
            self.setRowCount(row + 1)

            _item = qt.QTableWidgetItem()
            _item.setText(d)
            _item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
            self.setItem(row, 0, _item)

            self.items[d] = _item

    def setScanIDs(self, scanIDs):
        [self._addScanIDItem(item) for item in scanIDs]
        _ScanList.setScanIDs(self, scanIDs)

    def clear(self):
        """Remove all items on the list"""
        self.items = OrderedDict()
        _ScanList.clear(self)
        qt.QTableWidget.clear(self)
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(["folder"])
        if hasattr(self.horizontalHeader(), "setSectionResizeMode"):  # Qt5
            self.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.Stretch)
        else:  # Qt4
            self.horizontalHeader().setResizeMode(0, qt.QHeaderView.Stretch)

    def dropEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):
            for url in event.mimeData().urls():
                self.add(str(url.path()))

    def supportedDropActions(self):
        """Inherited method to redefine supported drop actions."""
        return qt.Qt.CopyAction | qt.Qt.MoveAction

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):
            event.accept()
            event.setDropAction(qt.Qt.CopyAction)
        else:
            qt.QListWidget.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):
            event.setDropAction(qt.Qt.CopyAction)
            event.accept()
        else:
            qt.QListWidget.dragMoveEvent(self, event)

    def _scanAt(self, point):
        item = self.itemAt(point)
        if item is not None:
            return item.text()

    def contextMenuEvent(self, event):
        self._target = self._scanAt(event.pos())
        if self._target is not None:
            self.menu.exec_(event.globalPos())

    def _copyRequested(self):
        clipboard = qt.QGuiApplication.clipboard()
        clipboard.setText(self._target)


class GenericDataList(_DataList):
    """Data list able to manage directories (EDF/HDF5?) or files (HDF5)"""

    def __init__(self, parent):
        _DataList.__init__(self, parent)
        self.setHorizontalHeaderLabels(["scan"])

    def add(self, path):
        """Add the path folder d in the scan list

        :param d: the path of the directory to add
        :type d: Union[str, TomoBase]
        """
        if isinstance(path, TomwerScanBase):
            scan_obj = _ScanList.add(self, path)
            self._addScanIDItem(str(scan_obj))
        elif os.path.isdir(path):
            scan_obj = _ScanList.add(self, path)
            if scan_obj:
                self._addScanIDItem(str(scan_obj.path))
        else:
            # try to add it as HDF5TomoScan
            try:
                scan_objs = ScanFactory.create_scan_objects(path)
            except Exception as e:
                logger.error(e)
            else:
                if scan_objs is None:
                    return
                for scan in scan_objs:
                    scan_obj = _ScanList.add(self, scan)
                    if scan_obj:
                        self._addScanIDItem(str(scan_obj))


class BlissDataList(_DataList):
    def __init__(self, parent):
        _DataList.__init__(self, parent)
        self.setHorizontalHeaderLabels(["entry@bliss_file.h5"])
        self._configurations = {}

    def _update(self):
        list_scan = list(self.items.keys())
        self.clear()
        for scan in list_scan:
            self.add(scan, configuration=self._configurations.get(scan, None))
        self.sortByColumn(0, self.horizontalHeader().sortIndicatorOrder())

    def remove(self, scan):
        if scan is not None and scan in self.items:
            if str(scan) in self._configurations:
                del self._configurations[str(scan)]
        super().remove(scan=scan)

    def add(self, path, configuration):
        """Add the path folder d in the scan list

        :param d: the path of the directory to add
        :type d: Union[str, TomoBase]
        """
        if "@" in path:
            entry, path = path.split("@")
            possible_entries = [entry]
        else:
            if not BlissScan.is_bliss_file(path):
                msg = qt.QMessageBox(self)
                msg.setIcon(qt.QMessageBox.Warning)
                types = qt.QMessageBox.Ok | qt.QMessageBox.Cancel
                msg.setStandardButtons(types)

                if HDF5TomoScan.is_nexus_nxtomo_file(path):
                    text = (
                        "The input file `{}` seems to contain `NXTomo` entries. "
                        "and no valid `Bliss` valid entry. \n"
                        "This is probably not a Bliss file. Do you still want to "
                        "translate ?".format(path)
                    )
                else:
                    text = (
                        "The input file `{}` does not seems to contain any "
                        "valid `Bliss` entry. \n"
                        "This is probably not a Bliss file. Do you still want to "
                        "translate ?".format(path)
                    )
                msg.setText(text)
                if msg.exec_() != qt.QMessageBox.Ok:
                    return

            try:
                possible_entries = nxtomomill_converter.get_bliss_tomo_entries(
                    path, configuration
                )
            except Exception:
                logger.error("Faild to find entries for {}".format(path))
                possible_entries = []

        for entry in possible_entries:
            scan = HDF5TomoScan(scan=path, entry=entry)
            scan_obj = _ScanList.add(self, scan)
            if scan_obj:
                self._configurations[str(scan_obj)] = configuration
                self._addScanIDItem(str(scan_obj))
