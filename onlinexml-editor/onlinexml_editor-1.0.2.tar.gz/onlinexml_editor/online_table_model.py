# Created by matveyev at 19.01.2021,

import pickle
import time

from PyQt5 import QtCore

from onlinexml_editor.devices_class import Node, DeviceNode, SerialDeviceNode, GroupNode
import onlinexml_editor.headers as headers

device_view_role = QtCore.Qt.UserRole + 1


# ----------------------------------------------------------------------
class OnlineModel(QtCore.QAbstractItemModel):

    root_index = QtCore.QModelIndex()
    drag_drop_signal = QtCore.pyqtSignal(str, QtCore.QModelIndex, int, QtCore.QModelIndex)

    # ----------------------------------------------------------------------
    def __init__(self, root=None):
        if root is None:
            root = Node(None, None, None)
        self.root = root
        self._last_num_column = 0
        self._drag_drop_storage = {}
        super(OnlineModel, self).__init__()

    # ----------------------------------------------------------------------
    def supportedDropActions(self):
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction

    # ----------------------------------------------------------------------
    def mimeTypes(self):
        return ['onlineditor/device']

    # ----------------------------------------------------------------------
    def mimeData(self, index):
        if index[0].isValid():
            key = time.time()
            self._drag_drop_storage[key] = index[0]
            mime_data = QtCore.QMimeData()
            mime_data.setData('onlineditor/device', pickle.dumps(key))
            return mime_data

    # ----------------------------------------------------------------------
    def dropMimeData(self, mime_data, action, row, column, parent_index):

        if action == QtCore.Qt.IgnoreAction:
            return True

        dropped_key = pickle.loads(mime_data.data('onlineditor/device'))

        if dropped_key in self._drag_drop_storage:
            dragged_index = self._drag_drop_storage[dropped_key]
            if action == QtCore.Qt.CopyAction:
                self.drag_drop_signal.emit('copy', parent_index, row, dragged_index)
                return True
            elif action == QtCore.Qt.MoveAction:
                self.drag_drop_signal.emit('move', parent_index, row, dragged_index)
                return True

        return False

    # ----------------------------------------------------------------------
    def clear(self):
        if len(self.root.children):
            self.beginRemoveRows(self.root_index, 0, len(self.root.children)-1)
            for row in range(len(self.root.children))[::-1]:
                self.root.remove_child(row)
            self.endRemoveRows()

    # ----------------------------------------------------------------------
    def rowCount(self, parent=None, *args, **kwargs):
        node = self.get_node(parent)
        return node.child_count

    # ----------------------------------------------------------------------
    def columnCount(self, parent=None, *args, **kwargs):
        return len(headers.online_headers)

    # ----------------------------------------------------------------------
    def index(self, row, column, parent=None, *args, **kwargs):
        node = self.get_node(parent)
        return self.createIndex(row, column, node.child(row))

    # ----------------------------------------------------------------------
    def parent(self, index=None):
        node = self.get_node(index)
        if node.parent is None:
            return QtCore.QModelIndex()
        if node.parent == self.root:
            return QtCore.QModelIndex()
        return self.createIndex(node.parent.row, 0, node.parent)

    # ----------------------------------------------------------------------
    def data(self, index, role=QtCore.Qt.DisplayRole):
        node = self.get_node(index)
        return node.data(index.column(), role)

    # ----------------------------------------------------------------------
    def setData(self, index, value, role):
        node = self.get_node(index)
        if role in [QtCore.Qt.EditRole, QtCore.Qt.CheckStateRole]:
            if node.set_data(index.column(), value, role):
                self.dataChanged.emit(index, index)
                return True
        return False

    # ----------------------------------------------------------------------
    def flags(self, index):
        node = self.get_node(index)
        return node.flags(index.column())

    # ----------------------------------------------------------------------
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if headers.online_headers and 0 <= section < len(headers.online_headers):
                return headers.online_headers[section]
            return None
        return super(OnlineModel, self).headerData(section, orientation, role)

    # ----------------------------------------------------------------------
    def get_node(self, index):
        if index and index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self.root

    # ----------------------------------------------------------------------
    def is_single_device(self, index):
        node = self.get_node(index)
        return isinstance(node, DeviceNode) and not isinstance(node.parent, SerialDeviceNode)

    # ----------------------------------------------------------------------
    def is_serial_device(self, index):
        node = self.get_node(index)
        return isinstance(node, SerialDeviceNode)

    # ----------------------------------------------------------------------
    def is_part_or_serial_device(self, index):
        node = self.get_node(index)
        return isinstance(node.parent, SerialDeviceNode)

    # ----------------------------------------------------------------------
    def is_group(self, index):
        node = self.get_node(index)
        return isinstance(node, GroupNode)

    # ----------------------------------------------------------------------
    def remove(self, index):
        node = self.get_node(index)
        self.beginRemoveRows(index.parent(), node.row, node.row)
        if not index.parent().isValid():
            parent_node = self.root
        else:
            parent_node = index.parent().internalPointer()

        parent_node.remove_child(node.row)
        self.endRemoveRows()

    # ----------------------------------------------------------------------
    def start_insert_row(self, insert_index, index=None, row=0):
        if index is not None:
            if index == insert_index:
                row = 0
            else:
                row = self.get_node(index).row
        row = max(0, row)
        self.beginInsertRows(insert_index, row, row)
        return self.get_node(insert_index), row

    # ----------------------------------------------------------------------
    def start_adding_row(self, num_elements, insert_index=0):
        self.beginInsertRows(self.root_index, insert_index, insert_index + num_elements-1)

    # ----------------------------------------------------------------------
    def finish_row_changes(self):
        self.endInsertRows()

    # ----------------------------------------------------------------------
    def filter_row(self, index, value_to_look):
        node = self.get_node(index)
        return node.filter_row(value_to_look)

    # ----------------------------------------------------------------------
    def save_columns_count(self):
        self._last_num_column = self.columnCount()

    # ----------------------------------------------------------------------
    def add_columns(self):
        num_columns = self.columnCount()

        if num_columns > self._last_num_column:
            self.beginInsertColumns(self.root_index, self._last_num_column, num_columns - 1)
            self.endInsertColumns()
        elif num_columns < self._last_num_column:
            self.beginRemoveRows(self.root_index, num_columns, self._last_num_column - 1)
            self.endRemoveColumns()

        self._last_num_column = num_columns


