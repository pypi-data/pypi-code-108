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
import collections
import itertools
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

from .types import MovableElementViewInterface
from . import decoration
from . decoration import (
    NodeStatusIconView, NodeViewLabel, NodeProgressView, Status)
from .. import themes
from .. import flow
from .. import user_commands
from .port import PortView
from sympathy.utils import prim
from sympathy.platform import editor as editor_api


class BaseNodeView(MovableElementViewInterface):
    """
    The BaseNodeView provides basic functionality for node like entities that
    can be connected, executed and configured.
    """

    connection_start_requested = QtCore.Signal(object)
    connection_end_requested = QtCore.Signal(object)
    transient_connection_add_request = QtCore.Signal(object)
    transient_connection_end_request = QtCore.Signal()
    open_add_context_requested = QtCore.Signal(
        QtWidgets.QGraphicsSceneMouseEvent)
    create_subflow_from_selection_requested = QtCore.Signal()
    reload_requested = QtCore.Signal(object)
    help_requested = QtCore.Signal(str)

    def __init__(self, model, parent=None):
        self._input_port_views = collections.OrderedDict()
        self._output_port_views = collections.OrderedDict()
        MovableElementViewInterface.__init__(self, model, parent)
        self._init_base()
        self._label = NodeViewLabel(self._model.name, parent=self)
        self._init_node_actions()
        self._init_signalling()
        self._init_port_views()
        self._node_state_changed()
        self.update_later()

    def _init_base(self):
        self.setZValue(5.1)
        self._status_icon = NodeStatusIconView(parent=self)
        self._status_icon.setPos(self._bounding_rect.left(),
                                 self._bounding_rect.top() - 10)
        self._dialog_icon = NodeStatusIconView(parent=self)
        self._dialog_icon.setPos(
            self._bounding_rect.right() - 30,
            self._bounding_rect.top() - 10)
        self._migrations_icon = NodeStatusIconView(parent=self)
        self._migrations_icon.setPos(self._bounding_rect.right() - 13,
                                     self._bounding_rect.top() - 10)
        self._update_migrations_icon()
        self._progress_view = None

        theme = themes.get_active_theme()

        self._border_width = 2.0
        self._border_color = theme.border_color
        self._pen = QtGui.QPen(self._border_color, self._border_width)
        self._node_color = theme.configurable_color
        self._brush = QtGui.QBrush(self._node_color)

    def _init_node_actions(self):
        theme = themes.get_active_theme()
        self._create_subflow_from_selection_action = self._create_action(
            'Create Subflow from Selected',
            self.create_subflow_from_selection_requested)

        self._configure_action = self._create_action(
            'Configure', self._handle_configure)
        self._execute_action = self._create_action(
            'Execute', self._handle_execute, icon=theme.execute)
        self._debug_action = self._create_action(
            'Debug', self._debug_requested)
        self._profile_action = self._create_action(
            'Profile', self._handle_profile, icon=theme.profile)
        self._reload_action = self._create_action(
            'Reload', self._handle_reload, icon=theme.reload)
        self._abort_action = self._create_action(
            'Abort', self._handle_abort, icon=theme.stop)
        self._edit_node_action = self._create_action(
            'Edit', self._edit_node_requested)
        self._node_help_action = self._create_action(
            'Help', self._node_help_requested, icon=theme.help)

    def _create_action(self, text, slot, icon=None):
        action = QtWidgets.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(icon))
        action.triggered.connect(slot)
        return action

    def _debug_requested(self):
        if editor_api.can_debug_file(prim.uri_to_path(self._model.source_file)):
            self._model.debug()

    def _init_signalling(self):
        self._signals.connect(
            self._model,
            self._model.input_port_created[flow.Port],
            self._handle_input_port_created)
        self._signals.connect(
            self._model,
            self._model.output_port_created[flow.Port],
            self._handle_output_port_created)
        self._signals.connect(
            self._model,
            self._model.input_port_removed[flow.Port],
            self._handle_input_port_removed)
        self._signals.connect(
            self._model,
            self._model.output_port_removed[flow.Port],
            self._handle_output_port_removed)

        self._signals.connect(
            self._model,
            self._model.parameter_viewer_changed,
            self._handle_parameter_view_changed)

        # Label related
        self._signals.connect(
            self._model,
            self._model.name_changed[str],
            self._label.set_label)
        self._signals.connect(
            self._model,
            self._label.label_edited[str],
            self._handle_label_edited)

        # State related
        self._signals.connect(
            self._model,
            self._model.state_changed,
            self._node_state_changed)
        self._signals.connect(
            self._model,
            self._model.progress_changed[int],
            self._update_progress)
        self._signals.connect(
            self._model,
            self.model.migration_status_changed,
            self._update_migrations_icon)

    def _init_port_views(self):
        for port in self._model.inputs:
            self._handle_input_port_created(port)
        for port in self._model.outputs:
            self._handle_output_port_created(port)

    def input_port_views(self):
        return self._input_port_views.values()

    def output_port_views(self):
        return self._output_port_views.values()

    def input_port_view(self, port):
        return self._input_port_views[port]

    def output_port_view(self, port):
        return self._output_port_views[port]

    def _update_migrations_icon(self):
        status = self._model.migration_status
        if status == 'red':
            self._migrations_icon.set_icon_type(Status.red_migration)
        elif status == 'yellow':
            self._migrations_icon.set_icon_type(Status.yellow_migration)
        elif status == 'green':
            self._migrations_icon.set_icon_type(Status.green_migration)
        else:
            self._migrations_icon.set_icon_type(Status.none)

    def _node_state_info(self):
        icon_type = Status.none
        new_brush = QtGui.QBrush(self._node_color)
        show_progress = None
        theme = themes.get_active_theme()

        if not self._model.ok:
            # Red color
            new_brush = QtGui.QBrush(theme.error_color)
            icon_type = self.missing_status()
            show_progress = False
        elif self._model.in_error_state():
            # Red color
            new_brush = QtGui.QBrush(theme.error_color)
            icon_type = Status.error
            show_progress = False
        elif self._model.is_successfully_executed():
            if self._model.is_done_locked():
                # Purple
                color = theme.done_locked_color
                icon_type = Status.executed_locked
            else:
                # Green
                color = theme.done_color
                icon_type = Status.executed
            new_brush = QtGui.QBrush(color)
            show_progress = False
        elif self._model.is_executing():
            # Blue
            new_brush = QtGui.QBrush(theme.queued_color)
            icon_type = Status.executing
            show_progress = True
        elif self._model.is_queued():
            # Blue
            new_brush = QtGui.QBrush(theme.queued_color)
            icon_type = Status.queued
        elif (self._model.is_executable() and
              self._model.is_configuration_valid()):
            # Yellow
            new_brush = QtGui.QBrush(theme.executable_color)
            icon_type = Status.executable
            show_progress = False
        else:
            # Standard gray
            new_brush = QtGui.QBrush(self._node_color)
            if not self._model.is_configuration_valid():
                icon_type = Status.unconfigured
            else:
                icon_type = Status.none
            show_progress = False

        return {
            'icon': icon_type, 'brush': new_brush, 'progress': show_progress}

    @QtCore.Slot()
    def _node_state_changed(self):
        # Change the color (and the icon) of the node depending on the state
        old_brush = self._brush
        info = self._node_state_info()

        icon_type = info['icon']
        brush = info['brush']
        show_progress = info['progress']

        if show_progress is None:
            # Keep progress.
            pass
        elif show_progress:
            self._show_progress_view()
        else:
            self._hide_progress_view()

        self._brush = brush
        self._update_tooltip(decoration.get_status_tooltip(icon_type))
        self._status_icon.set_icon_type(icon_type)

        if self._brush != old_brush:
            self.update_later()

    @QtCore.Slot()
    def update_later(self):
        # QtCore.QTimer.singleShot(0, self.update)
        self.update()

    def _tooltip(self):
        return ''

    def _update_tooltip(self, state_tooltip=None):
        tooltip = self._tooltip()

        if state_tooltip is None:
            state_tooltip = self._state_tooltip()
        if state_tooltip:
            state_tooltip = '<i>{}</i>'.format(state_tooltip)

        tooltips = [t for t in [tooltip, state_tooltip] if t]
        self.setToolTip('<br/><br/>'.join(tooltips))

    def _state_tooltip(self):
        icon_type = self._node_state_info()['icon']
        state_tooltip = decoration.get_status_tooltip(icon_type)
        if state_tooltip:
            return self._html_escape(state_tooltip)

    def _html_escape(self, text):
        return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))

    @QtCore.Slot(int)
    def _update_progress(self, progress):
        self._show_progress_view()
        if self._progress_view:
            self._progress_view.update_progress(progress)

    def _show_progress_view(self):
        if self._progress_view is None and self._model.is_executing():
            self._progress_view = NodeProgressView(parent=self)

    def _hide_progress_view(self):
        if self._progress_view is not None:
            if self.scene() is not None:
                self._progress_view.setParentItem(None)
                self.scene().removeItem(self._progress_view)
            del self._progress_view
            self._progress_view = None

    def _handle_abort(self):
        # Prevent node from becoming stuck in persistent pending state.
        # after abort is called when the node is done.
        # TODO: implement more robust solution in the Node/Flow class
        # so that this can not happen from other reasons.
        if self._model.is_abortable():
            self._model.flow.abort_node_action(self._model)
        else:
            self._model.flow.app_core.display_custom_node_message(
                self._model,
                warning='Could not abort node.')

    def _handle_reload(self):
        self._model.flow.reload_node_action(self._model)

    def _handle_configure(self):
        self._model.flow.configure_node_action(self._model)

    def _handle_execute(self):
        self._model.flow.execute_node_action(self._model)

    def _handle_profile(self):
        self._model.flow.profile_node_action(self._model)

    @QtCore.Slot(flow.Port)
    def _handle_input_port_created(self, port):
        port_view = PortView(port, self)
        self._input_port_views[port] = port_view

        self._signals.connect(
            port, port_view.connection_start_requested[object],
            self.connection_start_requested)
        self._signals.connect(
            port, port_view.connection_end_requested[object],
            self.connection_end_requested)
        self._signals.connect(
            port, port_view.open_add_context_requested[
                QtWidgets.QGraphicsSceneMouseEvent],
            self.open_add_context_requested)

    @QtCore.Slot(flow.Port)
    def _handle_output_port_created(self, port):
        port_view = PortView(port, self)
        self._output_port_views[port] = port_view

        self._signals.connect(
            port, port_view.connection_start_requested[object],
            self.connection_start_requested)
        self._signals.connect(
            port, port_view.connection_end_requested[object],
            self.connection_end_requested)
        self._signals.connect(
            port, port_view.open_add_context_requested[
                QtWidgets.QGraphicsSceneMouseEvent],
            self.open_add_context_requested)

    @QtCore.Slot(flow.Port)
    def _handle_input_port_removed(self, port):
        view = self._input_port_views.pop(port, None)
        if view is not None and self.scene():
            self.scene().removeItem(view)

    @QtCore.Slot(flow.Port)
    def _handle_output_port_removed(self, port):
        view = self._output_port_views.pop(port, None)
        if view is not None and self.scene():
            self.scene().removeItem(view)

    @QtCore.Slot(bool)
    def _handle_parameter_view_changed(self, state):
        if state:
            self._dialog_icon.set_icon_type(Status.configuring)
        else:
            self._dialog_icon.set_icon_type(Status.none)
        self.update_later()

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for port_view in itertools.chain(
                    self._input_port_views.values(),
                    self._output_port_views.values()):
                port_view.notify_position_changed()
        return super(BaseNodeView, self).itemChange(change, value)

    def remove(self):
        self.blockSignals(True)
        self._label.blockSignals(True)
        super(BaseNodeView, self).remove()
        for port_view in itertools.chain(
                self._input_port_views.values(),
                self._output_port_views.values()):
            port_view.remove()
            port_view.setParentItem(None)
            self.scene().removeItem(port_view)
        self.remove_all_ports()
        if self._label is not None:
            self._label.setParentItem(None)
            self.scene().removeItem(self._label)
            del self._label
            self._label = None
        self._hide_progress_view()
        self.blockSignals(False)

    def remove_all_ports(self):
        del self._input_port_views
        del self._output_port_views
        self._input_port_views = collections.OrderedDict()
        self._output_port_views = collections.OrderedDict()

    @QtCore.Slot(str)
    def _handle_label_edited(self, label):
        if self._model.name != label:
            cmd = user_commands.EditNodeLabelCommand(
                self._model, self._model.name, label)
            self._model.flow.undo_stack().push(cmd)

    def paint(self, painter, options, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawPath(self._outline)

    def mouseDoubleClickEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            event.ignore()
            return

        if self._model.in_error_state():
            self._handle_reload()
        elif self._model.is_executable():
            self._handle_execute()
        # elif self._model.is_configurable():
        #     self._model.configure()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.transient_connection_add_request.emit(self.model)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.transient_connection_end_request.emit()
        super().mouseReleaseEvent(event)

    def set_this_z(self):
        self.setZValue(5)
        for port in self.input_port_views():
            port.set_this_z()
        for port in self.output_port_views():
            port.set_this_z()

    def set_other_z(self):
        self.setZValue(4)
        for port in self.input_port_views():
            port.set_other_z()
        for port in self.output_port_views():
            port.set_other_z()

    def reset_z(self):
        self.setZValue(3)
        for port in self.input_port_views():
            port.reset_z()
        for port in self.output_port_views():
            port.reset_z()

    @QtCore.Slot()
    def _edit_node_requested(self):
        raise NotImplementedError('Not implemented for interface')

    @QtCore.Slot()
    def _node_help_requested(self):
        self.help_requested.emit(self._model.identifier)

    def missing_status(self):
        return Status.missing_node
