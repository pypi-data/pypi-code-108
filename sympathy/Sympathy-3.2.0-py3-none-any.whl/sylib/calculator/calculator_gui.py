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
import operator
import re
import html
import ast
import datetime
import json
import itertools

from sympathy.api import qt2 as qt
from sympathy.api import ParameterView
from sympathy.api.nodeconfig import deprecated_warn
from sympathy.platform import widget_library as sywidgets
from sympathy.utils import search
from sylib.calculator import calculator_model as models
from sylib.calculator import plugins
from sympathy.platform import colors

from sympathy.platform.widget_library import BasePreviewTable

QtGui = qt.QtGui
QtCore = qt.QtCore
QtWidgets = qt.QtWidgets

def _dtypes_str(dtypes):
    return ', '.join([str(d) for d in dtypes])


class PreviewTable(BasePreviewTable):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel)

    def scroll_to_column(self, column):
        self.scrollTo(self.model().index(0, column))


class ToolbarMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        toolbar = sywidgets.SyToolBar(self)
        toolbar.setIconSize(QtCore.QSize(18, 18))
        toolbar.add_action('Add',
                           'actions/list-add-symbolic.svg',
                           'Add column',
                           receiver=self.add_item)
        toolbar.add_action('Remove',
                           'actions/list-remove-symbolic.svg',
                           'Remove column',
                           receiver=self.remove_item)
        toolbar.add_action('Copy',
                           'actions/edit-copy-symbolic.svg',
                           'Copy column',
                           receiver=self.copy_item)

        toolbar.addStretch()
        toolbar.add_action('Move up',
                           'actions/go-up-symbolic.svg',
                           'Move row up',
                           receiver=self.move_item_up)
        toolbar.add_action('Move down',
                           'actions/go-down-symbolic.svg',
                           'Move row down',
                           receiver=self.move_item_down)
        self._toolbar = toolbar


