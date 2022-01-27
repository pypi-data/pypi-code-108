# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
import mistune
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

from sympathy.app.flowview import grid
from .types import MovableElementViewInterface
from .types import get_label
from .. import user_commands
from .. common import FRONT, FORWARD, BACKWARD, BACK
from .. import themes
from .. import actions
import sympathy.app.library_manager
import sympathy.app.settings


_ORDER = [FRONT, FORWARD, BACKWARD, BACK]


_RAD = 8  # Border radius for rounded corners
_OL = 5   # Outline width
_HW = 15  # Border handle width
_TW = 5   # Text offset


class TextView(QtWidgets.QGraphicsTextItem):
    def __init__(self, parent=None):
        super(TextView, self).__init__(parent)
        self._rect = QtCore.QRectF(0, 0, 0, 0)
        self._bounding_rect = self._rect

        self.setZValue(0)
        self.document().contentsChanged.connect(self._handle_contents_changed)

    def boundingRect(self):
        return self._bounding_rect

    @QtCore.Slot()
    def _handle_contents_changed(self):
        self.setTextWidth(-1)
        self.setTextWidth(self._bounding_rect.width())
        size = self._rect.size()
        size.setWidth(size.width() - _TW)
        self.document().setPageSize(size)

    def hoverMoveEvent(self, event):
        # Tell parent that the mouse entered the TextView. Otherwise it may
        # miss this motion.
        self.parentItem().hoverMoveEventOffset(
            event, QtCore.QPointF(_RAD, _RAD))

    @property
    def rect(self):
        """Get/Set the text container rectangle (QtCore.QRectF)."""
        return self._rect

    @rect.setter
    def rect(self, value):
        self.prepareGeometryChange()
        self._rect = value.adjusted(_OL, _OL, -_OL, -_OL)
        self.document().setPageSize(self._rect.size())
        self._bounding_rect = QtCore.QRectF(
            0, 0, self._rect.width(), self._rect.height())


