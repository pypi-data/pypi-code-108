# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
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
__date__ = "26/10/2020"


from silx.gui import qt
from tomwer.core.process.edit.imagekeyeditor import IMAGE_KEYS
from typing import Union
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomoscan.esrf.hdf5scan import ImageKey as _ImageKey
import weakref
import functools
from collections.abc import Iterable
import logging

_logger = logging.getLogger(__name__)


class ImageKeyDialog(qt.QDialog):
    """
    Dialog used to tune the ImageKey parameter.
    """

    sigValidated = qt.Signal()
    """Signal send when the user validate the image keys"""

    def __init__(self, parent):
        qt.QDialog.__init__(self, parent)

        self.setLayout(qt.QVBoxLayout())
        self._widget = ImageKeyWindow(self)
        self.layout().addWidget(self._widget)

        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.setStandardButtons(types)
        self.layout().addWidget(self._buttons)

        # signal / slot connection
        self._buttons.button(qt.QDialogButtonBox.Ok).released.connect(
            self._validateReleased
        )
        self._buttons.button(qt.QDialogButtonBox.Ok).setText("validate")
        self._buttons.button(qt.QDialogButtonBox.Cancel).released.connect(
            self._resetReleased
        )
        self._buttons.button(qt.QDialogButtonBox.Cancel).setText("reset")

    def _validateReleased(self, *args, **kwargs):
        self.sigValidated.emit()

    def _resetReleased(self, *args, **kwargs):
        self._widget.reset()

    def getModifications(self):
        """

        :return: list of indexes to be modified
        :rtype: list
        """
        return self._widget.getModifications()

    def setModifications(self, modifications):
        self._widget.setModifications(modifications)

    def setScan(self, scan):
        """

        :param HDF5TomoScan scan: scan to be edited
        """
        self._widget.setScan(scan)


class ImageKeyWindow(qt.QMainWindow):
    def __init__(self, parent):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)

        # dock widget editor
        self._editorControl = _ImageKeyEditor(self)
        self._editorDockWidget = qt.QDockWidget(self)
        self._editorDockWidget.setWidget(self._editorControl)
        self._editorDockWidget.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.TopDockWidgetArea, self._editorDockWidget)

        # main window
        self._mainWindow = _ImageKeyListFiltered(parent=self)
        self.setCentralWidget(self._mainWindow)

        # signal / slot connection
        self._editorControl.sigApply.connect(self._updateModifications)

    def setScan(self, scan) -> None:
        """

        :param HDF5TomoScan scan: scan to be edited
        """
        self._mainWindow.setScan(scan=scan)
        self._editorControl.setScan(scan=scan)

    def _updateModifications(self):
        modifications = self._editorControl.getModifications()
        to_ = self._editorControl.getUpgradeToImagKey()
        self._mainWindow.applyModifications(
            modifications=modifications, new_image_key=to_
        )

    def getModifications(self):
        """

        :return: list of indexes to be modified
        :rtype: list
        """
        return self._mainWindow.getModifications()

    def setModifications(self, modifications):
        self._mainWindow.clearModifcations()
        image_keys_set = set(modifications.values())
        image_keys_set = set(
            [_ImageKey.from_value(image_key) for image_key in image_keys_set]
        )
        for image_key_type in image_keys_set:
            self._mainWindow.applyModifications(
                modifications=modifications, new_image_key=image_key_type
            )

    def reset(self):
        self._mainWindow.reset()


