import re
import functools

from qtpy import QtGui, QtWidgets, QtCore
from qtpy.QtCore import Signal

from ._qt import load_ui
from .plot import NDScopePlotChannel

# ------------------------------------------------------------------------------

COLOR_TESTPOINT = 'blue'
COLOR_ONLINE = 'green'


def brush_for_channel(channel):
    if channel.testpoint:
        return QtGui.QBrush(QtGui.QColor(COLOR_TESTPOINT))
    elif channel.online:
        return QtGui.QBrush(QtGui.QColor(COLOR_ONLINE))
    else:
        return QtGui.QBrush()

# ------------------------------------------------------------------------------

def is_slow(sample_rate):
    return sample_rate <= 16

def is_fast(sample_rate):
    return not is_slow(sample_rate)

# ------------------------------------------------------------------------------

def filter_channel(channel, show_slow, show_fast, show_online_only):
    if show_online_only and not channel.online:
        return False
    else:
        if show_slow and is_slow(channel.sample_rate):
            return True
        elif show_fast and is_fast(channel.sample_rate):
            return True
        else:
            return False

# ------------------------------------------------------------------------------

# modified from https://github.com/pyside/Examples/blob/master/examples/itemviews/simpletreemodel/simpletreemodel.py


class AvailableChannelTreeBranchItem:
    def __init__(self, column_data, parent=None):
        self.column_data = column_data
        self.parent = parent
        self.flags = (QtCore.Qt.ItemIsEnabled, QtCore.Qt.NoItemFlags, QtCore.Qt.NoItemFlags)
        self.channel_name_part_dict = {}
        self.channel_name_dict = {}
        self.has_slow = False
        self.has_slow_online = False
        self.has_fast = False
        self.has_fast_online = False
        self.is_leaf = False

    def getChild(self, row):
        return (list(self.channel_name_part_dict.values()) + list(self.channel_name_dict.values()))[row]

    def getChildCount(self):
        return len(self.channel_name_part_dict) + len(self.channel_name_dict)

    def getColumnCount(self):
        return len(self.column_data)

    def getData(self, column, role):
        if role == QtCore.Qt.DisplayRole:
            try:
                return self.column_data[column]
            except IndexError:
                return QtCore.QVariant()
        else:
            return QtCore.QVariant()

    def getFlags(self, column):
        try:
            return self.flags[column]
        except IndexError:
            return QtCore.Qt.NoItemFlags

    def getParent(self):
        return self.parent

    def getRow(self):
        if self.parent:
            return (list(self.parent.channel_name_part_dict.values()) + list(self.parent.channel_name_dict.values())).index(self)
        else:
            return 0


class AvailableChannelTreeLeafItem:
    def __init__(self, channel, parent):
        self.channel = channel
        self.parent = parent
        self.column_data = (channel.name, str(channel.sample_rate))
        self.flags = (
            (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemNeverHasChildren),
            (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemNeverHasChildren),
        )
        self.is_leaf = True

    def getChild(self, row):
        return None

    def getChildCount(self):
        return 0

    def getColumnCount(self):
        return len(self.column_data)

    def getData(self, column, role):
        if role == QtCore.Qt.DisplayRole:
            try:
                return self.column_data[column]
            except IndexError:
                return QtCore.QVariant()
        elif role == QtCore.Qt.ForegroundRole:
            return brush_for_channel(self.channel)
        else:
            return QtCore.QVariant()

    def getFlags(self, column):
        try:
            return self.flags[column]
        except IndexError:
            return QtCore.Qt.NoItemFlags

    def getParent(self):
        return self.parent

    def getRow(self):
        if self.parent:
            return (list(self.parent.channel_name_part_dict.values()) + list(self.parent.channel_name_dict.values())).index(self)
        else:
            return 0


class AvailableChannelTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, channel_list, max_depth=4, parent=None):
        super().__init__(parent)
        column_data = ('name', 'rate')
        self.root = AvailableChannelTreeBranchItem(column_data)
        self.max_depth = max_depth
        for channel in channel_list:
            self.insert(channel)

    def insert(self, channel):
        current = self.root
        channel_name_part_list = re.split('[:\-_]', channel.name, self.max_depth)
        for channel_name_part in channel_name_part_list[:-1]:
            column_data = (channel_name_part, '')
            current = current.channel_name_part_dict.setdefault(channel_name_part, AvailableChannelTreeBranchItem(column_data, current))
            if is_slow(channel.sample_rate):
                current.has_slow = True
                if channel.online:
                    current.has_slow_online = True
            else:
                current.has_fast = True
                if channel.online:
                    current.has_fast_online = True
        current.channel_name_dict[channel.name] = AvailableChannelTreeLeafItem(channel, current)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().getColumnCount()
        return self.root.getColumnCount()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.ForegroundRole]:
            item = index.internalPointer()
            return item.getData(index.column(), role)
        return QtCore.QVariant()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        item = index.internalPointer()
        return item.getFlags(index.column())

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.root.column_data[section]
        return QtCore.QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if not parent.isValid():
            parent_item = self.root
        else:
            parent_item = parent.internalPointer()
        child_item = parent_item.getChild(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QtCore.QModelIndex()

    def itemFromIndex(self, index):
        return index.internalPointer()

    def mimeData(self, indexes):
        text_list = [self.data(index, QtCore.Qt.DisplayRole) for index in indexes if index.isValid()]
        text = '\n'.join(text_list)
        mime_data = QtCore.QMimeData()
        mime_data.setText(text)
        return mime_data

    def mimeTypes(self):
        return ['text/plain']

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        child_item = index.internalPointer()
        parent_item = child_item.getParent()
        if parent_item == self.root:
            return QtCore.QModelIndex()
        return self.createIndex(parent_item.getRow(), 0, parent_item)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parent_item = self.root
        else:
            parent_item = parent.internalPointer()
        return parent_item.getChildCount()


# Filters the branch and leaf items based on the sample rate and online status
# of the channels that they contain.
class AvailableChannelTreeSortFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.show_slow = True
        self.show_fast = True
        self.show_online_only = False

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        item = index.internalPointer()
        if item.is_leaf:
            channel = item.channel
            return filter_channel(channel, self.show_slow, self.show_fast, self.show_online_only)
        else:
            if self.show_online_only:
                if self.show_slow and item.has_slow_online:
                    return True
                elif self.show_fast and item.has_fast_online:
                    return True
                else:
                    return False
            else:
                if self.show_slow and item.has_slow:
                    return True
                elif self.show_fast and item.has_fast:
                    return True
                else:
                    return False

class AvailableChannelTreeView(QtWidgets.QTreeView):
    def __init__(self, parent):
        super().__init__(parent)

# ------------------------------------------------------------------------------


class AvailableChannelTableModel(QtCore.QAbstractTableModel):
    def __init__(self, channel_list, parent=None):
        super().__init__(parent)
        self.search_pattern = ''
        self.show_slow = True
        self.show_fast = True
        self.show_online_only = False

        self.full_channel_list = channel_list
        self.filtered_channel_list = channel_list
        self.header_data = ('name', 'rate')

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.header_data)

    def data(self, index, role):
        try:
            channel = self.itemFromIndex(index)
        except IndexError:
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return (channel.name, str(channel.sample_rate))[index.column()]
        elif role == QtCore.Qt.ForegroundRole:
            return brush_for_channel(channel)
        else:
            return QtCore.QVariant()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        try:
            return (
                (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemNeverHasChildren),
                (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemNeverHasChildren),
            )[index.column()]
        except IndexError:
            return QtCore.Qt.NoItemFlags

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header_data[section]
        elif orientation == QtCore.Qt.Vertical:
            return section + 1
        else:
            return QtCore.QVariant()

    def itemFromIndex(self, index):
        return self.filtered_channel_list[index.row()]

    def mimeData(self, indexes):
        text_list = [self.data(index, QtCore.Qt.DisplayRole) for index in indexes if index.isValid()]
        text = '\n'.join(text_list)
        mime_data = QtCore.QMimeData()
        mime_data.setText(text)
        return mime_data

    def mimeTypes(self):
        return ['text/plain']

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.filtered_channel_list)

    def update_filter(self):
        filtered_channel_list = []
        for channel in self.full_channel_list:
            if self.search_pattern.upper() in channel.name.upper():
                if filter_channel(channel, self.show_slow, self.show_fast, self.show_online_only):
                    filtered_channel_list.append(channel)

        self.beginResetModel()
        self.filtered_channel_list = filtered_channel_list
        self.endResetModel()


