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
import os
import html
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets
import Qt.QtSvg as QtSvg

from .types import (HighlightableElementViewInterface, get_label,
                    ScaleAnimationHoverHighlighter)
from . decoration import NodeStatusIconView, Status
from .. import themes
from .. import flow
from .. import user_commands
from .. import settings
from sympathy.utils import uuid_generator
from sympathy.platform import os_support as oss


class Info(QtWidgets.QDialog):

    def __init__(self, flowio_model, parent=None, flags=QtCore.Qt.Widget):
        super(Info, self).__init__(parent, flags)
        self._model = flowio_model
        self._init()

    def _init(self):
        def pre(x):
            return '<pre>{}</pre>'.format(html.escape(x))

        self.setWindowTitle(u'Information: {}'.format(self._model.name))
        self._main_layout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        layout.addRow('Name', get_label(self._model.name))
        namespace_uuid, item_uuid = uuid_generator.split_uuid(
            self._model.full_uuid)
        layout.addRow('Type', get_label(self._model.datatype.html))
        layout.addRow('Scheme', get_label(self._model.scheme))
        layout.addRow('Description', get_label(self._model.description))
        layout.addRow('Filename', get_label(
            os.path.basename(self._model.filename)))

        if settings.instance()['Gui/platform_developer']:
            layout.addRow('Namespace UUID', get_label(pre(namespace_uuid)))
            layout.addRow('Port UUID', get_label(pre(item_uuid)))
            layout.addRow('Is connected', get_label(
                str(self._model.is_connected_to_node())))

        self._main_layout.addLayout(layout)
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        self._main_layout.addWidget(button_box)
        self.setLayout(self._main_layout)


