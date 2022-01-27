# This file is part of Sympathy for Data.
# Copyright (c) 2021 Combine Control Systems AB
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
"""
Standard actions and menus for widgets.
"""
import Qt.QtWidgets as QtWidgets
import Qt.QtGui as QtGui
import Qt.QtCore as QtCore
from sympathy.platform import widget_library as sywidgets
from . themes import get_active_theme as _theme
from . keymaps import get_active_keymap as _keymap


class Actions:
    """
    Standard actions for a convenient way to create actions with a shared
    definition.
    """
    def _create_action(self, text, shortcut, icon=None, parent=None):
        action = QtWidgets.QAction(text, parent=parent)
        if icon is not None:
            action.setIcon(QtGui.QIcon(icon))
        action.setShortcut(shortcut)
        return action

    def _theme(self):
        return _theme()

    def _keymap(self):
        return _keymap()

    def undo(self, parent=None):
        return self._create_action(
            '&Undo', self._keymap().undo, icon=self._theme().undo,
            parent=parent)

    def redo(self, parent=None):
        return self._create_action(
            '&Redo', self._keymap().redo, icon=self._theme().redo,
            parent=parent)

    def copy(self, parent=None):
        return self._create_action(
            '&Copy', self._keymap().copy, icon=self._theme().copy,
            parent=parent)

    def cut(self, parent=None):
        return self._create_action(
            'Cu&t', self._keymap().cut, icon=self._theme().cut,
            parent=parent)

    def paste(self, parent=None):
        return self._create_action(
            '&Paste', self._keymap().paste, icon=self._theme().paste,
            parent=parent)

    def delete(self, parent=None):
        return self._create_action(
            'Delete', self._keymap().delete, icon=self._theme().delete,
            parent=parent)

    def select_all(self, parent=None):
        return self._create_action(
            'Select All', self._keymap().select_all,
            icon=self._theme().selection, parent=parent)

    def new_item(self, parent=None):
        return self._create_action(
            'Add Item', self._keymap().new_item,
            icon=self._theme().new_item, parent=parent)

    def delete_item(self, parent=None):
        return self._create_action(
            'Delete Item', self._keymap().delete_item,
            icon=self._theme().delete_item, parent=parent)


actions = Actions()


# Utils.

def _to_clipboard(text):
    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.setText(text)


def _from_clipboard():
    return QtWidgets.QApplication.clipboard().text()


def _intervals(values):
    """
    Return list of intervals of values. Values are sorted.
    [[start0, end0], [start1, end1], ...]
    Contiguous values end up in the same interval.
    """
    ranges = []

    if values:
        ivalues = iter(sorted(values))
        value = next(ivalues)
        range = [value, value]
        ranges = [range]
        for value in values:
            if value <= range[1] + 1:
                range[1] = value
            else:
                range = [value, value]
                ranges.append(range)
    return ranges


# Standard actions for various contexts and controllers that make them
# easy to add to different widgets, views.


class Controller:
    """
    Base class.
    """
    def setup(self):
        """
        Update actions state.
        """
        pass


class View:
    """
    View that uses controller to handle actions.

    Base class.
    Concrete subclasses should be instances of QWidget.
    """
    def __init__(self, *args, **kwargs):
        self._controller = None
        super().__init__(*args, **kwargs)

    def set_controller(self, controller: Controller):
        self._controller = controller
        self.setup()

    def setup(self):
        """
        Call to let the controller update actions.
        """
        if self._controller:
            self._controller.setup()


class MenuView(View, QtWidgets.QMenu):
    pass


class TextEditActions:
    def __init__(self, parent=None):
        super().__init__()
        self.undo = actions.undo(parent=parent)
        self.redo = actions.redo(parent=parent)
        self.copy = actions.copy(parent=parent)
        self.cut = actions.cut(parent=parent)
        self.paste = actions.paste(parent=parent)
        self.delete = actions.delete(parent=parent)
        self.select_all = actions.select_all(parent=parent)


class TextEditController(Controller):
    """
    Controls the actions of a TextEditMenu.
    Determines which to be shown, enabled and their action when triggered.

    Base class.
    """
    def __init__(self, actions: TextEditActions):
        super().__init__()
        self.actions = actions
        self.actions.undo.triggered.connect(self.undo)
        self.actions.redo.triggered.connect(self.redo)
        self.actions.copy.triggered.connect(self.copy)
        self.actions.cut.triggered.connect(self.cut)
        self.actions.paste.triggered.connect(self.paste)
        self.actions.delete.triggered.connect(self.delete)
        self.actions.select_all.triggered.connect(self.select_all)

    def setup(self):
        self.setup_undo(self.actions.undo)
        self.setup_redo(self.actions.redo)
        self.setup_copy(self.actions.copy)
        self.setup_cut(self.actions.cut)
        self.setup_paste(self.actions.paste)
        self.setup_delete(self.actions.delete)
        self.setup_select_all(self.actions.select_all)

    # Setup actions.
    def setup_undo(self, action):
        pass

    def setup_redo(self, action):
        pass

    def setup_copy(self, action):
        pass

    def setup_cut(self, action):
        pass

    def setup_delete(self, action):
        pass

    def setup_paste(self, action):
        pass

    def setup_select_all(self, action):
        pass

    # Behaviors when triggered.
    def undo(self):
        pass

    def redo(self):
        pass

    def copy(self):
        pass

    def paste(self):
        pass

    def cut(self):
        pass

    def delete(self):
        pass

    def select_all(self):
        pass


