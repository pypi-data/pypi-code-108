
import operator
from Qt import QtCore


class ChannelTableModel(QtCore.QAbstractTableModel):

    validation_error = QtCore.Signal(str)

    def __init__(self, parent, *args):
        super(ChannelTableModel, self).__init__(parent, *args)
        self.mylist = []
        self.header = ['code', 'name', 'type', 'eula_required']

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == QtCore.Qt.EditRole:
            return self.mylist[index.row()][self.header[index.column()]]
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.mylist[index.row()][self.header[index.column()]]

    def setData(self, index, value, role):
        if not self.mylist[index.row()][self.header[index.column()]] == value:
            if self.header[index.column()] == 'code':
                value = value.upper()
                if not self._is_code_unique(value):
                    self.validation_error.emit("Code must be unique.\n"
                                               "Channel with code {} already exists.".format(value))
                    return False
            self.mylist[index.row()][self.header[index.column()]] = value
            self.mylist[index.row()]['changed'] = True
        return self.mylist[index.row()][self.header[index.column()]] == value

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if self.header[index.column()] == 'code' and not self.mylist[index.row()].get('new', False):
            return QtCore.QAbstractTableModel.flags(self, index)
        else:
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable)

    def sort(self, col, order):
        self.layoutAboutToBeChanged.emit()
        self.mylist.sort(key=operator.itemgetter(self.header[col]), reverse=(order == QtCore.Qt.DescendingOrder))
        self.layoutChanged.emit()

    def add_channel(self, data, row=None):
        self.layoutAboutToBeChanged.emit()
        if row:
            self.mylist.insert(row, data)
        else:
            self.mylist.append(data)
        self.layoutChanged.emit()

    def delete_row(self, row):
        if not self.mylist[row].get('new', False):
            self.validation_error.emit("Cannot delete channel with code {}".format(self.mylist[row].get('code')))
            return
        self.layoutAboutToBeChanged.emit()
        self.mylist.pop(row)
        self.layoutChanged.emit()

    @property
    def edited_channels(self):
        edited = []
        for row in self.mylist:
            if row.get('changed', False) or row.get('new', False):
                edited.append(row)
        return edited

    def _is_code_unique(self, value):
        for item in self.mylist:
            if item.get('code') == value:
                return False
        return True