class PortView(HighlightableElementViewInterface, QtWidgets.QGraphicsObject):
    """An input or output port"""

    connection_start_requested = QtCore.Signal(object)
    connection_end_requested = QtCore.Signal(object)
    position_changed = QtCore.Signal(QtCore.QPointF)
    open_add_context_requested = QtCore.Signal(
        QtWidgets.QGraphicsSceneMouseEvent)

    hover_highlighter_cls = ScaleAnimationHoverHighlighter

    def __init__(self, *args, **kwargs):
        super(PortView, self).__init__(*args, **kwargs)
        size = self._model.size
        self._bounding_rect = QtCore.QRectF(0, 0, size.width(), size.height())
        self._port_symbol = None
        self.renderer = QtSvg.QSvgRenderer(parent=self)
        self._init()
        self._init_actions()
        self._init_signalling()
        self._init_context_menu()
        self._init_highlighter()

    def _init(self):
        theme = themes.get_active_theme()
        self.set_position(self._model.position)
        self.setTransformOriginPoint(self.boundingRect().center())

        self._port_viewer_icon = NodeStatusIconView(parent=self)
        self._update_port_viewer_icon_position()
        self._port_viewer_icon.setScale(0.14)
        self._port_viewer_icon.setZValue(3)
        self.set_port_viewer_icon(self._model.port_viewer_open)

        self._outline = QtGui.QPainterPath()
        self._outline.addEllipse(self.boundingRect())
        self._node_color = theme.object_color
        self._border_color = theme.border_color
        self._border_width = 1.0
        self._brush = QtGui.QBrush(self._node_color)
        self._pen = QtGui.QPen(self._border_color, self._border_width)
        self._set_port_type(self._model.datatype)
        # Make sure that all signals have done what they should
        # before trying to build the tooltip.
        QtCore.QTimer.singleShot(0, self._update_tool_tip)

    def _delete(self):
        if self._model.node.type == flow.Type.Flow and self._model.mirror_port:
            if self._model.type == flow.Type.InputPort:
                cmd = user_commands.DeleteFlowInputPortCommand(self._model)
            elif self._model.type == flow.Type.OutputPort:
                cmd = user_commands.DeleteFlowOutputPortCommand(self._model)
            else:
                assert False, 'Unknown port type of: {}.'.format(self._model)
        else:
            if self._model.type == flow.Type.InputPort:
                cmd = user_commands.DeleteInputPortCommand(self._model)
            elif self._model.type == flow.Type.OutputPort:
                cmd = user_commands.DeleteOutputPortCommand(self._model)
            else:
                assert False, 'Unknown port type of: {}.'.format(self._model)
        self._model.node.flow.undo_stack().push(cmd)

    def _create(self):
        if self._model.type == flow.Type.InputPort:
            cmd = user_commands.DuplicateInputPortCommand(self._model)
        elif self._model.type == flow.Type.OutputPort:
            cmd = user_commands.DuplicateOutputPortCommand(self._model)
        else:
            assert False, 'Unknown port type of: {}.'.format(self._model)
        self._model.flow.undo_stack().push(cmd)

    def _init_actions(self):
        self._show_port_viewer_action = QtWidgets.QAction(
            'Open in Viewer', self)
        self._show_port_viewer_action.triggered.connect(
            self._show_port_viewer)
        self._copy_file_to_clipboard_action = QtWidgets.QAction(
            'Copy File Path To Clipboard', self)
        self._copy_file_to_clipboard_action.triggered.connect(
            self._copy_file_to_clipboard)

        self._show_info_action = QtWidgets.QAction('Properties', self)
        self._open_file_path_action = QtWidgets.QAction('Open File Path', self)
        self._open_file_path_action.triggered.connect(self._open_file_path)

        self._create_port_action = QtWidgets.QAction('Create', self)
        self._delete_port_action = QtWidgets.QAction('Remove', self)
        self._create_port_action.triggered.connect(self._create)
        self._delete_port_action.triggered.connect(self._delete)
        self._show_info_action.triggered.connect(self._show_info_requested)

    def _init_context_menu(self):
        self._context_menu = QtWidgets.QMenu()
        self._context_menu.addAction(self._show_port_viewer_action)
        self._context_menu.addSeparator()
        self._context_menu.addAction(self._create_port_action)
        self._context_menu.addAction(self._delete_port_action)
        self._context_menu.addSeparator()
        advanced_menu = self._context_menu.addMenu('Advanced')
        advanced_menu.addAction(self._copy_file_to_clipboard_action)
        advanced_menu.addAction(self._open_file_path_action)
        advanced_menu.addSeparator()
        advanced_menu.addAction(self._show_info_action)

    def _set_port_type(self, datatype):
        if self._port_symbol is not None and self.scene() is not None:
            self.scene().removeItem(self._port_symbol)
            self._port_symbol.deleteLater()
        self.prepareGeometryChange()
        self.renderer.load(QtCore.QByteArray(datatype.icon))
        self._port_symbol = QtSvg.QGraphicsSvgItem(self)
        self._port_symbol.setSharedRenderer(self.renderer)

        s = self._model.size
        r = self._port_symbol.boundingRect()
        scale = s.height() / r.height()

        if self.model.type == flow.Type.InputPort:
            self._bounding_rect.setX(- r.width() * scale + s.width())
            self._bounding_rect.setWidth(r.width() * scale)
        else:
            self._bounding_rect.setWidth(r.width() * scale)

        self._port_symbol.setScale(scale)
        if self.model.type == flow.Type.InputPort:
            self._port_symbol.setX(- r.width() * scale + s.width())
        self._update_port_viewer_icon_position()

    def _init_signalling(self):

        self._signals.connect(
            self._model,
            self._model.position_changed[QtCore.QPointF],
            self.set_position)

        self._signals.connect(
            self._model,
            self._model.datatype_changed,
            self._handle_datatype_changed)

        self._signals.connect(
            self._model,
            self._model.description_changed,
            self._update_tool_tip)

        self._signals.connect(
            self._model,
            self._model.viewer_changed,
            self._handle_viewer_changed)

    def boundingRect(self):
        return self._bounding_rect

    def paint(self, painter, options, widget=None):
        pass

    def set_port_viewer_icon(self, state):
        if state:
            self._port_viewer_icon.set_icon_type(Status.viewing)
        else:
            self._port_viewer_icon.set_icon_type(Status.none)
        self.update()

    def set_this_z(self):
        self.setZValue(6)

    def set_other_z(self):
        self.setZValue(5)

    def reset_z(self):
        self.setZValue(3)

    def _update_port_viewer_icon_position(self):
        self._port_viewer_icon.setPos(self._bounding_rect.left(),
                                      self._bounding_rect.top() - 8)

    @QtCore.Slot()
    def _show_port_viewer(self):
        port = self._model
        if port.type == flow.Type.OutputPort:
            try:
                port.node.port_viewer(port)
            except AttributeError:
                pass

    @QtCore.Slot()
    def _show_info_requested(self):
        dialog = Info(self._model)
        dialog.exec_()

    @QtCore.Slot()
    def _handle_datatype_changed(self):
        self._set_port_type(self._model.datatype)
        self._update_tool_tip()
        self.notify_position_changed()

    @QtCore.Slot(bool)
    def _handle_viewer_changed(self, state):
        self.set_port_viewer_icon(state)

    @QtCore.Slot()
    def _copy_file_to_clipboard(self):
        self._mime_data = QtCore.QMimeData()
        self._mime_data.setText(self._model.filename)
        QtWidgets.QApplication.clipboard().setMimeData(self._mime_data)

    @QtCore.Slot()
    def _open_file_path(self):
        oss.open_directory(os.path.dirname(self._model.filename))

    @QtCore.Slot(QtCore.QPointF)
    def set_position(self, position):
        self.setPos(position)
        self.notify_position_changed()

    def connection_position(self):
        offset = (2 if self._hover_highlighter
                       and not self._hover_highlighter.highlighted else 4.5)
        r = self.sceneBoundingRect()
        w = self.renderer.viewBox().width() * 0.625 + offset
        x = (r.left() + w if self.model.type == flow.Type.OutputPort
             else r.right() - w)
        p = r.center()
        p.setX(x)
        return p

    def notify_position_changed(self):
        self.position_changed.emit(self.connection_position())

    @QtCore.Slot()
    def _update_tool_tip(self):
        self.setToolTip('<b>%s</b><br/><i>%s</i><br/>' % (
            self._model.description, self._model.datatype.html))

    def mouseMoveEvent(self, event):
        if not self.scene() and not self.scene().parent():
            return super(PortView, self).mouseMoveEvent(event)

        flowview = self.scene().parent()
        transient_connection = flowview._transient_connection
        if transient_connection:
            port_view = None
            valid_port = False
            item = self.scene().itemAt(event.scenePos(), QtGui.QTransform())
            if item is not None and isinstance(item.parentItem(), PortView):
                port_view = item.parentItem()
                valid_port = self._model.flow.connection_is_allowed(
                    *flow.connection_direction(self._model, port_view.model))
            transient_connection.set_valid_connection(
                valid_port, port=port_view)
        super(PortView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            self._set_cursor()
            event.ignore()
            return
        if (self.model.type == flow.Type.InputPort and
                self.model.is_connected_to_node()):
            # Do nothing
            event.accept()
            return
        event.accept()
        self._set_cursor(QtCore.Qt.CrossCursor)
        self.connection_start_requested.emit(self)

    def mouseReleaseEvent(self, event):
        self._set_cursor()
        port_view = self.scene().itemAt(event.scenePos(), QtGui.QTransform())
        if ((port_view is None or
             not isinstance(port_view.parentItem(), PortView))):
            event.accept()
            self.open_add_context_requested.emit(event)
        elif not port_view:
            self.connection_end_requested.emit(None)
            event.ignore()
        else:
            if isinstance(port_view.parentItem(), PortView):
                port_view = port_view.parentItem()
            if (isinstance(port_view, PortView) and
                    self._model.flow.connection_is_allowed(
                        *flow.connection_direction(
                            self._model, port_view.model))):

                self.connection_end_requested.emit(port_view)
                event.accept()
            else:
                self.connection_end_requested.emit(None)
                event.ignore()

    def _set_cursor(self, cursor=None):
        self.scene().flow_view().set_item_cursor(cursor)

    def mouseDoubleClickEvent(self, event):
        self._show_port_viewer()

    def contextMenuEvent(self, event):
        self._create_port_action.setEnabled(self._model.can_create())
        self._delete_port_action.setEnabled(self._model.can_delete())
        self._show_port_viewer_action.setEnabled(
            self._model.type == flow.Type.OutputPort)
        self._context_menu.exec_(event.screenPos())

    def highlight(self, active):
        if self._hover_highlighter is not None:
            self._hover_highlighter.highlighted = active
