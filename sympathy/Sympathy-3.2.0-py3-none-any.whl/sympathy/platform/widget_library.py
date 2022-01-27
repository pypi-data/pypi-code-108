# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
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
import os.path
import sys
import datetime
import functools

from sympathy.platform import qt_compat2
from sympathy.utils import prim
from sympathy.utils import search
from sympathy.platform import settings
from sympathy.platform import colors

import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets
import Qt.QtGui as QtGui


def _pygments():
    # Importing pygments can in rare cases with unicode paths
    # result in UnicodeEncodeErrors.
    import pygments.lexers
    import pygments.styles
    return pygments


def monospace_font():
    # This should select the systems default monospace font
    f = QtGui.QFont('Monospace')
    f.setStyleHint(QtGui.QFont.TypeWriter)
    f.setFixedPitch(True)
    return f


toolbar_stylesheet = """
QToolBar {
    background: %s;
    border: 1px solid %s;
    spacing: 3px;
}

QToolButton {
    border-radius: 1px;
    background-color: %s;
}

QLineEdit {
    padding: 0px;
    border-radius: 1px;
}

QToolButton:checked {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 rgba(0,0,0,60),
                                      stop: 1 rgba(0,0,0,30));
}

QToolButton:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 rgba(140,190,255,100),
                                      stop: 1 rgba(140,190,255,50));
}

QToolButton::menu-button {
    border: none;
}

QToolButton::menu-arrow:open {
    top: 1px;
}
"""


_NavigationToolbar = None


def mpl_toolbar_factory(canvas, parent, coordinates=True):
    def construct_style_sheet(toolbar):
        return toolbar_stylesheet % (get_parent_color(toolbar),
                                     get_border_color(toolbar),
                                     get_parent_color(toolbar))

    def get_parent_color(toolbar):
        color = toolbar.palette().color(toolbar.backgroundRole())
        return color.name()

    def get_border_color(toolbar):
        color = toolbar.palette().color(QtGui.QPalette.Mid)
        return color.name()

    global _NavigationToolbar
    if _NavigationToolbar is None:
        qt_compat2.backend.use_matplotlib_qt()
        from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

        class _ConnectNavigationToolbar(NavigationToolbar2QT):
            def connect_canvas(self):
                """
                Workaround to restore lost canvas interactivity.
                """
                self._id_press = self.canvas.mpl_connect(
                    'button_press_event', self._zoom_pan_handler)
                self._id_release = self.canvas.mpl_connect(
                    'button_release_event', self._zoom_pan_handler)
                self._id_drag = self.canvas.mpl_connect(
                    'motion_notify_event', self.mouse_move)
        _NavigationToolbar = _ConnectNavigationToolbar

    toolbar = _NavigationToolbar(canvas, parent, coordinates)
    toolbar.setStyleSheet(construct_style_sheet(toolbar))
    return toolbar


class ModeComboBox(QtWidgets.QComboBox):
    itemChanged = qt_compat2.Signal(str)

    def __init__(self, items, parent=None):
        super(ModeComboBox, self).__init__(parent)
        self._lookup = dict(items)
        self._rlookup = dict(zip(self._lookup.values(), self._lookup.keys()))
        self.addItems([item[1] for item in items])
        self.currentIndexChanged[int].connect(self._index_changed)

    def set_selected(self, key):
        text = self._lookup[key]
        index = self.findText(text)
        if index >= 0:
            self.setCurrentIndex(index)

    def _index_changed(self, index):
        if index >= 0:
            text = self.currentText()
            self.itemChanged.emit(self._rlookup[text])


class SpaceHandlingListWidget(QtWidgets.QListView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = QtGui.QStandardItemModel()
        self.setModel(self._model)

    def setModel(self, model):
        self._model = model
        return super().setModel(model)

    def clear(self):
        self._model.clear()

    def count(self):
        return self._model.rowCount()

    def addItem(self, item):
        row = self._model.rowCount()
        self._model.insertRow(row, item)

    def addItems(self, items):
        for item in items:
            self.addItem(item)

    def item(self, row):
        return self._model.item(row, 0)

    def items(self):
        return [self.item(row) for row in range(self.count())]

    def row(self, item):
        return self._model.indexFromItem(item).row()

    def removeItem(self, item):
        return self._model.removeRow(item.row())

    def selectedItems(self):
        return [self._model.itemFromIndex(i) for i in self.selectedIndexes()]

    def findItems(self, text, flags=QtCore.Qt.MatchExactly):
        return self._model.findItems(text, flags=flags)


class SpaceHandlingContextMenuListWidget(SpaceHandlingListWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._menu = QtWidgets.QMenu(self)
        self._actions = []
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self._custom_context_menu)

    def add_menu_action(self, action):
        self._actions.append(action)
        self._menu.addAction(action)
        self.addAction(action)

    def add_menu_separator(self):
        self._menu.addSeparator()

    def _custom_context_menu(self, pos):
        if self._actions:
            pos = self.mapToGlobal(pos)
            self._menu.exec_(pos)


class CheckableComboBox(QtWidgets.QComboBox):
    selectedItemsChanged = QtCore.Signal(bool)
    checked_items_changed = QtCore.Signal(list)

    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.setItemDelegate(QtWidgets.QStyledItemDelegate(self))

        self._listview = self.view()

        self._listview.pressed.connect(self.handleItemPressed)
        self._listview.clicked.connect(self.handleItemClicked)

    def handleItemClicked(self, index):
        self.handleItemPressed(index, alter_state=False)

    def handleItemPressed(self, index, alter_state=True):
        item = self.model().itemFromIndex(index)
        self.blockSignals(True)
        if alter_state:
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
                idx = self.select_current_index()
            else:
                item.setCheckState(QtCore.Qt.Checked)
                idx = index.row()
        else:
            if item.checkState():
                idx = index.row()
            else:
                idx = self.select_current_index()
        self.setCurrentIndex(idx)
        self.blockSignals(False)
        self.selectedItemsChanged.emit(True)
        self.currentIndexChanged.emit(idx)
        self.checked_items_changed.emit(self.checkedItemNames())

    def select_current_index(self):
        selected_items = self.checkedItems()
        if len(selected_items):
            idx = selected_items[-1].row()
        else:
            idx = 0
        return idx

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        select_all = menu.addAction('Select all')
        unselect_all = menu.addAction('Unselect all')
        invert_selection = menu.addAction('Invert selection')
        action = menu.exec_(event.globalPos())
        if action == select_all:
            for row_idx in range(self.model().rowCount()):
                self.set_checked_state(row_idx, True)
        elif action == unselect_all:
            for row_idx in range(self.model().rowCount()):
                self.set_checked_state(row_idx, False)
        elif action == invert_selection:
            for row_idx in range(self.model().rowCount()):
                state = self.get_checked_state(row_idx)
                self.set_checked_state(row_idx, not state)
        self.selectedItemsChanged.emit(True)

    def set_checked_state(self, idx, state):
        checked = QtCore.Qt.Checked if state else QtCore.Qt.Unchecked
        self.model().item(idx).setCheckState(checked)

    def get_checked_state(self, idx):
        return bool(self.model().item(idx).checkState())

    def checkedItems(self):
        selected_items = []
        for row_idx in range(self.model().rowCount()):
            item = self.model().item(row_idx)
            if item is not None and bool(item.checkState()):
                selected_items.append(item)
        return selected_items

    def checkedItemNames(self):
        return [item.text() for item in self.checkedItems()]

    def add_item(self, text, checked=False):
        item = QtGui.QStandardItem(text)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                      QtCore.Qt.ItemIsEnabled)
        is_checked = QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked
        item.setData(is_checked, QtCore.Qt.CheckStateRole)
        last_idx = self.model().rowCount()
        self.model().setItem(last_idx, 0, item)


class MacStyledItemDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        widget = QtWidgets.QCheckBox(index.data(), parent=parent)
        widget.stateChanged[bool].connect(self.stateChanged)
        return widget

    def paint(self, painter, option, index):
        option.showDecorationSelected = False
        super(MacStyledItemDelegate, self).paint(painter, option, index)

    def setEditorData(self, editor, index):
        editor.setCheckState(index.data(QtCore.Qt.EditRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.checkState(), QtCore.Qt.EditRole)

    @QtCore.Slot(bool)
    def stateChanged(self):
        self.commitData.emit(self.sender())


class LineEditDropDownMenuButton(QtWidgets.QToolButton):
    def __init__(self, icon=None, parent=None):
        super(LineEditDropDownMenuButton, self).__init__(parent)
        if isinstance(icon, QtGui.QIcon):
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(14, 14))
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.setStyleSheet(
            """
            QToolButton {
                border: none;
                padding: 0px;
                background-color: white;
            }
            QToolButton:hover { background-color: rgba(0,0,0,30); }
            QToolButton:pressed { background-color: rgba(0,0,0,60); }
            """)


