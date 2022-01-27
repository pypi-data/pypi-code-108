# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from sympathy.api import qt2 as qt_compat
from sympathy.utils import search
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')


def fuzzy_filter(text):
    """Method returns a regex generated with a fuzzy filter algoritm."""
    return search.fuzzy_free_pattern(text)


class FilterLineEdit(QtWidgets.QWidget):
    filter_changed = qt_compat.Signal()
    """Widget containing a lineedit connected to the creation of filter."""
    def __init__(self, start_exp='', parent=None):
        super(FilterLineEdit, self).__init__(parent)
        self._init_gui(start_exp)

    def _init_gui(self, start_exp):
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(QtCore.QMargins())
        hlayout.setSpacing(10)

        filter_label = QtWidgets.QLabel('Filter:')
        self._filter_lineedit = QtWidgets.QLineEdit()
        self._filter_lineedit.setText(start_exp)

        hlayout.addWidget(filter_label)
        hlayout.addWidget(self._filter_lineedit)

        self._filter_lineedit.textChanged.connect(self._filter_changed)

        self.setLayout(hlayout)

    def filter(self):
        return self._filter

    def set_text(self, text):
        self._filter_lineedit.setText(text)

    def get_text(self):
        return self._filter_lineedit.text()

    def _filter_changed(self, text):
        """Method called when the text in the lineedit is changed."""
        self._filter = fuzzy_filter(text)
        self.filter_changed.emit()


class FilterListView(QtWidgets.QWidget):
    """
    Widget containing a listwiget and filter functionality. The filter
    is used for reduce of the number of items in the listview to make it
    easier for users to search the content.
    """

    def __init__(self, header='', parent=None):
        super(FilterListView, self).__init__(parent)
        self._init_gui(header)

    def _init_gui(self, header):
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setContentsMargins(QtCore.QMargins())

        if header:
            header_label = QtWidgets.QLabel(header)
            vlayout.addWidget(header_label)

        self._filter_widget = FilterLineEdit()
        vlayout.addWidget(self._filter_widget)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.list_widget.setAlternatingRowColors(True)
        vlayout.addWidget(self.list_widget)

        self._filter_widget.filter_changed.connect(self._change_display)

        self.setLayout(vlayout)

    def add_item(self, item):
        self.list_widget.addItem(item)

    def add_items(self, items):
        self.list_widget.addItems(list(items))

    def clear(self):
        self.list_widget.clear()

    def _change_display(self):
        filter_ = self._filter_widget.filter()
        display = [row for row in range(self.list_widget.count())
                   if search.matches(filter_,
                                     self.list_widget.item(row).text())]

        for row in range(self.list_widget.count()):
            if row in display:
                self.list_widget.item(row).setHidden(False)
            else:
                self.list_widget.item(row).setHidden(True)