class AvailableChannelTableView(QtWidgets.QTableView):
    def __init__(self, parent):
        super().__init__(parent)

# ------------------------------------------------------------------------------


class PushButtonDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self):
        super().__init__()

    def paint(self, painter, option, index):
        button = QtWidgets.QStyleOptionButton()
        button.text = '-'
        button.rect = option.rect
        button.rect.setWidth(min(option.rect.width(), 30))
        button.state = QtWidgets.QStyle.State_Enabled
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_PushButton, button, painter)


class SelectedChannelTableModel(QtCore.QAbstractTableModel):
    # items in table are NDScopePlotChannel items.  setItemList
    # expects a list of PlotChannel objects, but all other
    # inserts/append operations expect channel name strings.

    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_list = []
        self.header = ('', 'name', 'color', 'width', 'scale', 'offset', 'unit')

    def __contains__(self, name):
        """check that channel name already in table or not"""
        for channel in self.item_list:
            if channel.channel == name:
                return True
        return False

    def _make_item(self, name):
        """make a table item from a channel name string"""
        return NDScopePlotChannel(name)

    def canDropMimeData(self, data, action, row, column, parent):
        return data.hasFormat('text/plain')

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.header)

    def data(self, index, role):
        try:
            item = self.item_list[index.row()]
        except IndexError:
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            column_data = (
                '',
                item.channel,
                '',
                item.params['width'],
                item.params['scale'],
                item.params['offset'],
                item.params['unit'],
            )
            return column_data[index.column()]
        elif role == QtCore.Qt.ForegroundRole:
            return QtGui.QBrush()
        elif role == QtCore.Qt.BackgroundRole and index.column() == 2:
            return item.get_QColor()
        elif role == QtCore.Qt.ToolTipRole and index.column() == 0:
            return 'remove channel'
        else:
            return QtCore.QVariant()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        try:
            return (
                (QtCore.Qt.ItemNeverHasChildren),
                (QtCore.Qt.ItemNeverHasChildren),
                (QtCore.Qt.ItemNeverHasChildren),
                (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemNeverHasChildren),
                (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemNeverHasChildren),
                (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemNeverHasChildren),
                (QtCore.Qt.ItemNeverHasChildren),
            )[index.column()]
        except IndexError:
            return QtCore.Qt.NoItemFlags

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[section]
        elif orientation == QtCore.Qt.Vertical:
            return section + 1
        else:
            return QtCore.QVariant()

    def dropMimeData(self, data, action, row, column, parent):
        if data.hasFormat('text/plain'):
            text = data.text()
            text_list = text.splitlines()

            item_list = [self._make_item(text) for text in text_list if text not in self]
            count = len(item_list)

            if count > 0:
                if row == -1 and column == -1:
                    if not parent.isValid():
                        # Drop is after last row.
                        row = len(self.item_list)
                        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
                        for i in range(count):
                            self.item_list.insert(row + i, item_list[i])
                        self.endInsertRows()
                        return True
                    else:
                        # Drop is on row.
                        row = parent.row()
                        self.item_list[row] = item_list.pop(0)
                        row = row + 1
                        count = count - 1
                        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
                        for i in range(count):
                            self.item_list.insert(row + i, item_list[i])
                        self.endInsertRows()
                        return True
                elif row >= 0 and column >= 0:
                    # Drop is before first row or between rows.
                    self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
                    for i in range(count):
                        self.item_list.insert(row + i, item_list[i])
                    self.endInsertRows()
                    return True
                else:
                    return False
            else:
                return False

    def mimeData(self, indexes):
        text_list = [self.data(index, QtCore.Qt.DisplayRole) for index in indexes if index.isValid()]
        text = '\n'.join(text_list)
        mime_data = QtCore.QMimeData()
        mime_data.setText(text)
        return mime_data

    def mimeTypes(self):
        return ['text/plain']

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.item_list)

    def supportedDropActions(self):
        return (QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

    def getItemList(self):
        """get list of PlotChannel objects in the table"""
        return self.item_list

    def setItemList(self, item_list):
        """set the list of PlotChannel objects in the table"""
        self.item_list = item_list

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if count <= 0 or row < 0 or (row + count) > self.rowCount(parent):
            return False
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
        for i in range(count):
            del self.item_list[row + i]
        self.endRemoveRows()
        return True

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        return self.removeRows(row, 1, parent)

    def setData(self, index, value, role):
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() == 3:
                if value > 0:
                    self.item_list[index.row()].set_params(width=value)
                    self.dataChanged.emit(index, index, [role])
                    return True
                else:
                    return False
            elif index.column() == 4:
                self.item_list[index.row()].set_params(scale=value)
                self.dataChanged.emit(index, index, [role])
                return True
            elif index.column() == 5:
                self.item_list[index.row()].set_params(offset=value)
                self.dataChanged.emit(index, index, [role])
                return True
            else:
                return False
        else:
            return False

    def setItemData(self, index, roles):
        if QtCore.Qt.EditRole in roles.keys():
            return self.setData(index, roles[QtCore.Qt.EditRole], QtCore.Qt.EditRole)
        elif QtCore.Qt.DisplayRole in roles.keys():
            return self.setData(index, roles[QtCore.Qt.DisplayRole], QtCore.Qt.DisplayRole)
        else:
            return False

    def add_channel(self, name):
        """add a channel to the table by name"""
        if name in self:
            return
        row = len(self.item_list)
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.item_list.insert(row, self._make_item(name))
        self.endInsertRows()


class SelectedChannelTableView(QtWidgets.QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        self.color_dialog = QtWidgets.QColorDialog()
        self.clicked.connect(self.clicked_slot)

    def clicked_slot(self, index):
        if index.column() == 0:
            model = self.model()
            model.removeRow(index.row())
        elif index.column() == 2:
            model = self.model()
            item = model.item_list[index.row()]
            color = item.get_QColor()
            self.color_dialog.setCurrentColor(color)
            self.color_dialog.colorSelected.connect(lambda color: self.color_selected_slot(color, item))
            self.color_dialog.show()

    def color_selected_slot(self, color, item):
        self.color_dialog.colorSelected.disconnect()
        item.set_params(color=color.name())

# ------------------------------------------------------------------------------


class ChannelListWidget(*load_ui('channel_list.ui')):

    def __init__(self, available_channel_tree_model, available_channel_table_model, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # available channel tree model
        self.available_channel_tree_model = available_channel_tree_model
        self.available_channel_tree_proxy_model = AvailableChannelTreeSortFilterProxyModel()
        self.available_channel_tree_proxy_model.setSourceModel(self.available_channel_tree_model)

        # available channel tree view
        self.available_channel_tree_view.setModel(self.available_channel_tree_proxy_model)
        self.available_channel_tree_view.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.available_channel_tree_view.header().setSectionsMovable(False)
        self.available_channel_tree_view.setDragEnabled(True)
        self.available_channel_tree_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # available channel table model
        self.available_channel_table_model = available_channel_table_model

        # available channel table view
        self.available_channel_table_view.setModel(self.available_channel_table_model)
        self.available_channel_table_view.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.available_channel_table_view.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.available_channel_table_view.horizontalHeader().setHighlightSections(False)
        self.available_channel_table_view.setDragEnabled(True)
        self.available_channel_table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.available_channel_table_view.setWordWrap(False)

        self.all_radio_button.toggled.connect(self.all_radio_button_toggled_slot)
        self.slow_radio_button.toggled.connect(self.slow_radio_button_toggled_slot)
        self.fast_radio_button.toggled.connect(self.fast_radio_button_toggled_slot)

        self.online_checkbox.setStyleSheet('color: {0}'.format(COLOR_ONLINE))
        self.online_checkbox.stateChanged.connect(self.online_checkbox_state_changed_slot)

        self.search_line_edit.textChanged.connect(self.search_line_edit_text_changed_slot)
        self.search_line_edit.setClearButtonEnabled(True)
        self.search_line_edit.setFocus()

        # FIXME: this is a substitute (possibly) for logic that should
        # maybe be based on whether we're talking to an NDS1 or NDS2
        # server.  for NDS1 everything is online, and there are
        # testpoints (which are also online only), so a checkbox to
        # filter on online is superfulous.
        all_online = functools.reduce(
            lambda value, chan: value and chan.online,
            self.available_channel_table_model.full_channel_list,
            True,
        )
        if all_online:
            self.online_checkbox.hide()
            self.legendLabel.setText(f"<span style='color: {COLOR_TESTPOINT}'>testpoints in blue</span>")
        else:
            self.legendLabel.hide()

    def search_line_edit_text_changed_slot(self, text):
        self.available_channel_table_model.search_pattern = text
        self.available_channel_table_model.update_filter()

    def all_radio_button_toggled_slot(self, checked):
        if checked:
            self.available_channel_tree_proxy_model.show_slow = True
            self.available_channel_tree_proxy_model.show_fast = True
            self.available_channel_tree_proxy_model.invalidateFilter()

            self.available_channel_table_model.show_slow = True
            self.available_channel_table_model.show_fast = True
            self.available_channel_table_model.update_filter()

    def slow_radio_button_toggled_slot(self, checked):
        if checked:
            self.available_channel_tree_proxy_model.show_slow = True
            self.available_channel_tree_proxy_model.show_fast = False
            self.available_channel_tree_proxy_model.invalidateFilter()

            self.available_channel_table_model.show_slow = True
            self.available_channel_table_model.show_fast = False
            self.available_channel_table_model.update_filter()

    def fast_radio_button_toggled_slot(self, checked):
        if checked:
            self.available_channel_tree_proxy_model.show_slow = False
            self.available_channel_tree_proxy_model.show_fast = True
            self.available_channel_tree_proxy_model.invalidateFilter()

            self.available_channel_table_model.show_slow = False
            self.available_channel_table_model.show_fast = True
            self.available_channel_table_model.update_filter()

    def online_checkbox_state_changed_slot(self, state):
        if state == QtCore.Qt.Unchecked:
            self.available_channel_tree_proxy_model.show_online_only = False
            self.available_channel_tree_proxy_model.invalidateFilter()

            self.available_channel_table_model.show_online_only = False
            self.available_channel_table_model.update_filter()
        elif state == QtCore.Qt.Checked:
            self.available_channel_tree_proxy_model.show_online_only = True
            self.available_channel_tree_proxy_model.invalidateFilter()

            self.available_channel_table_model.show_online_only = True
            self.available_channel_table_model.update_filter()


class ChannelSelectWidget(*load_ui('channel_select.ui')):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # selected channel table model
        self.selected_channel_table_model = SelectedChannelTableModel()

        # selected channel table view
        self.selected_channel_table_view.setModel(self.selected_channel_table_model)
        self.selected_channel_table_view.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.selected_channel_table_view.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.selected_channel_table_view.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.selected_channel_table_view.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.selected_channel_table_view.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.selected_channel_table_view.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.selected_channel_table_view.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        self.selected_channel_table_view.horizontalHeader().setHighlightSections(False)
        self.selected_channel_table_view.setDragEnabled(True)
        self.selected_channel_table_view.setAcceptDrops(True)
        self.selected_channel_table_view.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.selected_channel_table_view.setDragDropOverwriteMode(False)
        self.selected_channel_table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.selected_channel_table_view.setWordWrap(False)
        self.push_button_delegate = PushButtonDelegate()
        self.selected_channel_table_view.setItemDelegateForColumn(0, self.push_button_delegate)

    def set_channel_list(self, channel_list):
        self.selected_channel_table_model.setItemList(channel_list)

    def add_channel(self, channel):
        self.selected_channel_table_model.add_channel(channel)

    def get_channel_list(self):
        return self.selected_channel_table_model.getItemList()


class ChannelSelectDialog(*load_ui('channel_select_dialog.ui')):

    done = Signal('PyQt_PyObject')

    def __init__(self, channel_list_widget, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.channel_list_widget = channel_list_widget
        self.channel_list_widget.setParent(self)
        self.panel_layout.insertWidget(0, self.channel_list_widget)
        self.channel_list_widget.available_channel_tree_view.activated.connect(self.available_channel_tree_view_activated_slot)
        self.channel_list_widget.available_channel_table_view.activated.connect(self.available_channel_table_view_activated_slot)

        self.channel_select_widget = ChannelSelectWidget()
        self.channel_select_widget.setParent(self)
        self.panel_layout.insertWidget(1, self.channel_select_widget)

        self.infoLabel.setText(f"Douple click or drag channels to select.")

        self.dialog_button_box.accepted.connect(self._done_accepted)
        self.dialog_button_box.rejected.connect(self._done_rejected)

    def setSelectedChannelList(self, channel_dict):
        self.channel_select_widget.set_channel_list(list(channel_dict.values()))

    def getSelectedChannelList(self):
        return self.channel_select_widget.get_channel_list()

    def setTitlePlot(self, plot):
        self.title.setText(f"Select/configure channels for plot {plot}")

    # Appends the item in the available channel tree at the supplied
    # index to the end of the selected channel table.
    def available_channel_tree_view_activated_slot(self, index):
        if not self.channel_list_widget.available_channel_tree_proxy_model.hasChildren(index) and index.column() == 0:
            source_index = self.channel_list_widget.available_channel_tree_proxy_model.mapToSource(index)
            item = self.channel_list_widget.available_channel_tree_proxy_model.sourceModel().itemFromIndex(source_index)
            if item.is_leaf:
                self.channel_select_widget.add_channel(item.channel.name)

    # Appends the item in the available channel table at the supplied
    # index to the end of the selected channel table.
    def available_channel_table_view_activated_slot(self, index):
        if index.column() == 0:
            channel = self.channel_list_widget.available_channel_table_model.itemFromIndex(index)
            self.channel_select_widget.add_channel(channel.name)

    def _done_accepted(self):
        self.done.emit(self.getSelectedChannelList())

    def _done_rejected(self):
        self.done.emit(None)


def main():
    import os
    import sys
    import signal
    import logging
    import argparse

    from ._qt import create_app
    from . import nds
    from . import const
    from . import util

    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'WARNING').upper(),
        format="%(name)s: %(message)s",
    )

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    PROG = 'ndschans'
    DESCRIPTION = 'NDS channel search GUI'

    parser = argparse.ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--nds', metavar='HOST[:PORT]',
                        help=f"NDS server [{const.NDSSERVER}]")
    parser.add_argument('glob', nargs='?', default=os.getenv('CHANNEL_GLOB', '*'),
                        help="channel glob to filter channel list (e.g. 'H1:SUS-*')")

    args = parser.parse_args()

    os.environ['NDSSERVER'] = util.resolve_ndsserver(args.nds)

    server, server_formatted = util.format_nds_server_string()

    print(f"Fetching channel list from {server} (channel glob: '{args.glob}')... ")
    channel_dict = nds.find_channels(args.glob)
    channel_list = list(sorted(channel_dict.values(), key=lambda c: c.name))
    nchannels = len(channel_list)
    print(f"Channel list received: {nchannels} channels")
    tree_model = AvailableChannelTreeModel(channel_list)
    table_model = AvailableChannelTableModel(channel_list)

    app = create_app()

    cs = ChannelListWidget(tree_model, table_model)
    cs.title.setText(f"Channel list for <span style='font-weight: bold'>{server_formatted}</span><br/>channel glob: '{args.glob}' [{nchannels} channels]")
    cs.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