class _ImageKeyEditor(qt.QDialog):

    sigApply = qt.Signal()
    """Signal emitted when the user request to apply the current modifications
    """

    def __init__(self, parent):
        qt.QDialog.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        self.setLayout(qt.QGridLayout())

        # scan name + entry
        self._scanLabel = qt.QLabel("", parent=self)
        self.layout().addWidget(qt.QLabel("scan id"), 0, 0, 1, 1)
        self.layout().addWidget(self._scanLabel, 0, 1, 1, 1)

        # mode selection
        self.layout().addWidget(qt.QLabel("selection mode"), 1, 0, 1, 1)
        self._selectionModeCB = qt.QComboBox(self)
        for mode in ("slice", "list"):
            self._selectionModeCB.addItem(mode)
        self._selectionModeCB.setCurrentIndex(self._selectionModeCB.findText("list"))
        self.layout().addWidget(self._selectionModeCB, 1, 1, 1, 1)

        # image selection
        self._selectionWidget = _EditionSelection(parent=self)
        self.layout().addWidget(self._selectionWidget, 2, 0, 1, 3)

        # upgrade to
        self._upgradeToLabel = qt.QLabel("Upgrade to:", self)
        self._upgradeToLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.layout().addWidget(self._upgradeToLabel, 2, 3, 1, 1)
        self._upgradeToCB = qt.QComboBox(self)
        for image_key in IMAGE_KEYS:
            self._upgradeToCB.addItem(image_key)
        self.layout().addWidget(self._upgradeToCB, 2, 4, 1, 1)

        types = qt.QDialogButtonBox.Ok
        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.setStandardButtons(types)
        self._buttons.button(qt.QDialogButtonBox.Ok).setText(
            "update modifications to apply"
        )
        self.layout().addWidget(self._buttons, 5, 0, 1, 5)
        self._warningLabel = qt.QLabel(
            "!!! `update list` this will only modify key value on the following list. To apply modification you must `validate` those modifications",
            self,
        )
        self._warningLabel.setStyleSheet("font: italic; color: red")
        self._warningLabel.setAlignment(qt.Qt.AlignRight)
        self.layout().addWidget(self._warningLabel, 6, 0, 1, 5)

        # setup
        self._selectionWidget.setSelectionMode(self._selectionModeCB.currentText())

        # connect signal / slot
        self._selectionModeCB.currentTextChanged.connect(
            self._selectionWidget.setSelectionMode
        )
        self._buttons.button(qt.QDialogButtonBox.Ok).clicked.connect(self._apply)

    def getUpgradeToImagKey(self) -> str:
        """

        :return: selected image key as literal
        :rtype: str
        """
        return self._upgradeToCB.currentText()

    def getSelectionMode(self) -> str:
        """

        :return: frame indexes selection mode. Can be 'slice' or 'list'
        """
        return self._selectionModeCB.currentText()

    def getModifications(self) -> list:
        """

        :return: list of indexes to be modified
        :rtype: list
        """
        if self.getSelectionMode() == "slice":
            return self._selectionWidget.getSlice()
        elif self.getSelectionMode() == "list":
            return self._selectionWidget.getList()
        else:
            raise NotImplementedError("Not implemented")

    def _apply(self):
        self.sigApply.emit()

    def setScan(self, scan):
        self._selectionWidget.setScan(scan=scan)
        if scan is not None:
            self._scanLabel.setText(str(scan))
        else:
            self._scanLabel.setText("")


class _SliceSelection(qt.QWidget):
    """
    Widget used to define a set of frames from a range
    """

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())

        # from
        self._fromLabel = qt.QLabel("from: ", self)
        self._fromLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.layout().addWidget(self._fromLabel)
        self._fromQLE = qt.QSpinBox(self)
        self._fromQLE.setRange(0, 1000000)
        self.layout().addWidget(self._fromQLE)
        # to
        self._toLabel = qt.QLabel("to: ", self)
        self._toLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.layout().addWidget(self._toLabel)
        self._toQLE = qt.QSpinBox(self)
        self._toQLE.setRange(0, 1000000)
        self.layout().addWidget(self._toQLE)
        # steps
        self._stepsLabel = qt.QLabel("steps: ", self)
        self._stepsLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.layout().addWidget(self._stepsLabel)
        self._stepsQLE = qt.QSpinBox(self)
        self._stepsQLE.setRange(1, 1000000)
        self.layout().addWidget(self._stepsQLE)

    def getSlice(self) -> slice:
        """

        :return: slice defined
        :rtype: slice
        """
        return slice(self._fromQLE.value(), self._toQLE.value(), self._stepsQLE.value())