class LineEditComboButton(QtWidgets.QToolButton):
    value_changed = QtCore.Signal(tuple)
    value_edited = QtCore.Signal(tuple)

    _fixed = 15

    def __init__(self, options=None, value=None, parent=None):
        super().__init__(parent=parent)

        self.setCursor(QtCore.Qt.ArrowCursor)
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self._options = []
        self._current_value = None
        self._separator = '\t'
        self._menu = QtWidgets.QMenu(parent=self)
        self.setMenu(self._menu)

        if options is None:
            options = []
        elif value is None and options:
            value = options[0]
        self.options = options
        self.current_value = value

        self._set_style_sheet()
        self._menu.triggered.connect(self._state_changed)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options
        self._menu.clear()
        self._set_drop_down_items(options)
        self._set_style_sheet()

    @property
    def current_value(self):
        return self._current_value

    @current_value.setter
    def current_value(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._text_changed(value)

    def sizeHint(self):
        hint = super(LineEditComboButton, self).sizeHint()
        fm = QtGui.QFontMetrics(self.font())
        width = max([fm.width(p[0]) for p in self.options]) + self._fixed + 5
        hint.setWidth(width)
        return hint

    def _set_style_sheet(self):
        f = monospace_font()
        self.setFont(f)
        fm = QtGui.QFontMetrics(f)
        max_len_prefix = max([fm.width(p[0]) for p in self.options])

        self.setStyleSheet("""
        QToolButton {
            border: none;
            padding: 0px;
            background-color: rgba(0,0,0,30);
            max-width: %spx;
        }

        QToolButton:hover {
            background-color: rgba(0,0,0,60);
        }

        QToolButton:pressed {
            font-weight: bold;
        }

        QToolButton::menu-indicator {
            left: 0px;
        }

        QToolButton::menu-indicator::open {
            top: 1px;
        }
        """ % (str(max_len_prefix + self._fixed)))

    def _set_drop_down_items(self, items):
        self.setEnabled(len(items) > 0)
        for short, description in items:
            action = QtWidgets.QAction(
                '{}{}{}'.format(description, self._separator, short),
                self._menu)
            self._menu.addAction(action)

    def _state_changed(self, action):
        text = action.text()
        description, short = text.split(self._separator)
        self._text_changed((short, description), edit=True)

    def _text_changed(self, text, edit=False):
        prev = self.current_value
        if isinstance(text, tuple) and text != prev:
            self._current_value = text
            self.setText(text[0])
            if edit:
                self.value_edited.emit(self.current_value)
            self.value_changed.emit(self.current_value)


class LineEditToggleableLabelButton(QtWidgets.QToolButton):
    state_changed = QtCore.Signal(bool)

    def __init__(self, prefix_states=('Off', 'On'), parent=None):
        super(LineEditToggleableLabelButton, self).__init__(parent)

        self.setCursor(QtCore.Qt.ArrowCursor)
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.prefix_states = prefix_states

        self.setCheckable(True)
        self.setText(self._prefix_states[self.isChecked()])
        self.set_style_sheet()

        self.toggled.connect(self._state_changed)

    def setChecked(self, state):
        super(LineEditToggleableLabelButton, self).setChecked(state)
        self._state_changed(state)

    @property
    def prefix_states(self):
        return self._prefix_states

    @prefix_states.setter
    def prefix_states(self, prefix_states):
        self._prefix_states = prefix_states
        self.set_style_sheet()

    def set_style_sheet(self):
        f = monospace_font()
        self.setFont(f)

        fm = QtGui.QFontMetrics(f)
        max_len_prefix = max([fm.width(p[:3]) for p in
                              self._prefix_states]) + 5

        self.setStyleSheet("""
        QToolButton {
            border: none;
            padding: 0px;
            background-color: rgba(0,0,0,30);
            max-width: %spx;
        }

        QToolButton:hover {
            background-color: rgba(0,0,0,60);
        }

        QToolButton:pressed {
            font-weight: bold;
        }
        """ % (str(max_len_prefix + 2)))

    def _state_changed(self, state):
        self.setText(self._prefix_states[state][:3])
        self.state_changed.emit(state)

    def _handle_menu(self):
        state = self.menu_action2.isChecked() is True
        self._state_changed(state)


class WidgetToolButton(QtWidgets.QToolButton):
    """ToolButton which pops up a widget."""

    def __init__(self, widget, parent=None):
        super().__init__(parent=parent)
        menu = QtWidgets.QMenu()
        self._menu = menu
        self.setMenu(menu)
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        action = QtWidgets.QWidgetAction(parent)
        action.setDefaultWidget(widget)
        menu.addAction(action)


class MenuToolButton(QtWidgets.QToolButton):
    """ToolButton which changes active action depending on selection."""
    active_action_changed = QtCore.Signal(QtWidgets.QAction)

    def __init__(self, active_action, actions, parent=None):
        super().__init__(parent=parent)
        self._actions = actions
        menu = QtWidgets.QMenu()
        # menu.setToolTipsVisible(True)
        for action in actions:
            menu.addAction(action)
        self._menu = menu
        self.setMenu(menu)
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.set_active_action(active_action)
        menu.triggered.connect(self._menu_triggered)

    def _menu_triggered(self, action):
        self.setDefaultAction(action)
        self.active_action_changed.emit(action)

    def active_action(self):
        return self.defaultAction()

    def set_active_action(self, action):
        assert action in self._actions, (
            'default_action must be among actions')
        self._menu_triggered(action)


class BaseLineTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.left = QtWidgets.QWidget(self)
        self.left_layout = QtWidgets.QHBoxLayout(self.left)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.right = QtWidgets.QWidget(self)
        self.right_layout = QtWidgets.QHBoxLayout(self.right)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(100)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def add_widget(self, widget, to_right=True):
        if to_right:
            layout = self.right_layout
            layout.insertWidget(1, widget)
        else:
            layout = self.left_layout
            layout.addWidget(widget)
        self.update_geometry()

    def remove_widget(self, widget):
        self.left_layout.removeWidget(widget)
        self.right_layout.removeWidget(widget)

    def update_geometry(self):
        frame_width = self.style().pixelMetric(
            QtWidgets.QStyle.PM_DefaultFrameWidth)
        left_padding = self.left.sizeHint().width() + frame_width + 1
        left_padding += 0 if self.left_layout.isEmpty() else 5
        right_padding = self.right.sizeHint().width() + frame_width + 1
        self.setStyleSheet("""
        QTextEdit {
            padding-left: %spx;
            padding-right: %spx;
        }
        """ % (left_padding, right_padding))
        msz = self.minimumSizeHint()
        self.setMinimumSize(
            max(msz.width(),
                self.left.sizeHint().width() + self.right.sizeHint().width() +
                frame_width * 2 + 52),
            max([self.sizeHint().height(),
                 self.right.sizeHint().height() + frame_width * 2 + 2,
                 self.left.sizeHint().height() + frame_width * 2 + 2]))

    def sizeHint(self):
        fm = QtGui.QFontMetrics(self.font())
        opt = QtWidgets.QStyleOptionFrame()
        text = self.document().toPlainText()

        h = max(fm.height(), 14) + 4
        w = fm.width(text) + 4

        opt.initFrom(self)

        o = (self.style().sizeFromContents(QtWidgets.QStyle.CT_LineEdit,
                                           opt,
                                           QtCore.QSize(w, h),
                                           self))
        return o

    def resizeEvent(self, event):
        super().resizeEvent(event)
        frame_width = self.style().pixelMetric(
            QtWidgets.QStyle.PM_DefaultFrameWidth)
        rect = self.rect()
        left_hint = self.left.sizeHint()
        right_hint = self.right.sizeHint()
        self.left.move(frame_width + 1,
                       (rect.bottom() + 1 - left_hint.height()) / 2)
        self.right.move(rect.right() - frame_width - right_hint.width(),
                        (rect.bottom() + 1 - right_hint.height()) / 2)


class BaseLineEdit(QtWidgets.QLineEdit):
    def __init__(self, inactive="", parent=None):
        super(BaseLineEdit, self).__init__(parent)

        self.left = QtWidgets.QWidget(self)
        self.left_layout = QtWidgets.QHBoxLayout(self.left)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.right = QtWidgets.QWidget(self)
        self.right_layout = QtWidgets.QHBoxLayout(self.right)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.setPlaceholderText(inactive)

        self.setMinimumWidth(100)
        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalStretch(1)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

    def add_widget(self, widget, to_right=True):
        if to_right:
            layout = self.right_layout
            layout.insertWidget(1, widget)
        else:
            layout = self.left_layout
            layout.addWidget(widget)
        self.update_geometry()

    def remove_widget(self, widget):
        self.left_layout.removeWidget(widget)
        self.right_layout.removeWidget(widget)

    def update_geometry(self):
        frame_width = self.style().pixelMetric(
            QtWidgets.QStyle.PM_DefaultFrameWidth)
        self.setStyleSheet("""
        QLineEdit {
            padding-left: %spx;
            padding-right: %spx;
        }
        """ % (self.left.sizeHint().width() + frame_width + 1,
               self.right.sizeHint().width() + frame_width + 1))
        msz = self.minimumSizeHint()
        self.setMinimumSize(
            max(msz.width(),
                self.left.sizeHint().width() + self.right.sizeHint().width() +
                frame_width * 2 + 52),
            max([msz.height(),
                 self.right.sizeHint().height() + frame_width * 2 + 2,
                 self.left.sizeHint().height() + frame_width * 2 + 2]))

    def resizeEvent(self, event):
        frame_width = self.style().pixelMetric(
            QtWidgets.QStyle.PM_DefaultFrameWidth)
        rect = self.rect()
        left_hint = self.left.sizeHint()
        right_hint = self.right.sizeHint()
        self.left.move(frame_width + 1,
                       (rect.bottom() + 1 - left_hint.height()) / 2)
        self.right.move(rect.right() - frame_width - right_hint.width(),
                        (rect.bottom() + 1 - right_hint.height()) / 2)


class ClearButtonLineEdit(QtWidgets.QLineEdit):
    def __init__(self, placeholder="", clear_button=True, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        if clear_button:
            self.setClearButtonEnabled(True)


class PrefixLineEdit(BaseLineEdit):
    def __init__(self, placeholder="", prefix="", parent=None):
        super(PrefixLineEdit, self).__init__(placeholder, parent)

        self.prefix_label = QtWidgets.QLabel(prefix, parent=self)
        self.add_widget(self.prefix_label, to_right=False)

    def set_prefix(self, prefix):
        self.prefix_label.setText(prefix)


class ToggleablePrefixLineEdit(BaseLineEdit):
    state_toggled = QtCore.Signal(bool)

    def __init__(self, placeholder="", state=True, prefix_states=('Off', 'On'),
                 parent=None):
        super(ToggleablePrefixLineEdit, self).__init__(placeholder, parent)

        assert (len(prefix_states) == 2)
        self.prefix_button = LineEditToggleableLabelButton(
            prefix_states=prefix_states, parent=self)
        self.prefix_button.setChecked(state)
        self.add_widget(self.prefix_button, to_right=False)

        self.prefix_button.state_changed.connect(self.state_toggled)

    def get_state(self):
        return self.prefix_button.isChecked()

    def set_state(self, state):
        self.prefix_button.setChecked(state)

    def set_prefix_states(self, prefix_states):
        if len(prefix_states) == 2:
            self.prefix_button.set_prefix_states(prefix_states)


class MenuLineEdit(BaseLineEdit):
    state_changed = QtCore.Signal(tuple)
    state_edited = QtCore.Signal(tuple)

    def __init__(self, placeholder="", options=None, value=None, parent=None):
        super(MenuLineEdit, self).__init__(placeholder, parent)

        self.prefix_button = LineEditComboButton(
            options=options, value=value, parent=self)
        self.add_widget(self.prefix_button, to_right=False)
        self.prefix_button.value_edited.connect(self.state_edited)
        self.prefix_button.value_changed.connect(self.state_changed)

    @property
    def current_value(self):
        return self.prefix_button.current_value

    @current_value.setter
    def current_value(self, value):
        self.prefix_button.current_value = value


class SyBaseToolBar(QtWidgets.QToolBar):
    def __init__(self, *args, **kwargs):
        super(SyBaseToolBar, self).__init__(*args, **kwargs)
        self.setStyleSheet(self.construct_style_sheet())

    def construct_style_sheet(self):
        return toolbar_stylesheet % (self.get_parent_color(),
                                     self.get_border_color(),
                                     self.get_parent_color())

    def get_parent_color(self):
        color = self.palette().color(self.backgroundRole())
        return color.name()

    def get_border_color(self):
        color = self.palette().color(QtGui.QPalette.Mid)
        return color.name()


class TogglePushButton(QtWidgets.QPushButton):
    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)
        self.setCheckable(True)


def preview_icon():
    pixmap = QtGui.QPixmap(prim.get_icon_path(
        'node_open.svg'))
    return QtGui.QIcon(pixmap)


class PreviewButton(TogglePushButton):
    def __init__(self, parent=None):
        super().__init__(preview_icon(), 'Preview')


def filter_icon():
    pixmap = QtGui.QPixmap(prim.get_icon_path(
        'actions/view-filter-symbolic.svg'))
    return QtGui.QIcon(pixmap)


class FilterButton(TogglePushButton):
    def __init__(self, parent=None):
        super().__init__(filter_icon(), '')
        self.setFlat(True)


def edit_icon():
    pixmap = QtGui.QPixmap(prim.get_icon_path(
        'actions/fontawesome/svgs/solid/edit.svg'))
    return QtGui.QIcon(pixmap)


def copy_icon():
    pixmap = QtGui.QPixmap(prim.get_icon_path(
        'actions/fontawesome/svgs/regular/copy.svg'))
    return QtGui.QIcon(pixmap)


class EditButton(TogglePushButton):
    def __init__(self, parent=None):
        super().__init__(edit_icon(), '')
        self.setFlat(True)


class ShowButton(TogglePushButton):
    def __init__(self, parent=None):
        super().__init__(preview_icon(), '')
        self.setToolTip('Show/Hide.')


class ToggleFilterButton(FilterButton):
    def __init__(self, filter_widget=None, next_to_widget=None):
        """
        Button with a magnifying glass intended for toggling
        the display of filter options.

        If a filter_widget is provided it will automatically
        be connected and hidden by default.

        When placing it next to another widget it will look best if the height
        is the same: use set_size or next_to_widget.
        """
        super().__init__()
        self.setToolTip('Show/Hide filter.')
        self.setCheckable(True)
        self.setFlat(True)

        self._filter_widget = filter_widget
        if self._filter_widget:
            # Default hidden.
            self._filter_widget.hide()
            self.toggled.connect(self._toggled)

        if next_to_widget:
            # TODO(erik): Assuming a 1px border (which is not always true).
            # Next to a combobox seems good on Windows 10 and worse on Mac OS.
            size = next_to_widget.sizeHint().height() + 2
            self.set_size(size)

    def set_size(self, size):
        self.setIconSize(QtCore.QSize(size, size))
        self.setFixedSize(size, size)

    def _toggled(self, checked=False):
        if checked:
            self._filter_widget.show()
        else:
            self._filter_widget.hide()


class TogglePreviewButton(TogglePushButton):
    def __init__(self, child_widget=None, next_to_widget=None):
        """
        Button with a eye icon intended for toggling
        the display of preview.

        If a child_widget is provided it will automatically
        be connected and hidden by default.

        When placing it next to another widget it will look best if the height
        is the same: use set_size or next_to_widget.
        """
        icon = preview_icon()
        super().__init__(icon, '')
        self.setToolTip('Show/Hide preview.')
        self.setFlat(True)

        self._child_widget = child_widget
        if self._child_widget:
            # Default hidden.
            self._child_widget.hide()
            self.toggled.connect(self._toggled)

        if next_to_widget:
            # TODO(erik): Assuming a 1px border (which is not always true).
            # Next to a combobox seems good on Windows 10 and worse on Mac OS.
            size = next_to_widget.sizeHint().height() + 2
            self.set_size(size)

    def set_size(self, size):
        self.setIconSize(QtCore.QSize(size, size))
        self.setFixedSize(size, size)

    def _toggled(self, checked=False):
        if checked:
            self._child_widget.show()
        else:
            self._child_widget.hide()


class SortedSearchFilterModel(QtCore.QSortFilterProxyModel):
    """
    Search filter model which sorts the data in ascending order.
    """
    filter_changed = qt_compat2.Signal(str)

    def __init__(self, parent=None):
        self._filter = None
        super().__init__(parent)

    def set_filter(self, filter):
        if filter is not None:
            self._filter = search.fuzzy_free_pattern(filter)
            self.invalidateFilter()
        self.filter_changed.emit(filter)

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        if self._filter is None or model is None:
            return True
        index = model.index(
            source_row, model.columnCount() - 1, source_parent)
        data = model.data(index, self.filterRole())
        if data is None:
            return True
        return search.matches(self._filter, data)


class OrderedSearchFilterModel(SortedSearchFilterModel):
    """
    Search Filter model which keeps the ordering from the source
    model.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def lessThan(self, left, right):
        return self.mapFromSource(left).row() < self.mapFromSource(right).row()


class OrderedComboboxSearchFilterModel(OrderedSearchFilterModel):
    """
    Search Filter model which keeps the ordering from the source
    model.

    For convenience also creates a new combobox model which is set as
    source model.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Using existing model for standard combobox model behavior.
        self._dummy_combobox = QtWidgets.QComboBox()
        self.setSourceModel(self._dummy_combobox.model())

    def clear(self):
        self.sourceModel().clear()


class ToggleFilterCombobox(QtWidgets.QWidget):
    currentIndexChanged = qt_compat2.Signal(int)

    def __init__(self, combobox=None, use_filter=True,
                 parent=None):
        super().__init__(parent=parent)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(0)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(0)

        if combobox is None:
            combobox = QtWidgets.QComboBox()
        self._combobox = combobox

        self._search_model = OrderedComboboxSearchFilterModel(
            self._combobox)
        self._combobox.setModel(self._search_model)
        self._filter_widget = ClearButtonLineEdit(
            placeholder='Filter')

        hlayout.addWidget(self._combobox)
        self._filter_button = ToggleFilterButton(
            filter_widget=self._filter_widget,
            next_to_widget=self._combobox)

        if use_filter:
            hlayout.addWidget(self._filter_button)

        vlayout.addLayout(hlayout)
        vlayout.addWidget(self._filter_widget)
        self.setLayout(vlayout)
        self._combobox.currentIndexChanged[int].connect(
            self.currentIndexChanged)
        self._search_model.setFilterRole(QtCore.Qt.DisplayRole)
        self._search_model.set_filter('')
        self._filter_widget.textChanged.connect(self._search_model.set_filter)
        self._search_model.filter_changed.connect(self._filter_changed)

    def _filter_changed(self, filter):
        # Auto-select after filtering if nothing nothing is already selected.
        if filter and self._combobox.currentIndex() == -1:
            index = self._search_model.index(
                self._search_model.rowCount() - 1,
                self._search_model.columnCount() - 1)

            if index.isValid():
                src_index = self._search_model.mapToSource(index)
                self._combobox.setCurrentIndex(src_index.row())

    def addItems(self, items):
        items = items
        for text in items:
            item = QtGui.QStandardItem(text)
            self._search_model.sourceModel().appendRow(item)
        self._search_model.set_filter(self._filter_widget.text())

    def clear(self):
        # Clear combobox first to improve performance.
        self._combobox.clear()
        self._search_model.sourceModel().clear()

    def combobox(self):
        return self._combobox


# TODO(erik): refactor, move to appropriate utility module?
def create_action(text, icon=None, icon_name=None, tooltip_text=None,
                  is_checkable=False, is_checked=False,
                  triggered=None, toggled=None, parent=None):
    """
    Convenience function for creating an action and optionally
    connecting it.

    Many properties can be specified: text, icon, tooltip, checkable,
    checked.

    Signal handlers can be specified using: triggered and toggled.
    """
    if icon is None:
        if icon_name is not None:
            icon = QtGui.QIcon(prim.get_icon_path(icon_name))
        else:
            icon = None

    if icon is None:
        action = QtWidgets.QAction(text, parent=parent)
    else:
        action = QtWidgets.QAction(icon, text, parent=parent)

    if tooltip_text is not None:
        action.setToolTip(tooltip_text)
    if is_checkable:
        action.setCheckable(is_checkable)
        action.setChecked(is_checked)

    if triggered:
        action.triggered.connect(triggered)
    if toggled:
        action.toggled.connect(toggled)
    return action


class SyToolBar(SyBaseToolBar):
    def __init__(self, *args, **kwargs):
        super(SyToolBar, self).__init__(*args, **kwargs)
        self.setMinimumHeight(22)
        self.setMaximumHeight(38)
        self.setIconSize(QtCore.QSize(26, 26))

    def add_action(self, text, icon_name=None, tooltip_text=None,
                   is_checkable=False, is_checked=False,
                   receiver=None, triggered=None, toggled=None, icon=None):
        """
        Convenience method for creating an action and adding it.
        The action is created using create_action and the toolbar becomes
        the parent.

        Returns created action.
        """
        triggered = triggered or receiver

        action = create_action(text,
                               icon_name=icon_name,
                               icon=icon,
                               tooltip_text=tooltip_text,
                               is_checkable=is_checkable,
                               is_checked=is_checked,
                               triggered=triggered,
                               toggled=toggled,
                               parent=self)
        self.addAction(action)
        return action

    def addStretch(self):
        spacer = QtWidgets.QWidget(parent=self)
        spacer.setMinimumWidth(0)
        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalStretch(0)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        spacer.setSizePolicy(policy)
        self.addWidget(spacer)


class BasePreviewTable(QtWidgets.QTableView):

    def __init__(self, parent=None):
        super(BasePreviewTable, self).__init__(parent)
        self.setWordWrap(False)

        self._context_menu_actions = []

        self.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectItems)
        self.setSelectionMode(
            QtWidgets.QAbstractItemView.ContiguousSelection)
        self.ScrollHint(
            QtWidgets.QAbstractItemView.EnsureVisible)
        self.setCornerButtonEnabled(True)
        self.setShowGrid(True)
        self.setAlternatingRowColors(True)
        self.setMinimumHeight(100)

        vertical_header = self.verticalHeader()
        vertical_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        vertical_header.customContextMenuRequested.connect(
            self.vertical_header_context_menu)
        horizontal_header = self.horizontalHeader()
        horizontal_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        horizontal_header.customContextMenuRequested.connect(
            self.horizontal_header_context_menu)
        self.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel)

    def vertical_header_context_menu(self, pos):
        if not self._context_menu_actions:
            return
        header = self.verticalHeader()
        row_idx = header.logicalIndexAt(pos)
        self._show_context_menu(row_idx, -1, header.mapToGlobal(pos))

    def horizontal_header_context_menu(self, pos):
        if not self._context_menu_actions:
            return
        header = self.horizontalHeader()
        column_idx = header.logicalIndexAt(pos)
        self._show_context_menu(-1, column_idx, header.mapToGlobal(pos))

    def contextMenuEvent(self, event):
        if not self._context_menu_actions:
            return

        global_pos = event.globalPos()
        pos = self.viewport().mapFromGlobal(global_pos)
        qindex = self.indexAt(pos)
        row_idx = qindex.row()
        column_idx = qindex.column()

        self._show_context_menu(row_idx, column_idx, global_pos)
        event.accept()

    def _show_context_menu(self, row, column, pos):
        current_menu_items = self.create_menu(row, column)
        action = self.menu.exec_(pos)
        if action:
            callback = current_menu_items[action]
            callback(row, column)

    def create_menu(self, row_idx, column_idx):
        self.menu = QtWidgets.QMenu(self)
        current_menu_items = {}
        for action_param in self._context_menu_actions:
            title, func, icon_name, validate_func = action_param

            is_valid = validate_func(row_idx, column_idx)
            if is_valid:
                if icon_name is not None:
                    icon = QtGui.QIcon(prim.get_icon_path(icon_name))
                    action = self.menu.addAction(icon, title)
                else:
                    action = self.menu.addAction(title)
                current_menu_items[action] = func
        return current_menu_items

    def add_context_menu_action(self, title, function, icon_name=None,
                                validate_callback=None, key_sequence=None):
        # Create a separate action for the shortcut:
        if validate_callback is None:
            def validate_callback(row, col): True
        if key_sequence is not None:
            if icon_name is not None:
                icon = QtGui.QIcon(prim.get_icon_path(icon_name))
                action = QtWidgets.QAction(icon, title, self)
            else:
                action = QtWidgets.QAction(title, self)
            action.setShortcuts(key_sequence)
            action.triggered.connect(
                lambda: self._emit_context_menu_clicked(function))
            self.addAction(action)

        self._context_menu_actions.append((title, function, icon_name,
                                           validate_callback))

    def _emit_context_menu_clicked(self, callback, row=0, column=0):
        callback(row, column)

    def selection(self):
        """
        Return a tuple with two ranges (startrow, endrow, startcol, endcol) for
        the currently selected area. Both ranges are half closed meaning that
        e.g. rows where startrow <= row < endrow are selected.
        """
        selection_model = self.selectionModel()
        if not selection_model.selection().count():
            return None
        selection_range = selection_model.selection()[0]
        minrow, maxrow = selection_range.top(), selection_range.bottom() + 1
        mincol, maxcol = selection_range.left(), selection_range.right() + 1
        return (minrow, maxrow, mincol, maxcol)

    def center_on_cell(self, row=None, col=None):
        if row is None:
            row = max(self.rowAt(0), 0)
        if col is None:
            col = max(self.columnAt(0), 0)

        index = self.model().createIndex(row, col, 0)
        if index.isValid():
            self.scrollTo(index)