class TextEditor(QtWidgets.QGraphicsTextItem):
    finished_editing = QtCore.Signal(str)

    def __init__(self, text, parent):
        super(TextEditor, self).__init__(parent)
        self._text_view = parent
        self._menu = actions.document_text_edit_menu(self)
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setZValue(100)
        self.setPos(_RAD, _RAD)
        self.document().contentsChanged.connect(self._handle_contents_changed)
        self.setPlainText(text)

    @QtCore.Slot()
    def _handle_contents_changed(self):
        self.setTextWidth(-1)
        self.setTextWidth(self.parentItem().boundingRect().width() - 2 * _RAD)

    def _end_editing(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.finished_editing.emit(self.toPlainText())

    def focusInEvent(self, event):
        self._text_view.setZValue(999)
        super(TextEditor, self).focusOutEvent(event)

    def focusOutEvent(self, event):
        self._text_view.setZValue(0)
        why = event.reason()
        if why == QtCore.Qt.PopupFocusReason:
            event.ignore()
        elif (why != QtCore.Qt.ActiveWindowFocusReason and
                why != QtCore.Qt.OtherFocusReason):
            self._end_editing()
            event.accept()
        super(TextEditor, self).focusOutEvent(event)

    def paint(self, painter, o, w):
        painter.fillRect(self.boundingRect(), QtGui.QColor(255, 255, 255, 200))
        super(TextEditor, self).paint(painter, o, w)

    def keyPressEvent(self, event):
        if ((event.key() == QtCore.Qt.Key_Return or
                event.key() == QtCore.Qt.Key_Enter) and not
                event.modifiers() & QtCore.Qt.ShiftModifier):
            self._end_editing()
            event.accept()
        else:
            super(TextEditor, self).keyPressEvent(event)

    def hoverLeaveEvent(self, event):
        self._set_cursor()

    def hoverMoveEvent(self, event):
        self._set_cursor(QtCore.Qt.IBeamCursor)

    def _set_cursor(self, cursor=None):
        self.scene().flow_view().set_item_cursor(cursor)

    def contextMenuEvent(self, event):
        event.accept()
        self._menu.setup()
        self._menu.exec_(event.screenPos())


class TextFieldView(MovableElementViewInterface):
    resizing_started = QtCore.Signal()
    resizing_ended = QtCore.Signal()
    create_subflow_from_selection_requested = QtCore.Signal()
    request_reorder = QtCore.Signal(str)

    MIN_WIDTH = 100
    MIN_HEIGHT = 50

    def __init__(self, model, parent=None):
        self._textview = None
        self._editor = None
        super(TextFieldView, self).__init__(model, parent=parent)
        self.setCacheMode(QtWidgets.QGraphicsItem.NoCache)
        self.__init()

    def __init(self):
        self._resize_pos_none = 0
        self._resize_pos_top = 1
        self._resize_pos_bottom = 2
        self._resize_pos_right = 4
        self._resize_pos_left = 8
        self._resize_pos_top_left = (
            self._resize_pos_top | self._resize_pos_left)
        self._resize_pos_top_right = (
            self._resize_pos_top | self._resize_pos_right)
        self._resize_pos_bottom_left = (
            self._resize_pos_bottom | self._resize_pos_left)
        self._resize_pos_bottom_right = (
            self._resize_pos_bottom | self._resize_pos_right)
        self._cursors = {
            self._resize_pos_none: None,  # default cursor
            self._resize_pos_top: QtCore.Qt.SizeVerCursor,
            self._resize_pos_bottom: QtCore.Qt.SizeVerCursor,
            self._resize_pos_left: QtCore.Qt.SizeHorCursor,
            self._resize_pos_right: QtCore.Qt.SizeHorCursor,
            self._resize_pos_top_left: QtCore.Qt.SizeFDiagCursor,
            self._resize_pos_bottom_right: QtCore.Qt.SizeFDiagCursor,
            self._resize_pos_top_right: QtCore.Qt.SizeBDiagCursor,
            self._resize_pos_bottom_left: QtCore.Qt.SizeBDiagCursor}

        self._resize_edge = self._resize_pos_none
        self.setAcceptHoverEvents(True)

        self._undo_stack = self._model.flow.undo_stack()

        self._textview = TextView(self)
        self._textview.setPos(_RAD, _RAD)
        self._textview.rect = self.rect()

        self._border_width = _OL

        self._background_brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        self._border_pen = QtGui.QPen()
        self._border_pen.setWidth(self._border_width)

        self._init_resize_state_machine()
        self._init_context_menu()
        self.set_text(self._model.text())
        self.set_color(self._model.color())
        self.set_order()
        self._update_painter()

        self._signals.connect(
            self._model,
            self._model.size_changed[QtCore.QSizeF], self.set_size)
        self._signals.connect(
            self._model,
            self._model.text_changed[str], self.set_text)
        self._signals.connect(
            self._model,
            self._model.color_changed[str], self.set_color)
        self._signals.connect(
            self._model,
            self._model.order_changed, self.set_order)

    def _init_resize_state_machine(self):
        self._resize_state_machine = QtCore.QStateMachine()
        self._state_resizing = QtCore.QState(self._resize_state_machine)
        self._state_normal = QtCore.QState(self._resize_state_machine)

        self._state_normal.addTransition(
            self.resizing_started, self._state_resizing)
        self._state_resizing.addTransition(
            self.resizing_ended, self._state_normal)
        self._resize_state_machine.setInitialState(self._state_normal)
        self._resize_state_machine.start()

        self._state_resizing.entered.connect(self._handle_start_resize)
        self._state_resizing.exited.connect(self._handle_end_resize)

    def _init_context_menu(self):
        self._edit_action = QtWidgets.QAction("Edit", self)
        self._edit_action.triggered.connect(self._edit_requested)

        self._menu = QtWidgets.QMenu()
        self._menu.addAction(self._edit_action)
        self._menu.addSeparator()
        self._menu.addAction(self._copy_action)
        self._menu.addAction(self._cut_action)
        self._menu.addAction(self._delete_action)
        self._menu.addSeparator()

        color_menu = QtWidgets.QMenu('Color')
        self._color_actions = {}
        theme = themes.get_active_theme()
        for color in theme.text_field_colors():
            action = ColorAction(color, self)
            action.triggered.connect(self._handle_color_changed)
            action.setCheckable(True)
            color_menu.addAction(action)
            self._color_actions[color] = action
            if color == self._model.color():
                action.setChecked(True)

        self._menu.addMenu(color_menu)

        order_menu = QtWidgets.QMenu('Z-order')
        for order in _ORDER:
            action = QtWidgets.QAction(order, self)
            action.triggered.connect(self._handle_order_changed)
            order_menu.addAction(action)
        self._menu.addMenu(order_menu)
        examples_action = QtWidgets.QAction('Insert Examples', self)
        examples_action.triggered.connect(self._select_example_nodes_requested)
        if sympathy.app.settings.instance()['Gui/experimental']:
            self._menu.addAction(examples_action)

        self._menu.addSeparator()
        advanced_menu = self._menu.addMenu('Advanced')
        advanced_menu.addAction(self._show_info_action)

    def _update_painter(self):
        r = self._bounding_rect.adjusted(
            self._border_width, self._border_width, -self._border_width,
            -self._border_width)

        self._outline.clear()
        self._outline.addRoundedRect(r, _RAD, _RAD)
        self._background_path = QtGui.QPainterPath()
        self._background_path.addRoundedRect(r, _RAD, _RAD)

    def text(self):
        return self._textview.toPlainText()

    @QtCore.Slot(str)
    def set_text(self, value):
        try:
            lines = []
            for line in value.splitlines():
                ids = sympathy.app.library_manager.DocsBuilder.node_example_re.findall(
                    line)
                for node_id in ids:
                    try:
                        node_name = self._model.flow.app_core.library_node(
                            node_id).name
                        if node_name:
                            line = line.replace(node_id, node_name)
                    except Exception:
                        pass
                lines.append(line)
            self._textview.setHtml(mistune.markdown('\n'.join(lines)))
        except Exception:
            self._textview.setPlainText(value)

    @QtCore.Slot(str)
    def set_color(self, color):
        theme = themes.get_active_theme()
        colors = theme.text_field_colors()
        if color not in colors:
            color = list(colors.keys())[0]

        for action in self._color_actions:
            self._color_actions[action].setChecked(False)
        self._color_actions[color].setChecked(True)
        color = colors[color]
        self._background_brush.setColor(color)
        self._border_pen.setColor(color.darker(120))
        self.update()

    def size(self):
        return self._bounding_rect.size()

    @QtCore.Slot(QtCore.QSizeF)
    def set_size(self, size):
        if self._textview:
            rect = QtCore.QRectF(self.position(), size)
            self._textview.rect = rect
        if size.width() < self.MIN_WIDTH:
            size.setWidth(self.MIN_WIDTH)
        if size.height() < self.MIN_HEIGHT:
            size.setHeight(self.MIN_HEIGHT)
        self._set_bounding_rect(
            QtCore.QRectF(0, 0, size.width(), size.height()))
        self._update_painter()
        self.update()

    def rect(self):
        return QtCore.QRectF(self.position(), self.size())

    def set_rect(self, rect):
        self.set_position(rect.topLeft())
        self.set_size(rect.size())

    @QtCore.Slot()
    def set_order(self):
        self.setZValue(self._model.order())

    @QtCore.Slot(QtCore.QPointF)
    def set_position(self, pos):
        super(TextFieldView, self).set_position(pos)
        if self._textview:
            rect = QtCore.QRectF(pos, self.size())
            self._textview.rect = rect

    @QtCore.Slot(str)
    def handle_text_changed(self, text):
        if text != self._model.text():
            cmd = user_commands.EditTextFieldCommand(
                self._model, self._model.text(), text)
            self._undo_stack.push(cmd)
        self.set_order()

        if self._editor:
            self._editor.deleteLater()
            self._editor = None
            self._textview.show()

    def _edit_requested(self):
        if self._editor:
            return

        self._editor = TextEditor(self._model.text(), self)
        self._textview.hide()
        self._editor.finished_editing.connect(self.handle_text_changed)
        self._editor.setFocus()

    @QtCore.Slot()
    def _handle_start_resize(self):
        self._old_rect = self.rect()

    @QtCore.Slot()
    def _handle_end_resize(self):
        cmd = user_commands.ResizeElementCommand(
            self._model, self._old_rect, self.rect())
        self._undo_stack.push(cmd)

    @QtCore.Slot()
    def _show_info_requested(self):
        info = QtWidgets.QDialog()
        info.setWindowTitle("Text Field Information")
        self._main_layout = QtWidgets.QVBoxLayout()
        self._layout = QtWidgets.QFormLayout()
        self._layout.addRow('UUID', get_label(self._model.uuid))
        self._layout.addRow('Text', get_label(self._model.text()))

        self._main_layout.addLayout(self._layout)
        self._button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok)
        self._button_box.accepted.connect(info.accept)
        self._main_layout.addWidget(self._button_box)
        info.setLayout(self._main_layout)
        info.exec_()

    def _select_example_nodes_requested(self):
        # TODO(erik): Create non-experimental interface.  Might not belong in
        # text-field at all. At least this is a self contained function which
        # should be easy to move.

        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Select example nodes for this flow")
        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QListWidget()

        buttons = QtWidgets.QDialogButtonBox()
        buttons.addButton(QtWidgets.QDialogButtonBox.Ok)
        buttons.addButton(QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        root = self._model.flow.root_flow()
        if root is None:
            return

        node_ids = set()
        library_nodes = set()
        for node in root.all_nodes(atom=False):
            if node.identifier not in node_ids:
                node_ids.add(node.identifier)
                library_nodes.add(node.library_node)

        widget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)

        for node in sorted(library_nodes, key=lambda x: x.name):
            item = QtWidgets.QListWidgetItem(node.name)
            item.setData(QtCore.Qt.UserRole, node)
            widget.addItem(item)

        layout.addWidget(widget)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        texts = []
        if dialog.exec_():
            for item in widget.selectedItems():
                library_node = item.data(QtCore.Qt.UserRole)
                texts.append('- {}'.format(
                    sympathy.app.library_manager.DocsBuilder.format_node_example(
                        library_node.node_identifier)))
            text = self._model.text()
            texts.insert(0, text)
            cmd = user_commands.EditTextFieldCommand(
                self._model, self._model.text(), '\n'.join(texts))
            self._undo_stack.push(cmd)

    # @QtCore.Slot()
    # Weird PyQt issue where the sender is always None if the slot decorator
    # is used, more info:
    # https://riverbankcomputing.com/pipermail/pyqt/2001-May/001088.html
    def _handle_color_changed(self):
        for action in self._color_actions:
            self._color_actions[action].setChecked(False)
        color = self.sender().color()
        if color != self._model.color():
            cmd = user_commands.EditTextFieldColorCommand(
                self._model, self._model.color(), color)
            self._undo_stack.push(cmd)
            self.sender().setChecked(True)

    # @QtCore.Slot()
    def _handle_order_changed(self):
        self.request_reorder.emit(self.sender().text())

    def paint(self, painter, option, widget):
        painter.fillPath(self._background_path, self._background_brush)
        painter.setPen(self._border_pen)
        painter.drawPath(self._outline)

    def mousePressEvent(self, event):
        if self._resize_edge != self._resize_pos_none:
            self._start_pos = event.pos()
            self.resizing_started.emit()
            return True
        super(TextFieldView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(TextFieldView, self).mouseReleaseEvent(event)
        self.resizing_ended.emit()

    def mouseDoubleClickEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            event.ignore()
            return

        self._edit_requested()
        super(TextFieldView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._state_resizing in self._resize_state_machine.configuration():
            r = QtCore.QRectF(self.rect())
            grid_pos = grid.instance().snap_to_grid(event.scenePos())
            if self._resize_edge in [self._resize_pos_top,
                                     self._resize_pos_top_left,
                                     self._resize_pos_top_right]:
                y = grid_pos.y()
                if r.bottom() - y < self.MIN_HEIGHT:
                    r.setTop(r.bottom() - self.MIN_HEIGHT)
                else:
                    r.setTop(y)
            elif self._resize_edge in [self._resize_pos_bottom,
                                       self._resize_pos_bottom_left,
                                       self._resize_pos_bottom_right]:
                y = grid_pos.y()
                if y - r.top() < self.MIN_HEIGHT:
                    r.setBottom(r.top() + self.MIN_HEIGHT)
                else:
                    r.setBottom(y)
            if self._resize_edge in [self._resize_pos_left,
                                     self._resize_pos_top_left,
                                     self._resize_pos_bottom_left]:
                x = grid_pos.x()
                if r.right() - x < self.MIN_WIDTH:
                    r.setLeft(r.right() - self.MIN_WIDTH)
                else:
                    r.setLeft(x)
            elif self._resize_edge in [self._resize_pos_right,
                                       self._resize_pos_top_right,
                                       self._resize_pos_bottom_right]:
                x = grid_pos.x()
                if x - r.left() < self.MIN_WIDTH:
                    r.setRight(r.left() + self.MIN_WIDTH)
                else:
                    r.setRight(x)

            self.set_rect(r)
        else:
            super(TextFieldView, self).mouseMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.set_cursor(None)
        self.resizing_ended.emit()
        super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event):
        self.hoverMoveEventOffset(event)

    def hoverMoveEventOffset(self, event, offset=None):
        pos = event.pos()
        if offset is not None:
            pos += offset

        inner_area = self._bounding_rect.adjusted(_HW, _HW, -_HW, -_HW)
        if self._bounding_rect.contains(pos):
            if inner_area.contains(pos):
                self._resize_edge = self._resize_pos_none
            else:
                edge = 0
                if pos.y() - self._bounding_rect.top() <= _HW:
                    edge = 1
                if self._bounding_rect.bottom() - pos.y() <= _HW:
                    edge += 2
                if self._bounding_rect.right() - pos.x() <= _HW:
                    edge += 4
                if pos.x() - self._bounding_rect.left() <= _HW:
                    edge += 8
                self._resize_edge = edge
        else:
            self._resize_edge = self._resize_pos_none

        self.set_cursor(self._cursors[self._resize_edge])
        super().hoverMoveEvent(event)

    def itemChange(self, change, value):
        # Disable snap-to-grid while resizing cause it was acting up.
        if (change == QtWidgets.QGraphicsItem.ItemPositionChange and
                self._state_resizing in
                self._resize_state_machine.configuration()):
            return value
        return super(TextFieldView, self).itemChange(change, value)

    def contextMenuEvent(self, event):
        self._menu.exec_(event.screenPos())

    def remove(self):
        super().remove()


class ColorAction(QtWidgets.QAction):
    def __init__(self, color, parent=None):
        col = QtGui.QPixmap(30, 20)
        theme = themes.get_active_theme()
        col.fill(theme.text_field_colors()[color])
        super(ColorAction, self).__init__(QtGui.QIcon(col), color, parent)
        self._color = color

    def color(self):
        return self._color