class AttributeTableWidget(ToolbarMixin, QtWidgets.QWidget):
    data_changed = QtCore.Signal()

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self._table = QtWidgets.QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(['Name', 'Value'])
        self._table_model = self._table.model()
        # self.setStyleSheet("QTableWidget {border: 0px;}")
        layout.addWidget(self._table)
        layout.addWidget(self._toolbar)
        self.setLayout(layout)

        self._table.itemDelegate().commitData.connect(self._emit_data_changed)

    def _emit_data_changed(self, *args, **kwargs):
        self.data_changed.emit()

    def add_item(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        for col in [0, 1]:
            new_item = QtWidgets.QTableWidgetItem()
            self._table.setItem(row, col, new_item)

        self._table.setVerticalHeaderLabels(
            [str(i) for i in range(row + 1)])
        self.data_changed.emit()

    def remove_item(self):
        rows = {item.row() for item in self._table.selectedIndexes()}
        for row in sorted(rows, reverse=True):
            self._table.removeRow(row)
        self.data_changed.emit()

    def copy_item(self):
        index = self._table.currentIndex()
        row = index.row()
        if index.row() < 0:
            return
        items = [self._table.itemFromIndex(
            self._table_model.index(row, col)) for col in [0, 1]]

        self._table.insertRow(row + 1)
        self._table.setVerticalHeaderLabels(
            [str(i) for i in range(self._table.rowCount())])

        for old_item, col in zip(items, [0, 1]):
            new_item = QtWidgets.QTableWidgetItem()
            new_item.setText(old_item.text())
            self._table.setItem(row + 1, col, new_item)
        self.data_changed.emit()

    def move_item_up(self):
        self._move_item(-1)
        self.data_changed.emit()

    def move_item_down(self):
        self._move_item(1)
        self.data_changed.emit()

    def _move_item(self, direction):
        index = self._table.currentIndex()
        row = index.row()
        if direction > 0 and row == self._table_model.rowCount() - 1:
            return
        elif direction < 0 and row == 0:
            return

        old_row_data = [(col, self._table.takeItem(row + direction, col))
                        for col in [0, 1]]

        new_row_data = [(col, self._table.takeItem(row, col))
                        for col in [0, 1]]

        for col, item in new_row_data:
            self._table.setItem(row + direction, col, item)

        for col, item in old_row_data:
            self._table.setItem(row, col, item)

        selection_model = self._table.selectionModel()
        selected_indices = self._table.selectedIndexes()
        index = self._table.currentIndex()
        selection_model.setCurrentIndex(
            self._table_model.index(index.row() + direction, index.column()),
            QtCore.QItemSelectionModel.Clear |
            QtCore.QItemSelectionModel.Current)
        for index in selected_indices:
            selection_model.setCurrentIndex(
                self._table_model.index(
                    index.row() + direction, index.column()),
                QtCore.QItemSelectionModel.Select)

    @property
    def attributes(self):
        return [
            (self._table.item(row, 0).text(), self._table.item(row, 1).text())
            for row in range(self._table_model.rowCount())]

    @attributes.setter
    def attributes(self, items):
        for _ in range(self._table_model.rowCount()):
            self._table.removeRow(0)
        for row, (key, value) in enumerate(items):
            self._table.insertRow(row)
            for col, text in zip([0, 1], [key, value]):
                new_item = QtWidgets.QTableWidgetItem()
                new_item.setText(text)
                self._table.setItem(row, col, new_item)
        self._table.setVerticalHeaderLabels(
            [str(i) for i in range(self._table_model.rowCount())])



class TreeDragWidget(QtWidgets.QTreeWidget):
    """Extends QtWidgets.QTreeWidget and lets it use drag and drop."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mime_data = None
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)

    def mimeTypes(self):
        return ['function/plain']

    def mimeData(self, items):
        tree_item = items[0]
        if tree_item.childCount() == 0:
            data = tree_item.data(0, QtCore.Qt.UserRole)
            # TODO: Perhaps a good idea, but I don't like the implementation
            # if '(' not in data:
            #     data = tree_item.text(0)
            if data:
                self._mime_data = QtCore.QMimeData()
                self._mime_data.setData('function/plain', data.encode('utf8'))
                return self._mime_data


class FunctionsTreeWidget(TreeDragWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.setColumnCount(1)
        self.headerItem().setHidden(True)

    def _expr_has_trailing_whitespace(self, expr):
        res = False
        for item in ast.walk(
                compile(expr, '<string>', 'eval', ast.PyCF_ONLY_AST)):
            if isinstance(item, ast.Str):
                s = item.s
                if re.search('\\s$', s):
                    res = True
                    break
        return res

    @staticmethod
    def result_expr_from_name(name):
        return f"res[{repr(name)}]"

    def _result_leaf_data(self, name):
        expr = self.result_expr_from_name(name)
        return [expr, expr, 'Result: {}\nType: calculated result'
                .format(expr), self._expr_has_trailing_whitespace(expr)]

    def _set_leaf(self, item, text, func_name, tool_tip,
                  warn_whitespace=False,
                  column=0):
        item.setText(column, text)
        item.setData(0, QtCore.Qt.UserRole, func_name)
        if re.match(r"\${signal([0-9]+)}", func_name):
            deprecated_warn(
                "${signal0} syntax in calculator plugins", "4.0.0")
        if warn_whitespace:
            item.setBackground(column, QtGui.QBrush(colors.WARNING_BG_COLOR))
            item.setToolTip(
                column,
                '{}\n'
                'Warning, this input contains whitespace at the end.'
                .format(tool_tip))
        else:
            item.setToolTip(column, tool_tip)

    def set_model(self, model):
        """
        Initialises the function tree widget with common functions with
        tooltips.
        """
        assert self._model is None, 'Should only be set once.'
        self._model = model

        signals_and_types = self._model.input_columns_and_types or []
        results = [item.name for item in model.items()]

        def build_leaf(text, func_name, tool_tip,
                       warn_whitespace=False,
                       column=0):
            """
            Creates a new QtWidgets.QTreeWidgetItem, without inserting it in
            a parent element.

            Parameters:
            -----------
            column : int
                The column the text should be placed in.
            text : string
                The node text
            func_name : string
                The method syntax
            tool_tip : string
                The text at the tooltip

            Returns
            --------
            QtWidgets.QTreeWidgetItem
                The new QtWidgets.QTreeWidgetItem node.
            """
            item = QtWidgets.QTreeWidgetItem()
            self._set_leaf(item, text, func_name, tool_tip,
                           warn_whitespace=warn_whitespace, column=column)
            return item

        def build_and_insert_subroot(root, name, content):
            subroot = QtWidgets.QTreeWidgetItem(root)
            subroot.setText(0, name)
            build_tree(subroot, content)
            return subroot

        def build_tree(root, content):
            if isinstance(content, list):
                for item in content:
                    child = build_leaf(*item)
                    root.addChild(child)
            elif isinstance(content, dict):
                for tree_text, subcontent in content.items():
                    child = build_and_insert_subroot(root, tree_text, subcontent)
            else:
                raise TypeError("Plugin gui dict contained unsupported object "
                                "type: {}".format(type(gui_dict)))

        def purge_hidden_items(gui_dict, hidden_items):
            """
            Create a new gui_dict without the items in hidden_items.

            hidden_items should be a list of tuples with the "paths" in the
            gui_dict that should be hidden.
            """
            if not hidden_items:
                return gui_dict

            # The items that should be hidden on this level in the tree
            current_hidden = [item[0] for item in hidden_items if len(item) == 1]

            if isinstance(gui_dict, list):
                # Hide some items
                new_gui_dict = [item for item in gui_dict
                                if item[0] not in current_hidden]
            elif isinstance(gui_dict, dict):
                new_gui_dict = {}
                for subtree_label, subtree in gui_dict.items():
                    if subtree_label in current_hidden:
                        # Hide this subtree
                        continue

                    new_hidden = [item[1:] for item in hidden_items
                                  if item[0] == subtree_label]
                    new_gui_dict[subtree_label] = purge_hidden_items(
                        subtree, new_hidden)
            else:
                raise TypeError("Plugin gui dict contained unsupported object "
                                "type: {}".format(type(gui_dict)))
            return new_gui_dict

        available_signals = [
            [name, name, 'Signal: {}\nType: {}'.format(
                name, _dtypes_str(dtypes)),
             self._expr_has_trailing_whitespace(name)]
            for name, dtypes in signals_and_types]
        build_and_insert_subroot(self, 'Signals', available_signals)

        calculated_results = [
            self._result_leaf_data(name) for name in results]

        self._results = build_and_insert_subroot(
            self, 'Results', calculated_results)
        available_plugins = sorted(plugins.available_plugins('python'),
                                   key=operator.attrgetter("WEIGHT"))

        hidden_items = []
        for plugin in available_plugins:
            hidden_items.extend(plugin.hidden_items())
        for plugin in available_plugins:
            gui_dict = purge_hidden_items(plugin.gui_dict(), hidden_items)
            build_tree(self, gui_dict)

        model.rowsInserted.connect(self._handle_result_rows_inserted)
        model.rowsMoved.connect(self._handle_result_rows_moved)
        model.rowsRemoved.connect(self._handle_result_rows_removed)
        model.dataChanged.connect(self._handle_result_data_changed)

    def _handle_result_rows_inserted(self, parent_index, first, last):
        for row in range(first, last + 1):
            leaf = QtWidgets.QTreeWidgetItem()
            self._results.insertChild(row, leaf)
            item = self._model.item(row)
            self._set_leaf(leaf, *self._result_leaf_data(item.name))

    def _handle_result_rows_moved(self, *args, **kwargs):
        raise NotImplementedError('Not needed')

    def _handle_result_rows_removed(self, parent_index, first, last):
        for row in reversed(range(first, last + 1)):
            self._results.takeChild(row)

    def _handle_result_data_changed(self, top_left, bottom_right, roles=None):
        if top_left.isValid() and bottom_right.isValid():
            first = top_left.row()
            last = bottom_right.row()

            for row, item in enumerate(self._model.items()):
                if first <= row and row <= last:
                    leaf = self._results.child(row)
                    self._set_leaf(leaf, *self._result_leaf_data(item.name))



class CalcFieldWidget(QtWidgets.QPlainTextEdit):
    insert_function = QtCore.Signal(str)
    editingFinished = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        f = sywidgets.monospace_font()
        self.setFont(f)

        self.setTabChangesFocus(True)
        self.setUndoRedoEnabled(False)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)

    def canInsertFromMimeData(self, source):
        if source.hasFormat('function/plain'):
            return True
        else:
            res = super().canInsertFromMimeData(source)
            return res

    def insertFromMimeData(self, source):
        if source.hasFormat('function/plain'):
            data = source.data('function/plain').data()
            text = data.decode('utf8')
            self.insert_function.emit(text)
        else:
            super().insertFromMimeData(source)
        self.editingFinished.emit()


class TableDragMixin(object):
    def __init__(self, *args, **kwargs):
        """
        Generic mixin class for enabling dragging in a QTableView
        subclass.

        Parameters
        ----------
        drag_cols : iterable of int
            Column indices where drag should be enabled.

        drag_mode : Qt.QtCore.Qt.DropAction
            Drag mode to use.
        """
        drag_cols = kwargs.pop('drag_cols', [])
        drag_mode = kwargs.pop('drag_mode', None)

        if drag_mode is None:
            drag_mode = QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

        self._drag_index = None
        self._dragging = False
        self._drag_mode = drag_mode
        self._drag_cols = set(drag_cols)
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            index = self.indexAt(event.pos())
            drag_index = None
            if index.isValid() and index.column() in self._drag_cols:
                drag_index = index
            self._drag_index = drag_index
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_index = None
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not self._dragging and self._drag_index:
            self._dragging = True
            try:
                # Create new drag and render items on row to use as image
                # (pixmap) while dragging.
                drag = QtGui.QDrag(self)
                row = self._drag_index.row()
                visual_rect = self.visualRect(self._drag_index)
                for i in range(self.model().rowCount()):
                    row_index = self._drag_index.sibling(row, i)
                    if row_index.isValid():
                        visual_rect = visual_rect.united(
                            self.visualRect(row_index))

                pixmap = QtGui.QPixmap(visual_rect.size())
                self.render(pixmap, QtCore.QPoint(0, 0),
                            visual_rect.translated(
                                self.verticalHeader().width(),
                                self.horizontalHeader().height()))
                mime_data = self._row_mime_data(row)
                drag.setMimeData(mime_data)
                drag.setPixmap(pixmap)
                drag.exec_(self._drag_mode)
                event.accept()
            finally:
                self._dragging = False
        else:
            return super().mouseMoveEvent(event)

    def _row_mime_data(self, row):
        """
        Mime data for dragged row.

        Parameters
        ----------
        row : int
            Row index.

        Returns
        -------
        QtCore.QMimeData
            Mime data for row.
        """
        raise NotImplementedError(
            'Inheriting class needs to implement _row_mime_data.')


class TextLineItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    Delegate with the purpose of being able to show text with multiple lines
    in a table cell with a single line. Line breaking white-space are replaced
    with middle dot to ensure only single line is used.

    Remaining white-space are replaced by space, only a single space in case
    there are several in a row, to save space.

    Examples:

    1.

    >>> [x
    >>> for x in
    >>> [1,2,3]]

    will show up as

    >>> [x.for x in.[1,2,3]]

    2.

    >>> "    hello    world     "

    will show up as
    >>> " hello world "
    """
    _white_line_re = re.compile('[\\r\\n\\f]+')
    _white_multi_re = re.compile('\\s+')

    # Replacement characters used by Qt when
    # QTextOption.ShowTabsAndSpaces is active.
    _middle_dot = '\u00b7'
    _right_arrow = '\u2192'

    def __init__(self, column, parent, *args):
        super().__init__(parent, *args)
        self._column = column

    def displayText(self, value, locale):
        value = self._white_line_re.sub(self._middle_dot, value)
        value = self._white_multi_re.sub(' ', value)
        return super().displayText(value, locale)


class CalculationsTableView(TableDragMixin, QtWidgets.QTableView):
    current_row_changed = QtCore.Signal()

    # Adjust minimum height hint to fit this amount of rows.
    _min_rows_shown = 3

    def __init__(self, parent=None):
        super().__init__(drag_cols=[3], parent=parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
        item_delegate = TextLineItemDelegate(column=1, parent=self)
        self.setItemDelegate(item_delegate)
        self.setWordWrap(False)

    def setModel(self, model):
        super().setModel(model)
        selection_model = self.selectionModel()
        selection_model.currentRowChanged.connect(self.current_row_changed)

    def item_added(self, index):
        if index.isValid():
            self.setCurrentIndex(index)

    def current_item(self):
        index = self.currentIndex()
        if not index.isValid():
            return None
        if index.column() == 0:
            item = self.model().itemFromIndex(index)
        else:
            item = self.model().item(index.row(), 0)
        return item

    def _row_mime_data(self, row):
        mime_data = QtCore.QMimeData()
        data = FunctionsTreeWidget.result_expr_from_name(
            self.model().itemFromIndex(
                self._drag_index.sibling(row, 0)).name)
        mime_data.setData('text/plain', data.encode('utf8'))
        return mime_data

    def minimumSizeHint(self):
        minimum_size_hint = super().minimumSizeHint()

        model = self.model()
        if model:
            h = 0
            rc = model.rowCount()

            if rc:
                h = (
                    self.horizontalHeader().height() +
                    sum([self.rowHeight(i % rc)
                         for i in range(
                                 self._min_rows_shown)]))

            w = (self.verticalHeader().width() + 12 +
                 sum([self.columnWidth(i)
                      for i in range(model.columnCount())]))

            return QtCore.QSize(
                max(w,
                    minimum_size_hint.width()),
                max([h,
                     minimum_size_hint.height()]))

        return minimum_size_hint


class CalculationsWidget(ToolbarMixin, QtWidgets.QWidget):
    new_undo_state = QtCore.Signal()

    def __init__(self, model, undo_action, redo_action, parent=None):
        super().__init__(parent=parent)

        assert(isinstance(model, models.CalculatorItemModel))
        self._model = model
        self.view = CalculationsTableView(parent=self)
        self.view.setModel(self._model)

        # Insert undo/redo actions first in toolbar:
        first_action = self._toolbar.actions()[0]
        self._toolbar.insertAction(first_action, undo_action)
        self._toolbar.insertAction(first_action, redo_action)
        self._toolbar.insertSeparator(first_action)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._toolbar)
        layout.addWidget(self.view)
        self.setLayout(layout)

        # Workaround to get correct header looks when loading parameters
        # and when creating a new calculator node.
        self.add_item()
        self.remove_item()

        self.view.setColumnWidth(2, 30)
        self.view.setColumnWidth(3, 15)
        self.view.horizontalHeader().moveSection(2, 0)
        self.view.horizontalHeader().moveSection(3, 0)
        self.view.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.Fixed)

    def add_item(self):
        item = self._model.add_item()
        self.view.setCurrentIndex(item.index())
        self.new_undo_state.emit()

    def remove_item(self):
        current_selected_index = self.view.currentIndex()
        self._model.remove_item(current_selected_index.row())
        self.new_undo_state.emit()

    def copy_item(self):
        current_index = self.view.currentIndex()
        row_count = self._model.rowCount()
        self._model.copy_item(current_index.row())

        if self._model.rowCount() > row_count:
            # Item was successfully copied.
            self.view.setCurrentIndex(
                self._model.index(
                    current_index.row() + 1, current_index.column()))
        self.new_undo_state.emit()

    def move_item_up(self):
        self._move_item(-1)
        self.new_undo_state.emit()

    def move_item_down(self):
        self._move_item(1)
        self.new_undo_state.emit()

    def _move_item(self, direction):
        index = self.view.currentIndex()
        row = index.row()
        if direction > 0 and row == self._model.rowCount() - 1:
            return
        elif direction < 0 and row == 0:
            return
        items_row = self._model.takeRow(row)
        self._model.insertRow(row + direction, items_row)
        selection_model = self.view.selectionModel()
        selection_model.setCurrentIndex(
            items_row[0].index(),
            QtCore.QItemSelectionModel.ClearAndSelect |
            QtCore.QItemSelectionModel.Rows)
        items_row[0].emitDataChanged()