class EnhancedPreviewTable(QtWidgets.QWidget):
    def __init__(self, model=None, filter_function=None, parent=None):
        super(EnhancedPreviewTable, self).__init__(parent)

        if model is None:
            model = QtCore.QAbstractItemModel()
        self._model = model
        self._transposed = False
        self._filter_function = filter_function

        self._preview_table = BasePreviewTable()

        # Toolbar
        self._toolbar = SyToolBar()
        # Search field
        self._filter_lineedit = ClearButtonLineEdit(placeholder='Search',
                                                    parent=self)
        self._filter_lineedit.setMaximumWidth(250)

        self._toolbar.addWidget(self._filter_lineedit)
        self._toolbar.addStretch()

        # Legend
        self._legend_layout = QtWidgets.QHBoxLayout()
        self._legend_layout.addStretch()

        # Setup layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._toolbar)
        layout.addWidget(self._preview_table)
        layout.addLayout(self._legend_layout)

        self.setLayout(layout)

        # Connect signals
        self._filter_lineedit.textChanged[str].connect(
            self._filter_columns)

        self.set_model(self._model, self._transposed)

    def preview_table(self):
        return self._preview_table

    def toolbar(self):
        return self._toolbar

    def _show_all(self):
        """
        Show all items in the table.
        This method is expensive so don't call it if the table is too big.
        """
        headers = [self._preview_table.horizontalHeader(),
                   self._preview_table.verticalHeader()]
        for header in headers:
            for i in range(header.count()):
                header.showSection(i)

    def _filter_columns(self, pattern):
        try:
            table = self._model.table()
        except AttributeError:
            self._show_all()
            return
        if table is None:
            # No table available for filtering. This probably means that we are
            # currently showing attributes, so simply show all rows and
            # columns.
            self._show_all()
            return

        columns = [table.col(name) for name in table.column_names()]
        item_count = len(columns)

        filter_func = self._filter_function
        if filter_func is None:
            # Fall back to showing all columns
            self._show_all()
            return

        filtered_item_indexes = set(filter_func(pattern, columns))

        if self._transposed:
            set_hidden = self._preview_table.setRowHidden
        else:
            set_hidden = self._preview_table.setColumnHidden
        for i in range(item_count):
            set_hidden(i, i not in filtered_item_indexes)

    def reapply_filter(self):
        filter_pattern = self._filter_lineedit.text()
        self._filter_lineedit.textChanged.emit(filter_pattern)

    def clear_filter(self):
        self._filter_lineedit.textChanged.emit('')

    def set_model(self, model, transposed):
        # Temporary reset the filter to make sure that all columns and rows are
        # shown before changing the model.
        self.clear_filter()
        self._model = model
        self._transposed = transposed
        self._preview_table.setModel(model)
        self.reapply_filter()

    def set_filter_function(self, func):
        self._filter_function = func

    def add_widget_to_legend(self, widget, on_left=False):
        legend_layout = self._legend_layout
        if on_left:
            legend_layout.insertWidget(0, widget)
        else:
            legend_layout.addWidget(widget)

    def add_widget_to_layout(self, widget, on_top=False):
        layout = self.layout()
        if on_top:
            layout.insertWidget(0, widget)
        else:
            layout.addWidget(widget)

    def add_layout_to_layout(self, layout, on_top=False):
        main_layout = self.layout()
        if on_top:
            main_layout.insertLayout(0, layout)
        else:
            main_layout.addLayout(layout)