class _ListSelection(qt.QWidget):
    """
    Widget to define a list of frames
    """

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self._scan = None
        self.setLayout(qt.QHBoxLayout())

        # list selection
        self._listQLE = qt.QLineEdit("", self)
        self.layout().addWidget(self._listQLE)
        reg_exp = qt.QRegExp(r"(\d+)(,[ ]?\s*\d+)*")
        # list of int with optional space
        validator = qt.QRegExpValidator(reg_exp)
        self._listQLE.setValidator(validator)

        # select button
        self._selectButton = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectButton)

        # signal / slot selection
        self._selectButton.released.connect(self._selectFrames)

    def _selectFrames(self):
        if self._scan is None or self._scan() is None:
            _logger.warning(
                "No scan set or has been moved. Unable to select " "slices from it."
            )
            return
        scan = self._scan()
        dialog = _FrameSelectionDialog(parent=self)
        dialog.setFrames(scan.frames)
        if dialog.exec_():
            frame_indexes = dialog.getSelectedFrameIndexes()
            return self.setList(frame_indexes)

    def getList(self) -> list:
        """

        :return: list of indexes selected
        :rtype: list
        """
        text = self._listQLE.text()
        text = text.replace(" ", "")
        if text == "":
            return []
        else:
            return [int(element) for element in text.split(",")]

    def setList(self, list_: Union[str, Iterable]):
        """

        :param Union[str,Iterable] list_:
        :return:
        """
        if isinstance(list_, str):
            txt = list_
        else:
            txt = ", ".join(str(elmt) for elmt in list_)
        self._listQLE.setText(txt)

    def setScan(self, scan):
        self._scan = weakref.ref(scan)