class ItemEditBox(QtWidgets.QGroupBox):
    data_changed = QtCore.Signal()
    undo_triggered = QtCore.Signal()
    redo_triggered = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._item = None
        self.highlighter = None
        self.column_name = QtWidgets.QLineEdit('')
        self.column_name.setPlaceholderText('Column name')
        self._setup_name_colouring()

        self._tabs = QtWidgets.QTabWidget(parent=self)
        self.calc_field = CalcFieldWidget()
        self.attr_table = AttributeTableWidget()
        self._tabs.addTab(self.calc_field, 'Calculation')
        self._tabs.addTab(self.attr_table, 'Attributes')

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.column_name)
        layout.addWidget(self._tabs)
        self.setLayout(layout)

        self.setTabOrder(self.column_name, self.calc_field)

        self.column_name.installEventFilter(self)
        self.calc_field.installEventFilter(self)

        self.column_name.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.calc_field.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.column_name.customContextMenuRequested.connect(
            self._column_name_context_menu)
        self.calc_field.customContextMenuRequested.connect(
            self._calc_field_context_menu)

        self.highlighter = sywidgets.PygmentsHighlighter(
            self.calc_field, 'python')
        self.calc_field.textChanged.connect(self.highlighter.rehighlight)
        self.attr_table.data_changed.connect(self._attrs_changed)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.matches(QtGui.QKeySequence.Undo):
                self.undo_triggered.emit()
                return True
            elif event.matches(QtGui.QKeySequence.Redo):
                self.redo_triggered.emit()
                return True
        return False

    def _column_name_context_menu(self, pos):
        self._context_menu(self.column_name, pos)

    def _calc_field_context_menu(self, pos):
        self._context_menu(self.calc_field, pos)

    def _context_menu(self, widget, pos):
        menu = widget.createStandardContextMenu()

        for action in menu.actions():
            if 'Undo' in action.text() or 'Redo' in action.text():
                menu.removeAction(action)

        menu.exec_(widget.mapToGlobal(pos))

    def focus_attributes(self):
        self._tabs.setCurrentIndex(1)

    def focus_calculation(self, cursor_pos=None):
        self._tabs.setCurrentIndex(0)
        if cursor_pos is not None:
            cursor = self.calc_field.textCursor()
            cursor.setPosition(cursor_pos)
            self.calc_field.setTextCursor(cursor)

    def cursor_pos(self):
        """
        Return cursor position in calculation or None if attributes are
        focused.
        """
        if self._tabs.currentIndex() == 1:
            return None
        else:
            return self.calc_field.textCursor().position()

    def _setup_name_colouring(self):
        normal_palette = QtGui.QPalette()
        normal_palette.setColor(QtGui.QPalette.Base, colors.DEFAULT_BG_COLOR)
        normal_palette.setColor(QtGui.QPalette.Text, colors.DEFAULT_TEXT_COLOR)

        warning_palette = QtGui.QPalette()
        warning_palette.setColor(QtGui.QPalette.Base, colors.WARNING_BG_COLOR)
        warning_palette.setColor(
            QtGui.QPalette.Text, colors.WARNING_TEXT_COLOR)

        error_palette = QtGui.QPalette()
        error_palette.setColor(QtGui.QPalette.Base, colors.DANGER_BG_COLOR)
        error_palette.setColor(
            QtGui.QPalette.Text, colors.DANGER_TEXT_COLOR)

        def update_column_name_color(new_name, editor=self.column_name):
            if '=' in new_name:
                self.column_name.setPalette(error_palette)
                self.column_name.setToolTip(
                    'Column name must not contain equal sign')
            elif re.search("\\s$", new_name):
                self.column_name.setPalette(warning_palette)
                self.column_name.setToolTip(
                    'Warning, this column name contains whitespace at the end')
            else:
                self.column_name.setPalette(normal_palette)
                self.column_name.setToolTip('')
        self.column_name.setPalette(normal_palette)
        self.column_name.textChanged.connect(update_column_name_color)

    def set_item(self, item):

        if self._item is not None:
            self.save_parameters()
            self.column_name.textChanged.disconnect(self.column_name_changed)
            self.calc_field.textChanged.disconnect(self.calc_line_changed)
        self._item = item

        if item is not None:
            self.attr_table.attributes = item.attributes[:]
            self.column_name.setText(self._item.name)
            self.calc_field.setPlainText(self._item.expr)
            self.column_name.textChanged.connect(self.column_name_changed)
            self.calc_field.textChanged.connect(self.calc_line_changed)
        else:
            self.attr_table.attributes = []
            self.column_name.setText('')
            self.calc_field.setPlainText('')

    def column_name_changed(self):
        changed = self._item.name != self.column_name.text()
        if self._item is not None and changed:
            self._item.name = self.column_name.text()
            self.data_changed.emit()

    def calc_line_changed(self):
        changed = self._item.expr != self.calc_field.toPlainText()
        if self._item is not None and changed:
            self._item.expr = self.calc_field.toPlainText()
            self.data_changed.emit()

    def _attrs_changed(self):
        self.save_parameters()
        self.data_changed.emit()

    def save_parameters(self):
        if self._item is not None:
            self._item.attributes[:] = self.attr_table.attributes