class RowColumnLegend(QtWidgets.QGroupBox):
    def __init__(self, row=0, column=0, parent=None):
        super(RowColumnLegend, self).__init__(parent)
        self._row = row
        self._column = column
        self._init_gui()

    def _init_gui(self):
        self._row_column_label = QtWidgets.QLabel()
        self._row_column_label.setMaximumHeight(16)

        row_count_layout = QtWidgets.QHBoxLayout()
        row_count_layout.setContentsMargins(0, 0, 0, 0)
        row_count_layout.setAlignment(QtCore.Qt.AlignCenter)
        icon_label = QtWidgets.QLabel()
        icon = QtGui.QPixmap(prim.get_icon_path(
            'actions/view-grid-symbolic.svg'))
        icon_label.setPixmap(icon)
        row_count_layout.addWidget(icon_label)
        row_count_layout.addWidget(self._row_column_label)

        self.setLayout(row_count_layout)
        self._update_row_column_label()

    def _update_row_column_label(self):
        text = '{} \u00D7 {}'.format(self._row, self._column)
        self._row_column_label.setText(text)
        tooltip = '{} row{}<br>{} column{}'.format(
            self._row, '' if self._row == 1 else 's',
            self._column, '' if self._column == 1 else 's')
        self.setToolTip(tooltip)

    def set_row(self, row):
        self._row = row
        self._update_row_column_label()

    def set_column(self, column):
        self._column = column
        self._update_row_column_label()

    def set_row_column(self, row, column):
        self._row = row
        self._column = column
        self._update_row_column_label()


