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
from collections import OrderedDict
from silx.gui.widgets.TableWidget import TableWidget
from silx.io.url import DataUrl
import enum
import functools
import logging
import os

logger = logging.getLogger(__file__)


class ColumnMode(enum.Enum):
    SINGLE = ("single",)
    SINGLE_OR_NONE = ("single_or_none",)
    MULTIPLE = ("multiple",)
    MULTIPLE_OR_NONE = ("multiple_or_none",)


_DEFAULT_COLUMNS = OrderedDict(
    {("img B", ColumnMode.SINGLE), ("img A", ColumnMode.SINGLE)}
)


class UrlSelectionTable(TableWidget):
    """Table used to select the color channel to be displayed for each"""

    sigSelectionChanged = qt.Signal(dict)
    """Signal emitted when the a image selection changed
    Contains column id and the list of url selected (or None if none selected)
    """

    def __init__(self, parent=None, columns=_DEFAULT_COLUMNS):
        TableWidget.__init__(self, parent)
        self.selection_columns = columns
        self.clear()

    def clear(self):
        qt.QTableWidget.clear(self)
        self.setRowCount(0)
        self._column_index = OrderedDict({"url": 0})
        for i, column in enumerate(self.selection_columns):
            self._column_index[column] = i + 1

        self.setColumnCount(len(self._column_index))
        self.setHorizontalHeaderLabels(list(self._column_index.keys()))
        self.verticalHeader().hide()
        if hasattr(self.horizontalHeader(), "setSectionResizeMode"):  # Qt5
            self.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.Stretch)
        else:  # Qt4
            self.horizontalHeader().setResizeMode(0, qt.QHeaderView.Stretch)

        self.setSortingEnabled(True)
        self._checkBoxes = {}
        self._url_path_to_url = {}

    def setUrls(self, urls):
        self.clear()
        self.setRowCount(len(urls))
        for iUrl, url in enumerate(urls):
            self.addUrl(url=url, row=iUrl, resize=False)
        self.sortItems(0)
        self.resizeColumnsToContents()

    def addUrl(self, url, row=None, resize=False, **kwargs):
        """

        :param url:
        :param args:
        :return: index of the created items row
        :rtype int
        """
        assert isinstance(url, DataUrl)
        if row is None:
            row = self.rowCount()
            self.setRowCount(row + 1)

        _item = qt.QTableWidgetItem()
        _item.setText(os.path.basename(url.path()))
        _item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
        self.setItem(row, self._column_index["url"], _item)

        self._checkBoxes[url.path()] = {}
        # work for now since we are in a 'single' edf mode but will fail in the
        # future
        self._url_path_to_url[url.path()] = url
        for column_name in self.selection_columns:
            widgetImg = qt.QRadioButton(parent=self)
            widgetImg.setAutoExclusive(False)
            self.setCellWidget(row, self._column_index[column_name], widgetImg)
            callbackImg = functools.partial(self._selection_changed, column_name, url)
            widgetImg.toggled.connect(callbackImg)
            self._checkBoxes[url.path()][column_name] = widgetImg
        if resize is True:
            self.resizeColumnsToContents()
        return row

    def _selection_changed(self, column_name, url, toggle):
        column_mode = self.selection_columns[column_name]
        if toggle is True and column_mode in (
            ColumnMode.SINGLE,
            ColumnMode.SINGLE_OR_NONE,
        ):
            for tmp_url in self._checkBoxes:
                for tmp_column in self._checkBoxes[tmp_url]:
                    self._checkBoxes[tmp_url][tmp_column].blockSignals(True)
            self._set_column_selection(column=column_name, selection=[url])
            for tmp_url in self._checkBoxes:
                for tmp_column in self._checkBoxes[tmp_url]:
                    self._checkBoxes[tmp_url][tmp_column].blockSignals(False)

        # force a selection if need to have at least one and selection is empty
        # for now
        if toggle is False:
            if (
                column_mode
                in (
                    ColumnMode.SINGLE,
                    ColumnMode.MULTIPLE,
                )
                and self._has_no_element(column_name)
            ):
                for tmp_url in self._checkBoxes:
                    for tmp_column in self._checkBoxes[tmp_url]:
                        self._checkBoxes[tmp_url][tmp_column].blockSignals(True)
                selection = [url]
                self._set_column_selection(column=column_name, selection=selection)
                for tmp_url in self._checkBoxes:
                    for tmp_column in self._checkBoxes[tmp_url]:
                        self._checkBoxes[tmp_url][tmp_column].blockSignals(False)

    def _has_no_element(self, column):
        for url_path in self._checkBoxes:
            if self._checkBoxes[url_path][column].isChecked():
                return False
        return True

    def _updatecheckBoxes(self, whichImg, name):
        old = self.blockSignals(True)

        assert name in self._checkBoxes
        assert whichImg in self._checkBoxes[name]
        if self._checkBoxes[name][whichImg].isChecked():
            for radioUrl in self._checkBoxes:
                if radioUrl != name:
                    self._checkBoxes[radioUrl.path()][whichImg].setChecked(False)
        self.blockSignals(old)

    def getSelectedUrls(self, name=None):
        """

        :return: url selected for the requested name. Or full selection if no
                 name selected.
        """
        selection = {}
        for _name in self.selection_columns:
            selection[_name] = None

        for radioUrl in self._checkBoxes:
            for _name in self.selection_columns:
                if self._checkBoxes[radioUrl][_name].isChecked():
                    if selection[_name] is None:
                        selection[_name] = []
                    selection[_name].append(self._url_path_to_url[radioUrl])
        if name is None:
            return selection
        else:
            return selection[name]

    def setSelectedUrls(self, selection):
        """

        :param ddict: key: image url, values: list of active channels
        """
        assert isinstance(selection, dict)
        for name, sel in selection.items():
            assert isinstance(sel, (type(None), list, tuple))
            self._set_column_selection(column=name, selection=sel)
        self._signal_selection_changed()

    def _clear_column(self, column):
        """

        :param str column:
        """
        old = self.blockSignals(True)
        for radioUrl in self._checkBoxes:
            self._checkBoxes[radioUrl][column].setChecked(False)
        self.blockSignals(old)

    def _set_column_selection(self, column, selection):
        """

        :param str column: id of the column
        :param Union[None, list]: None or list of DataUrl
        """
        self._clear_column(column=column)
        old = self.blockSignals(True)
        if selection is not None:
            assert isinstance(selection, (list, tuple))
            for sel in selection:
                if sel is not None:
                    assert isinstance(sel, DataUrl)
                    self._checkBoxes[sel.path()][column].setChecked(True)
        self.blockSignals(old)

    def _signal_selection_changed(self):
        self.sigSelectionChanged.emit(self.getSelectedUrls())

    def removeUrl(self, url):
        raise NotImplementedError("")


class UrlSelectionDialog(qt.QDialog):
    """Embed the UrlSelectionWidget into a QDialog"""

    _sizeHint = qt.QSize(500, 500)

    def __init__(self, columns, parent=None):
        qt.QDialog.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self.widget = UrlSelectionTable(columns=columns, parent=self)
        self.layout().addWidget(self.widget)

        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        self._buttons = qt.QDialogButtonBox(parent=self)
        self._buttons.setStandardButtons(types)
        self.layout().addWidget(self._buttons)

        # connect signal / SLOT
        self._buttons.button(qt.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self._buttons.button(qt.QDialogButtonBox.Cancel).clicked.connect(self.reject)

        # expose API
        self.setUrls = self.widget.setUrls
        self.addUrl = self.widget.addUrl
        self.setSelection = self.widget.setSelectedUrls
        self.getSelection = self.widget.getSelectedUrls

    def sizeHint(self):
        """Return a reasonable default size for usage in :class:`PlotWindow`"""
        return self._sizeHint