# ----------------------------------------------------------------------
class DeviceModel(OnlineModel):

    def __init__(self):
        super(DeviceModel, self).__init__()

    # ----------------------------------------------------------------------
    def data(self, index, role=QtCore.Qt.DisplayRole):
        node = self.get_node(index)
        return node.data(index.column(), role+device_view_role)

    # ----------------------------------------------------------------------
    def setData(self, index, value, role):
        node = self.get_node(index)
        if role in [QtCore.Qt.EditRole, QtCore.Qt.CheckStateRole]:
            if node.set_data(index.column(), value, role+device_view_role):
                self.dataChanged.emit(index, index)
                return True
        return False

    # ----------------------------------------------------------------------
    def columnCount(self, parent=None, *args, **kwargs):
        return self.root.child_item_count

    # ----------------------------------------------------------------------
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            header_list = self.root.headers
            if header_list and 0 <= section < len(header_list):
                return header_list[section]
            return None
        else:
            return super(DeviceModel, self).headerData(section, orientation, role)


# ----------------------------------------------------------------------
class ProxyDeviceModel(QtCore.QSortFilterProxyModel):

    new_version = True

    # ----------------------------------------------------------------------
    def filterAcceptsRow(self, source_row, source_parent):
        if self.new_version:
            return super(ProxyDeviceModel, self).filterAcceptsRow(source_row, source_parent)
        else:
            match = False
            my_index = self.sourceModel().index(source_row, 0, source_parent)
            for row in range(self.sourceModel().rowCount(my_index)):
                match |= self.filterAcceptsRow(row, my_index)

            match |= super(ProxyDeviceModel, self).filterAcceptsRow(source_row, source_parent)

            return match

    # ----------------------------------------------------------------------
    def get_configs_indexes(self):
        indexes = []
        for row in range(self.sourceModel().rowCount(self.sourceModel().root_index)):
            indexes.append(self.mapFromSource(self.sourceModel().index(row, 0, self.sourceModel().root_index)))

        return indexes