class PathMixinWidget(QtWidgets.QWidget):
    """
    Mixin which adds context menu actions *Make absolute* and *Make relative*
    to self._editor. It also provides a few helpers.
    """

    def __init__(self, parent=None):
        super(PathMixinWidget, self).__init__(parent)

        make_relative = QtWidgets.QAction(
            'Make relative', self._editor)
        make_absolute = QtWidgets.QAction('Make absolute', self._editor)
        self._editor.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self._editor.addAction(make_relative)
        self._editor.addAction(make_absolute)
        make_relative.triggered.connect(self._make_relative)
        make_absolute.triggered.connect(self._make_absolute)

    def _make_default_path(self, path):
        """Helper for making the default kind of path."""
        res = path
        if self._default_relative and self._root_path is not None:
            res = self._make_relative_path(path)
        return res

    def _make_relative_path(self, path):
        """Helper for making relative path out of path."""
        res = path
        if os.path.isabs(path):
            try:
                res = os.path.relpath(path, self._root_path)
            except Exception:
                pass
        return res

    def _make_absolute_path(self, path):
        """Helper for making absolute path out of path."""
        res = path
        try:
            res = os.path.normpath(
                os.path.join(self._root_path, path))
        except Exception:
            pass
        return res


class PathListWidget(PathMixinWidget):
    """
    Widget with a list of paths, buttons to add remove paths and some utilities
    for handling relative/absolute paths.
    """
    def __init__(self, paths, root_path=None, default_relative=False,
                 recent=None, parent=None):
        self._root_path = root_path
        self._default_relative = default_relative
        self._editor = QtWidgets.QListWidget()
        self._editor.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self._editor.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self._recent = recent

        super(PathListWidget, self).__init__(parent)
        self.set_items(paths)

        remove_action = QtWidgets.QAction('Remove items', self._editor)
        remove_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete))
        remove_action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self._editor.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self._editor.addAction(remove_action)
        remove_action.triggered.connect(self._remove_path)
        add_button = QtWidgets.QPushButton('Add')
        remove_button = QtWidgets.QPushButton('Remove')

        buttons_container = QtWidgets.QVBoxLayout()
        buttons_container.addWidget(add_button)
        buttons_container.addWidget(remove_button)
        if recent is not None:
            recent_button = QtWidgets.QPushButton('Recent')
            buttons_container.addWidget(recent_button)
            menu = QtWidgets.QMenu(recent_button)
            for i, item in enumerate(recent, 1):
                action = menu.addAction(item)
                action.triggered.connect(functools.partial(
                    lambda item: self._add_item(item), item))
            recent_button.setMenu(menu)
        buttons_container.addStretch()

        container = QtWidgets.QHBoxLayout()
        container.setContentsMargins(1, 1, 1, 1)
        container.addWidget(self._editor)
        container.addLayout(buttons_container)
        self.setLayout(container)

        add_button.clicked.connect(self._add_path_dialog)
        remove_button.clicked.connect(self._remove_path)

    def add_item(self, path):
        self._add_item(path)

    def set_items(self, paths):
        self._editor.clear()
        for path in paths:
            self._add_item(path)
        self._initial_paths = list(paths)

    def _add_item(self, path):
        """Append a path to the list."""
        item = QtWidgets.QListWidgetItem(path)
        item.setFlags(QtCore.Qt.ItemIsEnabled |
                      QtCore.Qt.ItemIsSelectable |
                      QtCore.Qt.ItemIsEditable |
                      QtCore.Qt.ItemIsDragEnabled)
        self._editor.addItem(item)

    def _add_path_dialog(self):
        """Open a dialog to let the user select a directory, which is added."""
        default_directory = self._root_path or settings.get_default_dir()
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Choose a directory', default_directory)
        if len(dir_) > 0:
            dir_ = self._make_default_path(dir_)
            self._add_item(dir_)

    def _make_relative(self):
        """Make all selected paths relative."""
        if len(self._editor.selectedItems()) > 0:
            for selected_item in self._editor.selectedItems():
                old_path = selected_item.text()
                new_path = self._make_relative_path(old_path)
                if old_path != new_path:
                    self._editor.model().setData(
                        self._editor.indexFromItem(selected_item), new_path,
                        QtCore.Qt.DisplayRole)

    def _make_absolute(self):
        """Make all selected paths absolute."""
        if len(self._editor.selectedItems()) > 0:
            for selected_item in self._editor.selectedItems():
                old_path = selected_item.text()
                new_path = self._make_absolute_path(old_path)
                if old_path != new_path:
                    self._editor.model().setData(
                        self._editor.indexFromItem(selected_item), new_path,
                        QtCore.Qt.DisplayRole)

    def _remove_path(self):
        """Remove all selected paths."""
        if len(self._editor.selectedItems()) > 0:
            for selected_item in self._editor.selectedItems():
                row = self._editor.row(selected_item)
                self._editor.takeItem(row)
                del selected_item

    def paths(self):
        """Return a list of all paths in the list."""
        row_count = self._editor.model().rowCount(QtCore.QModelIndex())
        return [self._editor.item(i).text()
                for i in range(row_count)]

    def recent(self):
        new_recent_libs = []
        new_libs = [path for path in self.paths()
                    if path not in self._initial_paths]
        recent_libs = self._recent or []

        for lib in new_libs + recent_libs:
            if lib not in new_recent_libs:
                new_recent_libs.append(lib)
        return new_recent_libs

    def clear(self):
        self._editor.clear()