class CalculatorWidget(ParameterView):
    def __init__(self, in_data, parameters,
                 preview_calculator=None, parent=None,
                 multiple_input=False, empty_input=False,
                 show_copy_input=False):
        super().__init__(parent=parent)
        self._status_message = ''
        self._multiple_input = multiple_input
        if multiple_input:
            self._in_tables = in_data
        else:
            self._in_tables = []
            self._in_tables.append(in_data)
        self._parameter_root = parameters

        calc_list = self._parameter_root['calc_list'].list
        calc_attrs_dict = json.loads(
            self._parameter_root['calc_attrs_dict'].value)
        model_data = (calc_list, calc_attrs_dict)

        self._undo_stack = sywidgets.UndoStack()
        self.model = models.CalculatorItemModel(
            self._in_tables, model_data,
            preview_calculator=preview_calculator,
            empty_input=empty_input)
        self.preview_model = (
            PreviewModel(self.model) if preview_calculator else None)
        self.calcs_view = CalculationsWidget(
            self.model,
            self._undo_stack.undo_action,
            self._undo_stack.redo_action)
        self.calcs_table_view = self.calcs_view.view
        self.preview_view = PreviewTable()

        self.addAction(self._undo_stack.undo_action)
        self.addAction(self._undo_stack.redo_action)

        # edit signal widgets
        self.current_calc = ItemEditBox('Edit Signal')
        self.function_tree = FunctionsTreeWidget()
        self.search_field = sywidgets.ClearButtonLineEdit(
            placeholder='Search for signal or function')
        self.tree_head = None

        self.preview_view.setSelectionMode(
            QtWidgets.QAbstractItemView.NoSelection)
        self.preview_view.setModel(self.preview_model)
        hsplitter = QtWidgets.QSplitter()
        hsplitter.setOpaqueResize(QtCore.Qt.Horizontal)
        hsplitter.setContentsMargins(0, 0, 0, 0)
        hsplitter.addWidget(self.calcs_view)
        preview_view = PreviewTable()
        preview_view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        preview_view.setModel(self.preview_model)

        # function widget
        function_label = QtWidgets.QLabel("Signals and Common functions")
        self.function_tree.setMaximumWidth(2000)
        function_tree_layout = QtWidgets.QVBoxLayout()
        function_tree_layout.setContentsMargins(0, 0, 0, 0)
        function_tree_layout.setSpacing(5)
        function_tree_layout.addWidget(function_label)
        function_tree_layout.addWidget(self.function_tree)
        function_tree_layout.addWidget(self.search_field)
        functions_widget = QtWidgets.QWidget()
        functions_widget.setLayout(function_tree_layout)
        hsplitter.addWidget(functions_widget)

        # add widgets to global vsplitter
        vsplitter = QtWidgets.QSplitter()
        vsplitter.setOrientation(QtCore.Qt.Vertical)
        vsplitter.setContentsMargins(0, 0, 0, 0)
        vsplitter.addWidget(hsplitter)
        vsplitter.addWidget(self.current_calc)
        vsplitter.addWidget(self.preview_view)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(vsplitter)
        self._copy_input_gui = self._parameter_root['copy_input'].gui()
        if self._multiple_input:
            hlayout = QtWidgets.QHBoxLayout()
            hlayout.setContentsMargins(0, 0, 0, 0)
            if show_copy_input:
                hlayout.addWidget(self._copy_input_gui)
            layout.addLayout(hlayout)

        else:
            if show_copy_input:
                layout.addWidget(self._copy_input_gui)
        self._fail_strategy_gui = self._parameter_root['fail_strategy'].gui()
        layout.addWidget(self._fail_strategy_gui)
        self.setLayout(layout)

        self.calcs_table_view.current_row_changed.connect(self.update_current_item)
        self.function_tree.itemDoubleClicked.connect(self.insert_function)
        self.search_field.textChanged.connect(self.search_function)
        self.current_calc.calc_field.insert_function.connect(
            self.insert_text)
        self.model.data_ready.connect(self.status_changed)
        self.model.item_dropped.connect(self.calcs_table_view.item_added)

        if not self.model.rowCount():
            self.model.add_item()

        if self.calcs_table_view.model().rowCount():
            selection_model = self.calcs_table_view.selectionModel()
            first_idx = self.calcs_table_view.model().index(0, 0)
            selection_model.select(first_idx,
                                   QtCore.QItemSelectionModel.ClearAndSelect |
                                   QtCore.QItemSelectionModel.Rows)

        for idx, (cname, dtypes) in enumerate(
                self.model.input_columns_and_types):
            name_item = QtWidgets.QTableWidgetItem(models.display_calculation(
                cname))
            type_item = QtWidgets.QTableWidgetItem(_dtypes_str(dtypes))

            if re.search("\\s'(\\).data|\\])$", cname):
                name_item.setBackground(QtGui.QBrush(colors.WARNING_BG_COLOR))
                name_item.setToolTip(
                    'Warning, this column name contains whitespace at the end')
            for item in [name_item, type_item]:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)

        self.calcs_table_view.setCurrentIndex(self.model.index(0, 0))
        self.update_current_item()

        self.function_tree.set_model(self.model)
        self.tree_head = self.function_tree.invisibleRootItem()

        self._add_undo_state()
        self.calcs_view.new_undo_state.connect(self._add_undo_state)
        self.model.enabled_changed.connect(self._add_undo_state)
        self.current_calc.data_changed.connect(self._add_undo_state)
        self._parameter_root['copy_input'].value_changed.add_handler(
            self._add_undo_state)
        self._parameter_root['fail_strategy'].value_changed.add_handler(
            self._add_undo_state)
        self._undo_stack.state_changed.connect(self._undo_state_changed)
        self.current_calc.undo_triggered.connect(
            self._undo_stack.undo_action.trigger)
        self.current_calc.redo_triggered.connect(
            self._undo_stack.redo_action.trigger)

    def _diff_states(self, new_model_data):
        """
        Compare new_model_data with the current model data returning the
        index of the changed calculation (if any), a boolean specifying if the
        attributes (True) or the calculation (False) changed, and am integer
        for the first character of the calculation that changed.
        """
        old_calc_list, old_attrs_dict = self.model.get_data()
        new_calc_list, new_attrs_dict = new_model_data

        if new_calc_list != old_calc_list:
            for i, (new_calc, old_calc) in enumerate(itertools.zip_longest(
                    new_calc_list, old_calc_list)):
                if new_calc != old_calc:
                    if new_calc is None or old_calc is None:
                        return (i, False, None)

                    _, new_calc, _ = models.parse_calc(new_calc)
                    _, old_calc, _ = models.parse_calc(old_calc)
                    for char_i, (new_char, old_char) in enumerate(
                            itertools.zip_longest(new_calc, old_calc)):
                        if new_char != old_char:
                            return (i, False, char_i)
                    return (i, False, None)
            assert False, "lists differ, but lists don't differ!"

        elif new_attrs_dict != old_attrs_dict:
            for new_attrs, old_attrs in itertools.zip_longest(
                    new_attrs_dict, old_attrs_dict):
                if new_attrs != old_attrs:
                    if new_attrs is None:
                        return (old_attrs[0], True, None)
                    else:
                        return (new_attrs[0], True, None)
            assert False, "attributes differ, but attributes don't differ!"

        return (None, False, None)

    def _gui_state(self):
        """
        Return the current state of the gui in same format as _diff_states.
        """
        index = self.calcs_table_view.currentIndex()
        if not index.isValid():
            return (None, False, None)

        calc = index.row()
        cursor_pos = self.current_calc.cursor_pos()

        if cursor_pos is None:
            return (calc, True, None)
        else:
            return (calc, False, cursor_pos)

    def _add_undo_state(self, *args, **kwargs):
        model_data = self.model.get_data()
        fail_strategy = self._parameter_root['fail_strategy'].selected
        copy_input = self._parameter_root['copy_input'].value
        new_state = json.dumps(
            (model_data, copy_input, fail_strategy))
        res = self._undo_stack.add_undo_state(new_state)

    def _undo_state_changed(self, new_state):
        new_state = json.loads(new_state)
        model_data, copy_input, fail_strategy = new_state

        diff_calc, diff_attr, pos = self._diff_states(model_data)
        if diff_calc is None:
            diff_calc, diff_attr, pos = self._gui_state()

        copy_input_event = self._parameter_root['copy_input'].value_changed
        fail_strategy_event = self._parameter_root['fail_strategy'].value_changed
        with copy_input_event.block_handler(self._add_undo_state):
            self._copy_input_gui.set_value(copy_input)
        with fail_strategy_event.block_handler(self._add_undo_state):
            self._fail_strategy_gui.set_value(fail_strategy)
        self.model.set_data(model_data)

        # Focus the gui on what was undone:
        if diff_calc is not None:
            self.calcs_table_view.setCurrentIndex(self.model.index(diff_calc, 0))
        if diff_attr:
            self.current_calc.focus_attributes()
        else:
            self.current_calc.focus_calculation(pos)

    def save_parameters(self):
        self.current_calc.save_parameters()
        calc_list, calc_attrs_dict = self.model.get_data()
        self._parameter_root['calc_list'].list = calc_list
        self._parameter_root['calc_list'].value_names = []
        self._parameter_root['calc_attrs_dict'].value = json.dumps(
            calc_attrs_dict)

    def has_status(self):
        return True

    def cleanup(self):
        self.model.cleanup_preview_worker()

    @property
    def valid(self):
        status, self._status_message = self.model.validate()
        return status

    @property
    def status(self):
        if self._status_message:
            return '<p>{}</p>'.format(
                html.escape(str(self._status_message)))
        return ''

    def insert_function(self, item):
        text = item.data(0, QtCore.Qt.UserRole)
        self.insert_text(text)

    def insert_text(self, text):
        if text:
            text = models.display_calculation(text)

            # For signals 0-25 replace with letters from a-z.
            ordz = ord('z')
            for n in list(re.findall('\\${signal([0-9]+)}', text)):
                n = int(n)
                ll = n + ord('a')
                if ll <= ordz:
                    text = text.replace('${signal%s}' % n, chr(ll))
            self.current_calc.calc_field.insertPlainText(text)

    def update_current_item(self):
        item = self.calcs_table_view.current_item()
        self.current_calc.set_item(item)
        if item is not None:
            self.preview_view.scroll_to_column(item.row())

    def search_function(self):
        def recursive_hide(node, pattern, word):
            # Using fuzzy pattern against the text and exact pattern against
            # tooltip. Fuzzy matching against long docstring can produce
            # surprising matches especially since there is no direct feedback.
            status = 0
            if node.childCount() < 1:
                # This is a leave
                text = node.text(0)
                data = node.data(0, QtCore.Qt.UserRole)
                if not (search.matches(pattern, text) or data and
                        word in data):
                    status = 1
            else:
                count = 0
                for index in range(0, node.childCount()):
                    count += recursive_hide(node.child(index), pattern, word)
                if count == node.childCount():
                    # All children are hidden
                    status = 1

            node.setHidden(status)
            node.setExpanded(~status)
            if not pattern:
                node.setExpanded(status)

            return status

        term = self.search_field.text()
        pattern = search.fuzzy_free_pattern(term)
        recursive_hide(self.tree_head, pattern, term)


