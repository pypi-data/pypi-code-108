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
import collections
import html
import itertools
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

from .types import MovableElementViewInterface
from .decoration import NodeViewLabel
from .port import PortView
from .. import user_commands
from .. import flow
from .. import themes
from .. import settings
from .types import get_label
from sympathy.utils import uuid_generator, log

core_logger = log.get_logger('core')


class FlowIOInfo(QtWidgets.QDialog):

    def __init__(self, flowio_model, parent=None, flags=QtCore.Qt.Widget):
        super(FlowIOInfo, self).__init__(parent, flags)
        self._model = flowio_model
        self._properties = self._model.get_properties()

        def pre(x):
            return '<pre>{}</pre>'.format(html.escape(x))

        self.setWindowTitle(u'Information: {}'.format(self._model.name))
        self._main_layout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)

        self._label_edit = QtWidgets.QLineEdit(self._model.name)
        self._optional_edit = QtWidgets.QCheckBox()
        self._default_edit = QtWidgets.QCheckBox()

        editable_optional = self._model.can_set_optional()

        self._default_edit.setEnabled(
            self._model.is_optional() and self._model.can_set_default())
        self._default_edit.setChecked(self._model.default or False)

        self._optional_edit.setEnabled(editable_optional)
        self._optional_edit.stateChanged.connect(self._set_optional_state)
        self._optional_edit.setChecked(self._model.is_optional())

        layout.addRow('Label', self._label_edit)
        layout.addRow('Optional', self._optional_edit)
        layout.addRow('Default', self._default_edit)
        namespace_uuid, item_uuid = uuid_generator.split_uuid(
            self._model.full_uuid)

        if self._model.parent_port is None:
            pp_is_connected = str(False)
            pp_uuid = 'N/A'
        else:
            pp_is_connected = str(
                self._model.parent_port.is_connected_to_node())
            pp_uuid = pre(self._model.parent_port.uuid)

        if settings.instance()['Gui/platform_developer']:
            layout.addRow('Namespace UUID', get_label(pre(namespace_uuid)))
            layout.addRow('Flow UUID', get_label(pre(item_uuid)))
            layout.addRow('Is connected', get_label(
                str(self._model.port.is_connected_to_node())))
            layout.addRow('Parent port is connected',
                          get_label(pp_is_connected))
            layout.addRow('Port UUID', get_label(pre(self._model.port_uuid)))
            layout.addRow('Parent port UUID', get_label(pp_uuid))

        self._main_layout.addLayout(layout)
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        self._main_layout.addWidget(button_box)
        self.setLayout(self._main_layout)

    def _set_optional_state(self, value):
        enabled = value == QtCore.Qt.Checked
        self._default_edit.setEnabled(enabled and self._model.can_set_default())
        if not enabled:
            self._default_edit.setChecked(self._model.default_parent_port())

    def save(self):
        new_properties = dict(self._properties)
        new_properties['optional'] = self._optional_edit.isChecked()
        new_properties['default'] = self._default_edit.isChecked()
        new_properties['name'] = self._label_edit.text()

        if self._properties != new_properties:
            cmd = user_commands.SetElementProperties(
                self._model.flow, self._model, new_properties)
            self._model.flow.undo_stack().push(cmd)