class PathLineEdit(PathMixinWidget):
    """
    Widget with a single path editor and some utilities
    for handling relative/absolute paths.
    """

    def __init__(self, path, root_path=None, default_relative=False,
                 placeholder_text=None, filter=None, parent=None):
        self._root_path = root_path
        self._default_relative = default_relative
        self._filter = filter
        self._editor = QtWidgets.QLineEdit()
        self._editor.setText(path or '')
        if placeholder_text:
            self._editor.setPlaceholderText(placeholder_text)

        super(PathLineEdit, self).__init__(parent)
        self._editor.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        dialog_button = QtWidgets.QPushButton('...')
        container = QtWidgets.QHBoxLayout()
        container.setContentsMargins(1, 1, 1, 1)
        container.addWidget(self._editor)
        container.addWidget(dialog_button)
        self.setLayout(container)
        dialog_button.clicked.connect(self._add_path_dialog)

    def _add_path_dialog(self):
        """Open a dialog to let the user select a directory, which is added."""
        default_directory = self._root_path or settings.get_default_dir()
        fq_filename = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select file", default_directory, self._filter)[0]
        if len(fq_filename) > 0:
            fq_filename = self._make_default_path(fq_filename)
            self._change_item(fq_filename)

    def _change_item(self, path):
        """Change current itemt."""
        self._editor.setText(path)

    def _make_relative(self):
        """Make all selected paths relative."""
        old_path = self._editor.text()
        new_path = self._make_relative_path(old_path)
        if old_path != new_path:
            self._editor.setText(new_path)

    def _make_absolute(self):
        """Make all selected paths absolute."""
        old_path = self._editor.text()
        new_path = self._make_absolute_path(old_path)
        if old_path != new_path:
            self._editor.setText(new_path)

    def path(self):
        return self._editor.text()


class StackedTextViews(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._combo = QtWidgets.QComboBox()
        self._stacked = QtWidgets.QStackedWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._combo)
        layout.addWidget(self._stacked)
        self.setLayout(layout)

        self._combo.currentIndexChanged[int].connect(
            self._stacked.setCurrentIndex)

    def add_text(self, label, text):
        text_edit = SyTextEdit(text)
        text_edit.setReadOnly(True)
        self._combo.addItem(label)
        self._stacked.addWidget(text_edit)


class SearchBar(SyBaseToolBar):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setMinimumHeight(22)
        self.setMaximumHeight(38)
        self.setIconSize(QtCore.QSize(18, 18))

        style = self.style()

        self._line_edit = QtWidgets.QLineEdit()
        self._line_edit.setPlaceholderText('Find in text')
        self._line_edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.find_action = QtWidgets.QAction('Find', parent=self)
        self.find_action.setShortcutContext(
            QtCore.Qt.WidgetWithChildrenShortcut)
        self.find_action.setShortcut(QtGui.QKeySequence.Find)
        self.find_action.setShortcutVisibleInContextMenu(True)

        self.forward_action = QtWidgets.QAction(
            'Find Next', parent=self)
        self.forward_action.setShortcutContext(
            QtCore.Qt.WidgetWithChildrenShortcut)
        self.forward_action.setShortcut(QtGui.QKeySequence.FindNext)
        self.forward_action.setShortcutVisibleInContextMenu(True)

        self.backward_action = QtWidgets.QAction(
            'Find Previous', parent=self)
        self.backward_action.setShortcutContext(
            QtCore.Qt.WidgetWithChildrenShortcut)
        self.backward_action.setShortcut(QtGui.QKeySequence.FindPrevious)
        self.backward_action.setShortcutVisibleInContextMenu(True)

        self.close_action = QtWidgets.QAction(parent=self)

        self.backward_action.setIcon(QtGui.QIcon(prim.get_icon_path(
            'actions/go-up-symbolic.svg')))
        self.forward_action.setIcon(QtGui.QIcon(prim.get_icon_path(
            'actions/go-down-symbolic.svg')))
        self.close_action.setIcon(style.standardIcon(
            QtWidgets.QStyle.SP_LineEditClearButton))

        self._line_edit.addAction(self.backward_action)
        self._line_edit.addAction(self.forward_action)

        self.addAction(self.close_action)
        self.addWidget(self._line_edit)
        self.addAction(self.backward_action)
        self.addAction(self.forward_action)

        self.close_action.triggered.connect(self.close)
        self.find_action.triggered.connect(self._find)
        self._line_edit.customContextMenuRequested.connect(
            self._custom_lineedit_context_menu)

    def _find(self, *args, **kwargs):
        self.open()

    def _custom_lineedit_context_menu(self, pos):
        pos = self._line_edit.mapToGlobal(pos)
        menu = self._line_edit.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction(self.find_action)
        if self.isVisible():
            menu.addAction(self.backward_action)
            menu.addAction(self.forward_action)
        menu.exec_(pos)

    def text(self):
        return self._line_edit.text()

    def open(self):
        self.show()
        QtCore.QTimer.singleShot(0, self._line_edit.setFocus)
        QtCore.QTimer.singleShot(0, self._line_edit.selectAll)

    def close(self):
        self.hide()


class SearchableTextEdit(QtWidgets.QWidget):
    textChanged = qt_compat2.Signal()

    def __init__(self, text_edit, search_bar, parent=None):
        super().__init__(parent=parent)
        self._search_bar = search_bar
        self._text_edit = text_edit

        self.addAction(self._search_bar.find_action)
        self.addAction(self._search_bar.forward_action)
        self.addAction(self._search_bar.backward_action)

        self._text_edit.addAction(self._search_bar.find_action)
        self._text_edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._text_edit)
        self._search_bar.hide()
        layout.addWidget(self._search_bar)
        self.setLayout(layout)

        self._search_bar.forward_action.triggered.connect(
            self._forward_search)
        self._search_bar.backward_action.triggered.connect(
            self._backward_search)
        self._text_edit.textChanged.connect(self.textChanged)
        self._text_edit.customContextMenuRequested.connect(
            self._custom_textedit_context_menu)

    def _forward_search(self, *args, **kwargs):
        term = self._search_term()
        if term:
            self._text_edit.find(term)

    def _backward_search(self, *args, **kwargs):
        term = self._search_term()
        if term:
            self._text_edit.find(term, QtGui.QTextDocument.FindBackward)

    def _search_term(self):
        if self._search_bar.isVisible():
            return self._search_bar.text()
        return ''

    def _custom_textedit_context_menu(self, pos):
        pos = self._text_edit.mapToGlobal(pos)
        menu = self._text_edit.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction(self._search_bar.find_action)
        if self._search_bar.isVisible():
            menu.addAction(self._search_bar.backward_action)
            menu.addAction(self._search_bar.forward_action)
        menu.exec_(pos)

    # Intended to more or less satisfy QTextEdit interface.
    # Please forward whatever methods and signals that are needed.

    def toPlainText(self):
        return self._text_edit.toPlainText()

    def setPlainText(self, text):
        return self._text_edit.setPlainText(text)

    def toHtml(self):
        return self._text_edit.toHtml()

    def setHtml(self, text):
        return self._text_edit.setHtml(text)

    def setText(self, text):
        return self._text_edit.setText(text)

    def textCursor(self):
        return self._text_edit.textCursor()

    def setTextCursor(self, cursor):
        return self._text_edit.setTextCursor(cursor)

    def isReadOnly(self):
        return self._text_edit.isReadOnly()

    def setReadOnly(self, ro):
        return self._text_edit.setReadOnly(ro)

    def wordWrapMode(self, policy):
        return self._text_edit.wordWrapMode()

    def setWordWrapMode(self, policy):
        return self._text_edit.setWordWrapMode(policy)

    def document(self):
        return self._text_edit.document()

    def setDocument(self, document):
        return self._text_edit.setDocument(document)

    def font(self):
        return self._text_edit.font()

    def setFont(self, font):
        return self._text_edit.setFont(font)


class SyTextEdit(SearchableTextEdit):
    def __init__(self, text=None, parent=None):
        if text:
            text_edit = QtWidgets.QTextEdit(text)
        else:
            text_edit = QtWidgets.QTextEdit()

        search_bar = SearchBar()
        super().__init__(text_edit, search_bar, parent=parent)
        self._text_edit.setAcceptRichText(False)


class CodeEditMixin(object):
    def __init__(self, language='python', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(monospace_font())
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)

        self._highlighter = PygmentsHighlighter(self, language)
        self.textChanged.connect(self._highlighter.rehighlight)


class CodeEdit(CodeEditMixin, SyTextEdit):
    pass


class PygmentsHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, text_edit_widget, language):
        super(PygmentsHighlighter, self).__init__(text_edit_widget.document())
        style = settings.get_code_editor_theme()
        try:
            self._style = _pygments().styles.get_style_by_name(style)
        except _pygments().util.ClassNotFound:
            self._style = _pygments().styles.get_style_by_name('default')
        self._lexer = _pygments().lexers.get_lexer_by_name(
            language, stripall=True)

        self._tokens = []
        self._highlighting = False

        # Set background color from style
        palette = text_edit_widget.palette()
        palette.setColor(
            QtGui.QPalette.Base, QtGui.QColor(self._style.background_color))
        text_edit_widget.setPalette(palette)

    def _qt_format_for_token(self, token):
        styles = self._style.style_for_token(token)
        f = QtGui.QTextCharFormat()
        if styles['color'] is not None:
            f.setForeground(QtGui.QBrush(QtGui.QColor(
                '#' + styles['color'])))
        if styles['bgcolor'] is not None:
            f.setBackground(QtGui.QBrush(QtGui.QColor(
                '#' + styles['bgcolor'])))
        if styles['bold']:
            f.setFontWeight(QtGui.QFont.Bold)
        if styles['italic']:
            f.setFontItalic(True)
        return f

    def _parse_document(self):
        text = self.document().toPlainText()
        self._tokens = list(self._lexer.get_tokens_unprocessed(text))

    def rehighlight(self):
        # Prevent highlighting calling itself
        if self._highlighting:
            return
        self._highlighting = True

        self._parse_document()
        super(PygmentsHighlighter, self).rehighlight()
        self._highlighting = False

    def highlightBlock(self, text):
        block_start = self.previousBlockState() + 1
        block_end = block_start + len(text)

        for token_start, token_type, value in self._tokens:
            # Constrain token to block limits
            token_start = max(token_start, block_start)
            token_end = min(token_start + len(value), block_end)
            token_length = token_end - token_start

            # Skip tokens that are completely outside of this block
            if token_length <= 0:
                continue

            self.setFormat(token_start - block_start, token_length,
                           self._qt_format_for_token(token_type))

        # Adding one for the inevitable trailing newline character
        self.setCurrentBlockState(self.previousBlockState() + len(text) + 1)


class BaseLineCodeEdit(CodeEditMixin, BaseLineTextEdit):
    pass


class ValidationError(Exception):
    pass


class ValidatedLineEditBase(QtWidgets.QLineEdit):
    """Abstract base class for validated Line edit widgets."""

    def __init__(self, *args, **kwargs):
        super(ValidatedLineEditBase, self).__init__(*args, **kwargs)
        self._tooltip = ''
        self._validation_tooltip = ''
        self._builder = None
        self._base_builder = None
        self.textChanged.connect(self._handleTextChanged)
        self._value = None
        self._valid = False
        self._keep_last_valid_value = True

    def setBuilder(self, builder):
        """
        Parameters
        ----------
        builder : Callable[[int], Any]
            Builder builds typed value from string line and performs
            validation. Can raise ValidationError to indicate invalid input.
        """
        self._builder = builder

    def setToolTip(self, tooltip):
        self._tooltip = tooltip
        self._update_tooltip()

    def toolTip(self):
        return self._tooltip

    def _update_tooltip(self):
        tooltip = "\n\n".join(
            filter(bool, [self._tooltip, self._validation_tooltip]))
        super().setToolTip(tooltip)

    def _build(self, text):
        value = self._base_builder(text)
        if self._builder is not None:
            value = self._builder(value)
        return value

    def _handleTextChanged(self, text):
        tooltip = ''
        valid = False
        try:
            value = self._build(text)
            if value != self._value:
                self._value = value
                self.valueChanged.emit(value)
            valid = True
        except ValidationError as v:
            if self._keep_last_valid_value:
                tooltip = f'Error: {v}\nValue: {self._value}'
            else:
                tooltip = f'Error: {v}'

        except Exception:
            pass
        self._validation_tooltip = tooltip
        self._update_tooltip()
        palette = self.palette()
        if valid:
            palette = QtGui.QPalette()
        else:
            if prim.is_osx():
                # Special-case handling for MacOS.
                # For some reason, changing the background color of LineEdits
                # does not work. See:
                # https://bugreports.qt.io/browse/QTBUG-73183
                # https://bugreports.qt.io/browse/QTBUG-72662
                # https://bugreports.qt.io/browse/QTBUG-72428
                palette.setColor(
                    self.foregroundRole(), colors.DANGER_TEXT_NORMAL_BG_COLOR)
            else:
                palette.setColor(
                    self.foregroundRole(), colors.DANGER_TEXT_COLOR)
                palette.setColor(self.backgroundRole(), colors.DANGER_BG_COLOR)

        self.setPalette(palette)
        self._valid = valid

    def value(self):
        """
        Returns
        -------
        Any
            The stored value. Converted by applying builders on the text.
            Not necessarily the same as what is currently shown in the text
            box.
        """
        return self._value

    def valid(self):
        return self._valid

    def set_keep_last_valid_value(self, enabled):
        self._keep_last_valid_value = enabled


class ValidatedIntLineEdit(ValidatedLineEditBase):
    """Signal valueChanged is emitted when the stored value is changed."""
    valueChanged = qt_compat2.Signal(int)

    def __init__(self, *args, **kwargs):
        super(ValidatedIntLineEdit, self).__init__(*args, **kwargs)
        self._base_builder = self._valid_int_builder

    def _valid_int_builder(self, text):
        try:
            return int(text)
        except Exception:
            raise ValidationError(
                '"{}" is not a valid int value.'.format(text))


class ValidatedFloatLineEdit(ValidatedLineEditBase):
    """Signal valueChanged is emitted when the stored value is changed."""
    valueChanged = qt_compat2.Signal(float)

    def __init__(self, *args, **kwargs):
        super(ValidatedFloatLineEdit, self).__init__(*args, **kwargs)
        self._base_builder = self._valid_float_builder

    def _valid_float_builder(self, text):
        try:
            return float(text)
        except Exception:
            raise ValidationError(
                '"{}" is not a valid floating point value.'.format(text))


class ValidatedTextLineEdit(ValidatedLineEditBase):
    """Signal valueChanged is emitted when the stored value is changed."""
    valueChanged = qt_compat2.Signal(str)

    def __init__(self, *args, **kwargs):
        super(ValidatedTextLineEdit, self).__init__(*args, **kwargs)
        self._base_builder = self._valid_text_builder

    def _valid_text_builder(self, text):
        try:
            return str(text)
        except Exception:
            raise ValidationError(
                '"{}" is not a valid text value.'.format(text))


class ValidatedSpinBoxBase(QtWidgets.QAbstractSpinBox):
    """Signal valueChanged is emitted when the stored value is changed."""

    def __init__(self, *args, **kwargs):
        super(ValidatedSpinBoxBase, self).__init__(*args, **kwargs)
        self._max = None
        self._min = None
        self._step = 1
        self._value = None

    def _init_line_validator(self):
        def bounded_validator(value):
            if self._max is not None and value > self._max:
                raise ValidationError(
                    '"{}" is greater than upper bound: "{}".'.format(
                        value, self._max))

            if self._min is not None and value < self._min:
                raise ValidationError(
                    '"{}" is smaller than lower bound: "{}".'.format(
                        value, self._min))
            return value

        self.lineEdit().setBuilder(bounded_validator)

    def setLineEdit(self, line_edit):
        super(ValidatedSpinBoxBase, self).setLineEdit(line_edit)
        line_edit.valueChanged.connect(self._handleValueChanged)
        self._init_line_validator()

    def setMaximum(self, value):
        self._max = value

    def setMinimum(self, value):
        self._min = value

    def setSingleStep(self, value):
        self._step = value

    def setValue(self, value):
        if self._max is not None and value > self._max:
            value = self._max
        if self._min is not None and value < self._min:
            value = self._min

        line_edit = self.lineEdit()
        line_edit.setText(str(value))

    def value(self):
        return self._value

    def stepEnabled(self):
        state = QtWidgets.QAbstractSpinBox.StepNone
        if self._value is not None:
            if self._max is None or self._value < self._max:
                state |= QtWidgets.QAbstractSpinBox.StepUpEnabled
            if self._min is None or self._value > self._min:
                state |= QtWidgets.QAbstractSpinBox.StepDownEnabled
        return state

    def stepBy(self, steps):
        self.setValue(self._value + steps * self._step)

    def _handleValueChanged(self, value):
        self._value = value
        self.valueChanged.emit(value)


class ValidatedFloatSpinBox(ValidatedSpinBoxBase):
    valueChanged = qt_compat2.Signal(float)

    def __init__(self, *args, **kwargs):
        super(ValidatedFloatSpinBox, self).__init__(*args, **kwargs)
        self._decimals = None
        line_edit = ValidatedFloatLineEdit(parent=self)
        super(ValidatedFloatSpinBox, self).setLineEdit(line_edit)

    def setValue(self, value):
        if self._decimals is not None:
            value = float(round(value, self._decimals))
        super(ValidatedFloatSpinBox, self).setValue(value)

    def setMaximum(self, value):
        if value is None:
            self._max = None
        else:
            self._max = float(value)

    def setMinimum(self, value):
        if value is None:
            self._min = None
        else:
            self._min = float(value)

    def setDecimals(self, value):
        self._decimals = value