class PreviewModel(QtCore.QAbstractTableModel):
    def __init__(self, source_model, parent=None):
        super().__init__(parent=parent)

        assert(isinstance(source_model, models.CalculatorItemModel))
        self.source_model = source_model

        self.source_model.dataChanged.connect(self.update_model)
        self.source_model.data_ready.connect(self.modelReset)

    def update_model(self, topleft_index, bottomright_index):
        if topleft_index.parent() == bottomright_index.parent():
            self.modelReset.emit()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            item = self.source_model.item(section)
            if role == QtCore.Qt.DisplayRole:
                return item.name
            elif role == QtCore.Qt.ToolTipRole:
                return item.name
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
            elif role == QtCore.Qt.BackgroundRole:
                if item.valid:
                    return None
                else:
                    return colors.DANGER_BG_COLOR  # redish color
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(section)

        return super().headerData(section, orientation, role)

    def rowCount(self, qmodel_index=None):
        source_items = self.source_model.items()
        columns_len = [len(item._column_data) for item in source_items]
        if columns_len:
            row_count = max(columns_len)
        else:
            row_count = 0
        return row_count

    def columnCount(self, qmodel_index=None):
        return self.source_model.rowCount()

    def data(self, qmodel_index, role=QtCore.Qt.DisplayRole):

        def cell_format(data):
            # TODO: Share with other previews in library.
            try:
                data = data.tolist()
            except AttributeError:
                pass

            if isinstance(data, datetime.datetime):
                data = data.isoformat()
            elif isinstance(data, bytes):
                # repr will show printable ascii characters as usual
                # but will replace any non-ascii or non-printable
                # characters with an escape sequence. The slice
                # removes the quotes added by repr.
                data = repr(data)[2:-1]
            else:
                data = str(data)
            return data

        if not qmodel_index.isValid():
            return None
        row = qmodel_index.row()
        col = qmodel_index.column()
        column_item = self.source_model.item(col)
        data = column_item._column_data
        try:
            display_data = data[row]
        except IndexError:
            display_data = ''
        if role == QtCore.Qt.DisplayRole:
            return cell_format(display_data)
        elif role == QtCore.Qt.ToolTipRole:
            if display_data is not None:
                return cell_format(display_data)
            else:
                return ''
        elif role == QtCore.Qt.BackgroundRole:
            if not column_item.valid or column_item.duplicate:
                return colors.DANGER_BG_COLOR
            elif column_item.is_computing:
                return colors.WARNING_BG_COLOR
            else:
                return None
        return None

    def flags(self, qmodel_index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