class FlowIOView(MovableElementViewInterface):
    connection_start_requested = QtCore.Signal(object)
    connection_end_requested = QtCore.Signal(object)
    transient_connection_add_request = QtCore.Signal(object)
    transient_connection_end_request = QtCore.Signal()
    open_add_context_requested = QtCore.Signal(
        QtWidgets.QGraphicsSceneMouseEvent)

    def __init__(self, model, parent=None):
        super(FlowIOView, self).__init__(model, parent)
        self._model = model
        self._input_port_views = collections.OrderedDict()
        self._output_port_views = collections.OrderedDict()
        self._init_base()
        self._label = NodeViewLabel(self._model.name, parent=self)
        self._init_actions()
        self._init_signalling()

    def _init_base(self):
        self.set_position(self._model.position)
        self.setZValue(2)

        self._port_label = None
        theme = themes.get_active_theme()
        self._node_color = theme.object_color
        self._unselected_border_color = theme.border_color
        self._border_width = 2.0
        self._brush = QtGui.QBrush(self._node_color)
        self._pen = QtGui.QPen(
            self._unselected_border_color, self._border_width)
        size = self._model.size
        self._bounding_rect = QtCore.QRectF(0, 0, size.width(), size.height())

    def _init_actions(self):
        pass

    def _init_signalling(self):
        # Label related
        self._signals.connect(self._model,
                              self._model.name_changed[str],
                              self._label.set_label)
        self._signals.connect(self._model,
                              self._label.label_edited[str],
                              self._handle_label_edited)

    @QtCore.Slot()
    def _show_info_requested(self):
        dialog = FlowIOInfo(self._model)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.save()

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            self._model.blockSignals(True)
            self._model.position = value
            self._model.blockSignals(False)
            for port_view in itertools.chain(self._input_port_views.values(),
                                             self._output_port_views.values()):
                port_view.notify_position_changed()
        return super(FlowIOView, self).itemChange(change, value)

    def remove_all_ports(self):
        self._input_port_views = collections.OrderedDict()
        self._output_port_views = collections.OrderedDict()

    def input_port_views(self):
        return self._input_port_views.values()

    def output_port_views(self):
        return self._output_port_views.values()

    def input_port_view(self, port):
        return self._input_port_views[port]

    def output_port_view(self, port):
        return self._output_port_views[port]

    @QtCore.Slot(flow.Port)
    def _handle_input_port_created(self, port):
        port_view = PortView(port, self)
        self._input_port_views[port] = port_view

        self._signals.connect(port,
                              port_view.connection_start_requested[object],
                              self.connection_start_requested)
        self._signals.connect(port,
                              port_view.connection_end_requested[object],
                              self.connection_end_requested)
        self._signals.connect(
            port, port_view.open_add_context_requested[
                QtWidgets.QGraphicsSceneMouseEvent],
            self.open_add_context_requested)

    @QtCore.Slot(flow.Port)
    def _handle_output_port_created(self, port):
        port_view = PortView(port, self)
        self._output_port_views[port] = port_view

        self._signals.connect(port,
                              port_view.connection_start_requested[object],
                              self.connection_start_requested)
        self._signals.connect(port,
                              port_view.connection_end_requested[object],
                              self.connection_end_requested)
        self._signals.connect(
            port, port_view.open_add_context_requested[
                QtWidgets.QGraphicsSceneMouseEvent],
            self.open_add_context_requested)

    @QtCore.Slot()
    def _handle_label_edited(self, label):
        if self._model.name != label:
            cmd = user_commands.EditNodeLabelCommand(
                self._model, self._model.name, label)
            self._model.flow.undo_stack().push(cmd)

    def paint(self, painter, option, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawPath(self._outline)

    def boundingRect(self):
        return self._bounding_rect

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.transient_connection_add_request.emit(self.model)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.transient_connection_end_request.emit()
        super().mouseReleaseEvent(event)

    def show_context_menu(self, menu_position):
        menu = QtWidgets.QMenu()
        submenu = QtWidgets.QMenu('Move port to position')
        old_index = self._model.index
        indices = list(self._model.available_indices())

        reorder_actions = []
        for index in indices:
            if index == old_index:
                action = submenu.addAction(
                    '{} (current position)'.format(index))
                action.setEnabled(False)
            else:
                action = submenu.addAction('{}'.format(index))
                action.setEnabled(self._model.can_reorder())
            reorder_actions.append(action)

        menu.addAction(self._delete_action)
        menu.addSeparator()
        menu.addMenu(submenu)
        menu.addSeparator()
        advanced_menu = menu.addMenu('Advanced')
        advanced_menu.addAction(self._show_info_action)

        self._delete_action.setEnabled(self._model.is_deletable())

        selected_action = menu.exec_(menu_position)

        if selected_action in reorder_actions:
            try:
                new_index = int(selected_action.text())
                indices[old_index], indices[new_index] = (
                    indices[new_index], indices[old_index])
            except Exception as e:
                core_logger.error('Failed to reorder ports: %s.', e)
                indices = None
            return indices
        else:
            return None

    def remove(self):
        self.blockSignals(True)
        self._label.blockSignals(True)
        super(FlowIOView, self).remove()
        for port_view in list(itertools.chain(
                self._input_port_views.values(),
                self._output_port_views.values())):
            port_view.setParentItem(None)
            self.scene().removeItem(port_view)
        self.remove_all_ports()
        if self._label is not None:
            self._label.setParentItem(None)
            self.scene().removeItem(self._label)
            del self._label
            self._label = None
        self.blockSignals(False)


class FlowInputView(FlowIOView):
    def __init__(self, model, parent=None):
        super(FlowInputView, self).__init__(model, parent)
        self._init()

    def _init(self):
        self.prepareGeometryChange()
        r = self._bounding_rect.adjusted(
            self._border_width / 2.0, self._border_width / 2.0,
            -self._border_width / 2.0, -self._border_width / 2.0)

        self._outline.moveTo(r.left(), r.top() + (r.height() / 2.0))
        self._outline.cubicTo(
            r.left(), r.top(), r.left(), r.top(), r.left() + (r.width() / 2.0),
            r.top() + (r.height() / 4.0))
        self._outline.cubicTo(
            r.right(), r.top() + (r.height() / 2.0), r.right(),
            r.top() + (r.height() / 2.0), r.left() + (r.width() / 2.0),
            r.top() + (3.0 * r.height() / 4.0))
        self._outline.cubicTo(
            r.left(), r.bottom(), r.left(), r.bottom(), r.left(),
            r.top() + (r.height() / 2.0))

        self._handle_output_port_created(self._model.output)

    def contextMenuEvent(self, event):
        new_order = self.show_context_menu(event.screenPos())
        if new_order is not None:
            cmd = user_commands.ChangeFlowInputOrderCommand(
                self._model.flow, new_order)
            self._model.flow.undo_stack().push(cmd)


class FlowOutputView(FlowIOView):
    def __init__(self, model, parent=None):
        super(FlowOutputView, self).__init__(model, parent)
        self._init()

    def _init(self):
        r = self._bounding_rect.adjusted(
            self._border_width / 2.0, self._border_width / 2.0,
            -self._border_width / 2.0, -self._border_width / 2.0)

        self._outline.moveTo(r.right(), r.top() + (r.height() / 2.0))
        self._outline.cubicTo(
            r.right(), r.top(), r.right(), r.top(),
            r.left() + (r.width() / 2.0), r.top() + (r.height() / 4.0))
        self._outline.cubicTo(
            r.left(), r.top() + (r.height() / 2.0), r.left(),
            r.top() + (r.height() / 2.0), r.left() + (r.width() / 2.0),
            r.top() + (3.0 * r.height() / 4.0))
        self._outline.cubicTo(
            r.right(), r.bottom(), r.right(), r.bottom(), r.right(),
            r.top() + (r.height() / 2.0))

        self._handle_input_port_created(self._model.input)

    def contextMenuEvent(self, event):
        new_order = self.show_context_menu(event.screenPos())
        if new_order is not None:
            cmd = user_commands.ChangeFlowOutputOrderCommand(
                self._model.flow, new_order)
            self._model.flow.undo_stack().push(cmd)