class ValidatedIntSpinBox(ValidatedSpinBoxBase):
    valueChanged = qt_compat2.Signal(int)

    def __init__(self, *args, **kwargs):
        super(ValidatedIntSpinBox, self).__init__(*args, **kwargs)
        line_edit = ValidatedIntLineEdit(parent=self)
        super(ValidatedIntSpinBox, self).setLineEdit(line_edit)

    def setValue(self, value):
        super(ValidatedIntSpinBox, self).setValue(value)


class ValidatedComboBoxBase(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._max = None
        self._min = None
        self._value = None
        self.currentIndexChanged[int].connect(self._handleIndexChanged)
        self.setEditable(True)

    def _init_line_validator(self):
        def bounded_validator(value):
            if self._max is not None and value > self._max:
                raise ValidationError(
                    '"{}" is greater than upper bound: "{}".'.format(
                        value, self._max))

            if self._min is not None and value < self._min:
                raise ValidationError(
                    '"{}" is smaller than lower bound: "{}".'.format(
                        value, self._min))
            return value

        self.lineEdit().setBuilder(bounded_validator)

    def setLineEdit(self, line_edit):
        super().setLineEdit(line_edit)
        line_edit.valueChanged.connect(self._handleValueChanged)
        self._init_line_validator()

    def setMaximum(self, value):
        self._max = value

    def setMinimum(self, value):
        self._min = value

    def setValue(self, value):
        if self._max is not None and value > self._max:
            value = self._max
        if self._min is not None and value < self._min:
            value = self._min

        line_edit = self.lineEdit()
        line_edit.setText(str(value))

    def value(self):
        return self._value

    def _handleValueChanged(self, value):
        self._value = value
        self.valueChanged.emit(value)

    def _handleIndexChanged(self, index):
        line_edit = self.lineEdit()
        text = line_edit.text()
        line_edit.setText(text)


class ValidatedTextComboBox(ValidatedComboBoxBase):
    valueChanged = qt_compat2.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        line_edit = ValidatedTextLineEdit(parent=self)
        super().setLineEdit(line_edit)


class ValidatedFloatComboBox(ValidatedComboBoxBase):
    valueChanged = qt_compat2.Signal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._decimals = None
        line_edit = ValidatedFloatLineEdit(parent=self)
        super().setLineEdit(line_edit)

    def setValue(self, value):
        if self._decimals is not None:
            value = round(value, self._decimals)
        super().setValue(value)

    def setDecimals(self, value):
        self._decimals = value


class ValidatedIntComboBox(ValidatedComboBoxBase):
    valueChanged = qt_compat2.Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        line_edit = ValidatedIntLineEdit(parent=self)
        super().setLineEdit(line_edit)

    def setValue(self, value):
        super().setValue(value)


class NonEditableComboBox(QtWidgets.QComboBox):
    valueChanged = qt_compat2.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditable(False)
        self.currentIndexChanged[int].connect(self._handleIndexChanged)

    def value(self):
        return self.currentText()

    def _handleIndexChanged(self, index):
        self.valueChanged.emit(self.value())


class DateTimeWidget(QtWidgets.QDateTimeEdit):
    valueChanged = qt_compat2.Signal(datetime.datetime)
    datetime_format = "yyyy-MM-ddTHH:mm:ss"

    def __init__(self, value=None, datetime_format=None, parent=None):
        super().__init__(parent=parent)
        if datetime_format:
            self.datetime_format = datetime_format

        self.setDisplayFormat(self.datetime_format)
        self.setCalendarPopup(True)
        if value is not None:
            self.setValue(value)
        self.dateTimeChanged.connect(self._datetime_changed)

    def value(self):
        qdatetime = self.dateTime()
        return prim.parse_isoformat_datetime(
            qdatetime.toString(QtCore.Qt.ISODateWithMs))

    def setValue(self, value):
        qdatetime = QtCore.QDateTime.fromString(
            value.isoformat(), QtCore.Qt.ISODateWithMs)
        self.setDateTime(qdatetime)

    def _datetime_changed(self, value):
        value = prim.parse_isoformat_datetime(
            value.toString(QtCore.Qt.ISODateWithMs))
        self.valueChanged.emit(value)


# leave for debugging widgets
if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)

    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()

    test_widget = ToggleablePrefixLineEdit(placeholder='enter filename',
                                           prefix_states=('rel', 'abs'),
                                           parent=widget)
    # test_widget.textChanged.connect(lambda a: test_widget.set_state(a == ''))

    other_widget = ClearButtonLineEdit(parent=widget)

    normal_widget = QtWidgets.QLineEdit(widget)

    layout.addWidget(test_widget)
    layout.addWidget(other_widget)
    layout.addWidget(normal_widget)

    widget.setLayout(layout)
    widget.show()
    widget.raise_()

    # print(test_widget.rect().height())
    # print(other_widget.rect().height())
    # print(normal_widget.rect().height())

    sys.exit(application.exec_())


class UndoStack(QtCore.QObject):
    """
    A simple undo stack which saves a list of states and allows moving
    between those states.

    The signal state_changed is emitted every time the current state of the
    undo stack changes.
    """
    state_changed = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self._undo_stack = []
        self._undo_index = 0

        self._undo_action = QtWidgets.QAction(
            QtGui.QIcon(prim.get_icon_path('actions/edit-undo-symbolic.svg')),
            'Undo')
        self._undo_action.setShortcut(QtGui.QKeySequence.Undo)
        self._undo_action.setToolTip('Undo')
        self._undo_action.triggered.connect(self._undo)

        self._redo_action = QtWidgets.QAction(
            QtGui.QIcon(prim.get_icon_path('actions/edit-redo-symbolic.svg')),
            'Redo')
        self._redo_action.setShortcut(QtGui.QKeySequence.Redo)
        self._redo_action.setToolTip('Redo')
        self._redo_action.triggered.connect(self._redo)

    @property
    def undo_action(self):
        """
        Return a QAction for undo which can be used in menus and toolbars.

        The QAction is automatically enabled/disabled as needed.
        """
        return self._undo_action

    @property
    def redo_action(self):
        """
        Return a QAction for redo which can be used in menus and toolbars.

        The QAction is automatically enabled/disabled as needed.
        """
        return self._redo_action

    def add_undo_state(self, new_state):
        """
        Store a new state on the undo stack.

        If the new state is equal to the current state, the new state is
        ignored and the undo stack isn't modified. Otherwise any states ahead
        of the current state are discarded and new_state becomes the new
        current state.

        This method does not emit state_changed. The reasoning behind this is
        that this method is usually called after the model has already been
        updated, so we don't want to trigger another update of the model.

        Returns True if the new state was added and False otherwise.
        """
        if not isinstance(new_state, str):
            raise TypeError(f"Undo state must be str not {type(new_state)}")
        if (not len(self._undo_stack)
                or new_state != self._undo_stack[self._undo_index]):
            self._undo_stack = self._undo_stack[:self._undo_index + 1]
            self._undo_stack.append(new_state)
            self._undo_index = len(self._undo_stack) - 1
            self._update_enabled_undo_redo_actions()
            return True
        return False

    def _undo(self):
        """Move the undo stack pointer back one step."""
        if self.can_undo():
            self._undo_index -= 1
            self._update_enabled_undo_redo_actions()
            self.state_changed.emit(self._undo_stack[self._undo_index])

    def _redo(self):
        """Move the undo stack pointer forward one step."""
        if self.can_redo():
            self._undo_index += 1
            self._update_enabled_undo_redo_actions()
            self.state_changed.emit(self._undo_stack[self._undo_index])

    def can_undo(self):
        """Return True if is currently possible to undo."""
        return self._undo_index > 0

    def can_redo(self):
        """Return True if is currently possible to redo."""
        return self._undo_index + 1 < len(self._undo_stack)

    def _update_enabled_undo_redo_actions(self):
        """Set the appropriate enabled state for the undo/redo buttons."""
        self._undo_action.setEnabled(self.can_undo())
        self._redo_action.setEnabled(self.can_redo())


class HLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(self.HLine)
        self.setFrameShadow(self.Sunken)


class VLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(self.VLine)
        self.setFrameShadow(self.Sunken)


class FormLayout(QtWidgets.QFormLayout):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Override the default platform depended sizing and alignment rules,
        # to get a Sympathy specific layout
        self.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)


class ReadOnlyLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setReadOnly(True)
        palette = self.palette()
        palette.setColor(
            self.foregroundRole(), palette.color(
                palette.Disabled, self.foregroundRole()))
        self.setPalette(palette)
        self.setFocusPolicy(QtCore.Qt.NoFocus)


class ClickableHtmlLabel(QtWidgets.QLabel):
    """
    HTML label with clickable links with can be handled.
    Connect linkActivated(string) to handle clicks.
    WordWrap is enabled by default.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTextFormat(QtCore.Qt.RichText)
        self.setWordWrap(True)
        self.setOpenExternalLinks(False)