class TextEditMenu(MenuView):
    """
    TextEditMenu, has actions similar to a default context menu for QTextEdit,
    QLineEdit, etc.
    """

    def __init__(self, actions: TextEditActions, parent=None):
        super().__init__(parent=parent)
        self.actions = actions

        self.addAction(self.actions.undo)
        self.addAction(self.actions.redo)
        self.addSeparator()
        self.addAction(self.actions.copy)
        self.addAction(self.actions.cut)
        self.addAction(self.actions.paste)
        self.addAction(self.actions.delete)
        self.addSeparator()
        self.addAction(self.actions.select_all)


class DocumentTextEditController(TextEditController):
    """
    Controller for TextEditMenu using QTextDocument based view.
    Suitable for QGraphicsTextItem or QTextEdit.
    """
    def __init__(self, actions: TextEditActions, view):
        super().__init__(actions)
        self._view = view
        self._get_cursor = view.textCursor
        self._set_cursor = view.setTextCursor
        self._cursor = self._get_cursor()
        self._document = view.document()

    def _undo_redo_visible(self):
        return self._document.isUndoRedoEnabled()

    def setup_undo(self, action):
        action.setVisible(self._undo_redo_visible())
        action.setEnabled(self._document.isUndoAvailable())

    def setup_redo(self, action):
        action.setVisible(self._undo_redo_visible())
        action.setEnabled(self._document.isRedoAvailable())

    def _text_selected(self):
        return self._get_cursor().hasSelection()

    def setup_copy(self, action):
        action.setEnabled(self._text_selected())

    def setup_cut(self, action):
        action.setEnabled(self._text_selected())

    def setup_delete(self, action):
        action.setEnabled(self._text_selected())

    def _all_selected(self):
        count = self._document.characterCount()
        res = True
        if count > 0:
            cursor = self._get_cursor()
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            res = (start == 0 and end == self._document.characterCount() - 1)
        return res

    def setup_select_all(self, action):
        empty = self._document.isEmpty()
        enabled = not empty
        if enabled:
            enabled = not self._all_selected()
        action.setEnabled(enabled)

    def undo(self):
        self._document.undo()

    def redo(self):
        self._document.redo()

    def copy(self):
        _to_clipboard(self._get_cursor().selectedText())

    def paste(self):
        cursor = self._get_cursor()
        cursor.insertText(_from_clipboard())
        cursor.clearSelection()

    def cut(self):
        self.copy()
        self.delete()

    def delete(self):
        self._get_cursor().removeSelectedText()

    def select_all(self):
        cursor = self._get_cursor()
        if not self._document.isEmpty():
            end = self._document.characterCount() - 1
            cursor.setPosition(0)
            cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
            self._set_cursor(cursor)


def document_text_edit_menu(view, parent=None):
    actions = TextEditActions(parent=parent)
    menu = TextEditMenu(actions, parent=parent)
    controller = DocumentTextEditController(actions, view)
    menu.set_controller(controller)
    return menu


class ToolBarView(View, sywidgets.SyToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QtCore.QSize(18, 18))


class ContainerActions:
    def __init__(self, parent=None):
        super().__init__()
        self.new_item = actions.new_item(parent=parent)
        self.delete_item = actions.delete_item(parent=parent)


class ContainerToolBar(ToolBarView):
    """
    ContainerToolBar, has actions suitable for basic container views.
    QListView, QTableView, etc.
    """

    def __init__(self, actions: ContainerActions, parent=None):
        super().__init__(parent=parent)
        self.actions = actions
        self.addAction(self.actions.new_item)
        self.addAction(self.actions.delete_item)


class ContainerController(Controller):
    def __init__(self, actions: ContainerActions):
        super().__init__()
        self.actions = actions
        self.actions.new_item.triggered.connect(self.new_item)
        self.actions.delete_item.triggered.connect(self.delete_item)

    def setup(self):
        self.setup_new_item(self.actions.new_item)
        self.setup_delete_item(self.actions.delete_item)

    # Setup actions.
    def setup_new_item(self, action):
        pass

    def setup_delete_item(self, action):
        pass

    def new_item(self):
        pass

    def delete_item(self):
        pass


class TableWidgetContainerController(ContainerController):
    def __init__(self, actions: ContainerActions,
                 view: QtWidgets.QAbstractItemView):
        super().__init__(actions)
        self._view = view
        self._model = view.model()
        self._view.selectionModel().selectionChanged.connect(
            self._handle_selection_changed)

    def _handle_selection_changed(self, selected, deselected):
        self.setup_delete_item(self.actions.delete_item)

    def setup_delete_item(self, action):
        action.setEnabled(bool(self._view.selectedIndexes()))

    def new_item(self):
        self._model.insertRow(self._model.rowCount())
        self._view.scrollToBottom()

    def delete_item(self):
        indices = self._view.selectedIndexes()
        rows = {i.row() for i in indices if i.row() >= 0}
        for start, end in reversed(_intervals(rows)):
            self._model.removeRows(start, end - start + 1)


def table_container_toolbar(view, parent=None):
    actions = ContainerActions(parent=parent)
    toolbar = ContainerToolBar(actions, parent=parent)
    controller = TableWidgetContainerController(actions, view)
    toolbar.set_controller(controller)
    return toolbar
