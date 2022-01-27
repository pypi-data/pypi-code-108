# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
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

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

from sylib.report import models


class SelectReportPages(QtWidgets.QWidget):
    def __init__(self, model, parameter_root, parent=None):
        super(SelectReportPages, self).__init__(parent)

        self.parameter_root = parameter_root

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel('Select Pages'))

        if model is not None:
            pages = model.find_all_nodes_with_class(models.Page)
        else:
            pages = []
        icons = []
        for page in pages:
            base64_png = page.thumbnail
            if base64_png is None:
                icons.append(QtGui.QIcon())
                continue
            byte_array = QtCore.QByteArray.fromBase64(
                QtCore.QByteArray(base64_png))
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(byte_array)
            icon = QtGui.QIcon(pixmap)
            icons.append(icon)

        self.data_model = {
            'pages': pages,
            'icons': icons
        }

        self.table_view = PageItemTableView()
        layout.addWidget(self.table_view)

        item_model = PageItemModel(self.data_model)
        self.table_view.setModel(item_model)
        self.table_view.resizeRowsToContents()

        # We are storing tuples with values (uuid, label)
        initially_selected_uuids = []
        for v in parameter_root['selected_pages'].list:
            try:
                initially_selected_uuids.append(v[0])
            except TypeError:
                # For backward compatibility where the value was a list of
                # row numbers.
                if v < len(pages):
                    initially_selected_uuids.append(pages[v].uuid)
        initially_selected_uuids = list(set(initially_selected_uuids))
        current_uuids = [p.uuid for p in pages]
        selected_rows = [current_uuids.index(x)
                         for x in initially_selected_uuids
                         if x in current_uuids]
        for row in selected_rows:
            self.table_view.selectRow(row)

        # Listen to changes. Store reference to selection model to avoid
        # segfault in PySide.
        self.selection_model = self.table_view.selectionModel()
        self.selection_model.selectionChanged.connect(
            self.handle_selection_changed)

    def handle_selection_changed(self, selected, deselected):
        uuid_list = []
        for index in self.selection_model.selectedIndexes():
            page = self.data_model['pages'][index.row()]
            uuid_list.append((page.uuid, page.label))
        self.parameter_root['selected_pages'].list = uuid_list


class PageItemTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(PageItemTableView, self).__init__(parent)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(True)
        self.setShowGrid(False)
        self.setGridStyle(QtCore.Qt.NoPen)
        self.setIconSize(QtCore.QSize(64, 64))
        self.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection)

    def setModel(self, item_model):
        super(PageItemTableView, self).setModel(item_model)


class PageItemModel(QtCore.QAbstractTableModel):
    def __init__(self, data_model, parent=None):
        super(PageItemModel, self).__init__(parent)

        self.data_model = data_model

    def rowCount(self, parent_index=QtCore.QModelIndex()):
        return len(self.data_model['pages'])

    def columnCount(self, parent_index=QtCore.QModelIndex()):
        return 1

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return 'Page'
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return '{}'.format(section + 1)
        return None

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return self.data_model['pages'][index.row()].label
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                icon = self.data_model['icons'][index.row()]
                return icon
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