class _EditionSelection(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        # slice selection
        self._sliceSelection = _SliceSelection(parent=self)
        self.layout().addWidget(self._sliceSelection)

        self._listSelection = _ListSelection(parent=self)
        self.layout().addWidget(self._listSelection)

    def setSelectionMode(self, mode: str) -> None:
        """

        :param str mode: define indexes selection mode. Can be 'slice' or
                         'list'
        """
        assert mode in ("slice", "list")
        self._sliceSelection.setVisible(mode == "slice")
        self._listSelection.setVisible(mode == "list")

    def getList(self) -> list:
        return self._listSelection.getList()

    def getSlice(self) -> slice:
        return self._sliceSelection.getSlice()

    def setScan(self, scan):
        self._listSelection.setScan(scan)


class _ImageKeyList(qt.QTableWidget):
    sigKeyUpdated = qt.Signal(tuple)
    """Signal emitted when a key has been updated. tuple contains
    (frame index, ImageKey)"""

    COLUMNS = (
        "index",
        "current image type",
        "new image type",
    )

    _IMAGE_KEYS_INV = {v: k for k, v in IMAGE_KEYS.items()}

    class ImageKeyComboBox(qt.QComboBox):
        def __init__(self, parent, image_key):
            qt.QComboBox.__init__(self, parent)
            for img_key_type in IMAGE_KEYS:
                self.addItem(img_key_type)
            self.setImageKey(image_key)

        def setImageKey(self, image_key):
            if image_key in _ImageKeyList._IMAGE_KEYS_INV:
                image_key = _ImageKeyList._IMAGE_KEYS_INV[image_key]
            idx = self.findText(image_key)
            assert idx >= 0, "image key not recognized"
            self.setCurrentIndex(idx)

    def __init__(self, parent):
        qt.QTableWidget.__init__(self, parent)
        self._filterMode = None
        self.__frames_modifications = {}
        """contains new and old values"""
        self._imageKeyComboboxes = {}
        """Qt / python needs to keep a pointer on those"""

    def setFilterMode(self, mode: str) -> None:
        """
        Define the filter mode to use and update the QTableWidget

        :param str mode: filtering mode
        """
        self._filterMode = mode
        self.updateFiltering()

    def clear(self) -> None:
        self._imageKeyComboboxes.clear()
        qt.QTableWidget.clear(self)

    def setFrames(self, frames: Iterable, frames_new_keys: dict) -> None:
        """
        Update the QTableWidget for the provided frames

        :param Iterable frames: Iterable of tomoscan.esrf.HDF5TomoScan.Frame
        :param dict frames_new_keys: dictionary with frame edited. key is frame
                                     index. Value is the new `image_key` value
        """
        self.clear()
        self.setRowCount(len(frames))
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.horizontalHeader().setSectionResizeMode(qt.QHeaderView.ResizeToContents)
        self.verticalHeader().hide()

        for i_frame, frame in enumerate(frames):
            # frame index
            index = frame.index
            _item = qt.QTableWidgetItem()
            _item.setText(str(index))
            _item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
            _item.setData(qt.Qt.UserRole, weakref.ref(frame))
            self.setItem(i_frame, 0, _item)

            # current image key
            current_image_key = _ImageKey.from_value(frame.image_key)
            current_image_key = self._IMAGE_KEYS_INV[current_image_key]
            currentImgKeyItem = qt.QLabel(current_image_key, self)
            self.setCellWidget(i_frame, 1, currentImgKeyItem)

            # new image key
            if frame.index in frames_new_keys:
                new_image_key = frames_new_keys[frame.index]
            else:
                new_image_key = frame.image_key
            new_image_key = _ImageKey.from_value(new_image_key)
            new_image_key = self._IMAGE_KEYS_INV[new_image_key]
            newImgKeyItem = self.ImageKeyComboBox(parent=self, image_key=new_image_key)
            self._imageKeyComboboxes[index] = newImgKeyItem
            callback = functools.partial(self.notify_modified, frame.index)
            newImgKeyItem.currentIndexChanged.connect(callback)
            self.setCellWidget(i_frame, 2, newImgKeyItem)
        self.updateFiltering()

    def clearFrameModifications(self) -> None:
        """
        undo modifications
        """
        for frame_index in self.__frames_modifications:
            item_index = self._getFrameRowIndex(frame_index)
            if item_index:
                frame_item = self.item(item_index, 0).data(qt.Qt.UserRole)
                if frame_item() is not None:
                    new_image_key = frame_item().image_key
                    new_image_key = self._IMAGE_KEYS_INV[new_image_key]
                    old = self._imageKeyComboboxes[frame_index].blockSignals(True)
                    self._imageKeyComboboxes[frame_index].setImageKey(new_image_key)
                    self._imageKeyComboboxes[frame_index].blockSignals(old)
        self.__frames_modifications = {}
        self.updateFiltering()

    def applyModifications(
        self, modifications: Iterable, new_image_key: _ImageKey
    ) -> None:
        """
        Update the current QTableWidget with provided modications
        :param modifications: iterable of frame indexes to be modify
        :param new_image_key: new `image_key` value
        """
        if isinstance(modifications, slice):
            sl = modifications
            my_list = list(range(sl.start, sl.stop, sl.step))
        else:
            my_list = modifications
        to_apply = {}
        for frame_index in my_list:
            to_apply[frame_index] = new_image_key
            if frame_index in self._imageKeyComboboxes:
                self._imageKeyComboboxes[frame_index].setImageKey(new_image_key)

        for _, value in to_apply.items():
            assert isinstance(value, _ImageKey), "values should be instance of" + str(
                _ImageKey
            )
        self.__frames_modifications.update(to_apply)
        self.updateFiltering()

    def updateFiltering(self) -> None:
        for i in range(self.rowCount()):
            frame = self.item(i, 0).data(qt.Qt.UserRole)()
            if not frame:
                continue
            if self._filterMode is None:
                return
            if self._filterMode == _ImageKeyListFiltered.ALL_IMG_FILTER:
                visible = True
            elif self._filterMode == _ImageKeyListFiltered.MODIFIED_IMG_FILTER:
                visible = frame.index in self.__frames_modifications
            else:
                visible = frame.image_key == IMAGE_KEYS[self._filterMode]
            if visible:
                self.showRow(i)
            else:
                self.hideRow(i)

    def notify_modified(self, frame_index) -> None:
        """
        Update list of modification and emit sigKeyUpdated

        :param int frame_index:
        """
        frame_row = self._getFrameRowIndex(frame_index)
        if frame_row is not None:
            new_image_key = self._imageKeyComboboxes[frame_index].currentText()
            new_image_key = IMAGE_KEYS[new_image_key]
            self.__frames_modifications[frame_index] = new_image_key
            self.sigKeyUpdated.emit((frame_index, new_image_key))

    def _getFrameRowIndex(self, frame_index):
        for i in range(self.rowCount()):
            frame = self.item(i, 0).data(qt.Qt.UserRole)()
            if frame and frame.index == frame_index:
                return i
        return None

    def getModifications(self):
        return self.__frames_modifications


class _ImageKeyListFiltered(qt.QWidget):

    MODIFIED_IMG_FILTER = "modified"
    ALL_IMG_FILTER = "all"

    sigFilterchanged = qt.Signal()
    """Signal emitted when the filter to apply change"""

    def __init__(self, parent):
        qt.QWidget.__init__(self)
        self.setLayout(qt.QGridLayout())
        """Expected frames type once modifications will be done"""

        # add filter
        self.layout().addWidget(qt.QLabel("image filter:"), 0, 0, 1, 1)
        self._filterCB = qt.QComboBox(self)
        for filter_name in IMAGE_KEYS:
            self._filterCB.addItem(filter_name)
        self._filterCB.addItem(_ImageKeyListFiltered.MODIFIED_IMG_FILTER)
        self._filterCB.addItem(_ImageKeyListFiltered.ALL_IMG_FILTER)
        self.layout().addWidget(self._filterCB)

        # add TableWidget
        self._imageKeyList = _ImageKeyList(self)
        self.layout().addWidget(self._imageKeyList)

        # set up
        self._filterCB.setCurrentIndex(
            self._filterCB.findText(_ImageKeyListFiltered.ALL_IMG_FILTER)
        )
        self._updateFilter()

        # connect signal / slot
        self._filterCB.currentIndexChanged.connect(self._updateFilter)

    def applyModifications(self, modifications: Union[slice, list], new_image_key):
        if new_image_key in IMAGE_KEYS:
            new_image_key = IMAGE_KEYS[new_image_key]
        self._imageKeyList.applyModifications(modifications, new_image_key)

    def reset(self):
        self._imageKeyList.clearFrameModifications()

    def getModifications(self):
        return self._imageKeyList.getModifications()

    def clearModifcations(self):
        self._imageKeyList.clearFrameModifications()

    def getFilerMode(self):
        return self._filterCB.currentText()

    def setScan(self, scan):
        if not isinstance(scan, HDF5TomoScan):
            raise TypeError("scan should be an instance of {}" "".format(HDF5TomoScan))
        self.__frames_modifications = {}
        self._scan = weakref.ref(scan)
        frames = scan.frames
        self._imageKeyList.setFrames(frames, self.__frames_modifications)

    def _updateFilter(self):
        self._imageKeyList.setFilterMode(mode=self.getFilerMode())
        self._imageKeyList.updateFiltering()


class _FrameSelectionDialog(qt.QDialog):
    def __init__(self, parent):
        qt.QDialog.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        # list widget
        self._listWidget = qt.QListWidget(parent=self)
        self._listWidget.setSelectionMode(qt.QAbstractItemView.ExtendedSelection)
        self.layout().addWidget(self._listWidget)
        # add buttons
        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.setStandardButtons(types)
        self.layout().addWidget(self._buttons)

        # connect signal / slot
        self._buttons.button(qt.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self._buttons.button(qt.QDialogButtonBox.Cancel).clicked.connect(self.reject)

    def setFrames(self, frames):
        item_texts = []
        for frame in frames:
            item_texts.append(
                "{index} ({image_key})".format(
                    index=frame.index, image_key=frame.image_key.value
                )
            )
        self._listWidget.addItems(item_texts)

    def getSelectedFrameIndexes(self):
        item_selected = self._listWidget.selectedItems()

        def get_index(my_str):
            return int(my_str.replace(" ", "").split("(")[0])

        return [get_index(item.text()) for item in item_selected]
