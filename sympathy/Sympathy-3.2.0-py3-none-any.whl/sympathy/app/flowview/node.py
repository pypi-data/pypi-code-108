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
import json
import html
import functools
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets
import Qt.QtSvg as QtSvg

from sympathy.utils import prim
from sympathy.platform import editor as editor_api
from sympathy.platform.widget_library import StackedTextViews
from sympathy.platform import os_support as oss
from .basenode import BaseNodeView
from .types import get_label
from .. import user_commands
from .. import settings


def pre(text):
    return u'<pre>{}</pre>'.format(html.escape(text))


def _last_port(ports, name):
    res = None
    for port in ports:
        if port.name == name:
            res = port
    return res


class NodeInfo(QtWidgets.QDialog):
    def __init__(self, node, parent=None, flags=QtCore.Qt.Widget):
        super(NodeInfo, self).__init__(parent, flags)
        self._node = node
        self._init()

    def _init(self):
        self.setWindowTitle(u'Information: {}'.format(
            prim.format_display_string(self._node.name)))
        self._main_layout = QtWidgets.QVBoxLayout()
        self._tab_widget = QtWidgets.QTabWidget(self)
        self._init_general_tab()
        self._init_parameters_tab()
        self._main_layout.addWidget(self._tab_widget)
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        self._main_layout.addWidget(button_box)
        self.setLayout(self._main_layout)

    def _init_general_tab(self):
        general_tab = QtWidgets.QWidget(self)
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        layout.addRow('Label', get_label(
            prim.format_display_string(self._node.name)))
        layout.addRow('Library name', get_label(self._node.library_node_name))
        layout.addRow('Tags', get_label(', '.join(self._node.tags or [])))
        layout.addRow('Identifier', get_label(self._node.identifier))
        layout.addRow('Version', get_label(str(self._node.version)))
        layout.addRow('Author', get_label(self._node.author))
        layout.addRow('Maintainer', get_label(self._node.maintainer))
        layout.addRow('Copyright', get_label(self._node.copyright))
        layout.addRow('Class name', get_label(self._node.class_name))

        if settings.instance()['Gui/platform_developer']:
            layout.addRow('Namespace UUID', get_label(
                self._node.namespace_uuid()))
            layout.addRow('UUID', get_label(self._node.uuid))

        layout.addRow('Filename', get_label(
            prim.uri_to_path(self._node.source_file)))
        layout.addRow('State', get_label(self._node.state_string()))
        general_tab.setLayout(layout)
        self._tab_widget.addTab(general_tab, "General")

    def _init_parameters_tab(self):
        def overrides_debug_dict(node_):
            res = {}
            for flow in node_.parent_flows():
                model = self._node.get_override_parameter_model(flow)
                if model is None:
                    model_dict = None
                else:
                    model_dict = model.to_dict()
                res[flow.uuid] = model_dict
            return res

        parameters_tab = StackedTextViews()

        if self._node.has_overrides():
            base_parameters = pre(json.dumps(
                self._node.base_parameter_model.to_ordered_dict(), indent=2))
            parameters_tab.add_text('Base Parameters', base_parameters)

            overrides_text = pre(json.dumps(
                overrides_debug_dict(self._node), indent=2))
            parameters_tab.add_text('Parameter overrides', overrides_text)
        else:
            parameters = pre(json.dumps(
                self._node.parameter_model.to_ordered_dict(), indent=2))
            parameters_tab.add_text('Parameter Model', parameters)

        migrations_text = pre(json.dumps(
            self._node.migrations_debug_info(), indent=2))
        parameters_tab.add_text('Migrations', migrations_text)

        full_json = pre(json.dumps(self._node.to_dict(), indent=2))
        parameters_tab.add_text('Full JSON', full_json)

        self._tab_widget.addTab(parameters_tab, "Parameters")


class NodeView(BaseNodeView):
    """A standard node"""

    def __init__(self, model, parent=None):
        super(NodeView, self).__init__(model, parent)
        self._icon = None
        self._icon_renderer = None
        self._init()

    def _init(self):
        if self._model.has_svg_icon:
            self._icon = QtSvg.QGraphicsSvgItem(self)
            self._icon_renderer = QtSvg.QSvgRenderer(
                self._model.svg_icon_data, parent=self._icon)
            self._icon.setSharedRenderer(self._icon_renderer)
            self._icon.setZValue(2)
            self._icon.setCacheMode(
                QtWidgets.QGraphicsItem.DeviceCoordinateCache)
            icon_rect = self._icon.boundingRect()
            (width, height) = icon_rect.width(), icon_rect.height()
            r = self.boundingRect().adjusted(5, 5, -5, -5)
            max_width, max_height = r.width(), r.height()
            scale = 1.0
            if width / max_width > height / max_height:
                scale = max_width / width
            else:
                scale = max_height / height
            self._icon.setScale(scale)
            self._icon.setPos(5, 5)

        bounding_rect = self.boundingRect().adjusted(
            self._border_width, self._border_width,
            -self._border_width, -self._border_width)
        self._outline.addRoundedRect(bounding_rect, 7.0, 7.0)

        self._update_tooltip()
        self._init_context_menu()

    def _init_context_menu(self):
        self._context_menu = QtWidgets.QMenu()
        self._context_menu.addAction(self._configure_action)
        self._context_menu.addAction(self._execute_action)
        self._context_menu.addAction(self._reload_action)
        self._context_menu.addAction(self._abort_action)
        self._context_menu.addSeparator()
        self._context_menu.addAction(self._copy_action)
        self._context_menu.addAction(self._cut_action)
        self._context_menu.addAction(self._delete_action)
        self._context_menu.addSeparator()
        self._context_menu.addAction(self._node_help_action)
        self._context_menu.addSeparator()

        self._migrate_forward_action = QtWidgets.QAction(
            'Migrate node')
        self._migrate_forward_action.triggered.connect(
            self._migrate_forward)

        refactor_menu = self._context_menu.addMenu('Refactor')
        refactor_menu.addAction(self._migrate_forward_action)
        refactor_menu.addAction(
            self._create_subflow_from_selection_action)
        self._context_menu.addSeparator()

        self._input_actions_add = {}
        self._input_actions_rem = {}

        input_defs = self._model.creatable_input_defs()
        output_defs = self._model.creatable_output_defs()

        ports_menu = None
        if input_defs or output_defs:
            ports_menu = self._context_menu.addMenu('Ports')
            self._context_menu.addSeparator()

        advanced_menu = self._context_menu.addMenu('Advanced')

        advanced_menu.addAction(self._debug_action)
        advanced_menu.addAction(self._profile_action)

        advanced_menu.addSeparator()
        advanced_menu.addAction(self._edit_node_action)
        advanced_menu.addSeparator()

        self._exec_conf_menu = advanced_menu.addMenu(
            'Execution mode')
        self._conf_exec_action = QtWidgets.QAction(
            'Execute configuration only', self)
        self._normal_exec_action = QtWidgets.QAction(
            'Execute node normally', self)
        self._conf_exec_action.triggered.connect(
            self._set_conf_exec)
        self._normal_exec_action.triggered.connect(
            self._set_normal_exec)
        self._conf_exec_action.setCheckable(True)
        self._normal_exec_action.setCheckable(True)

        self._exec_conf_menu.addAction(
            self._conf_exec_action)
        self._exec_conf_menu.addAction(
            self._normal_exec_action)

        advanced_menu.addAction(self._show_info_action)

        if ports_menu and input_defs:
            input_menu = ports_menu.addMenu('Input')

            for i, def_ in enumerate(input_defs):
                name = def_['name']
                if self._model.is_config_port_name(name) and i > 0:
                    input_menu.addSeparator()

                action = QtWidgets.QAction(
                    f"Create: {def_['description']}", self)
                action.triggered.connect(
                    functools.partial(self._create_input, name))
                input_menu.addAction(action)
                self._input_actions_add[name] = action

                action = QtWidgets.QAction(
                    f"Remove: {def_['description']}", self)
                action.triggered.connect(
                    functools.partial(self._remove_input, name))
                input_menu.addAction(action)
                self._input_actions_rem[name] = action

        self._output_actions_add = {}
        self._output_actions_rem = {}

        if ports_menu and output_defs:
            output_menu = ports_menu.addMenu('Output')

            for i, def_ in enumerate(output_defs):
                name = def_['name']
                if name in {self._model._conf_port_name,
                            self._model._out_port_name} and i > 0:
                    output_menu.addSeparator()

                action = QtWidgets.QAction(
                    f"Create: {def_['description']}", self)
                action.triggered.connect(
                    functools.partial(self._create_output, name))
                output_menu.addAction(action)
                self._output_actions_add[name] = action

                action = QtWidgets.QAction(
                    f"Remove: {def_['description']}", self)
                action.triggered.connect(
                    functools.partial(self._remove_output, name))
                output_menu.addAction(action)
                self._output_actions_rem[name] = action

    def _set_conf_exec(self):
        cmd = user_commands.EditNodeExecutionConfig(self.model, True)
        self.model.flow.undo_stack().push(cmd)

    def _set_normal_exec(self):
        cmd = user_commands.EditNodeExecutionConfig(self.model, False)
        self.model.flow.undo_stack().push(cmd)

    def _migrate_forward(self):
        cmd = user_commands.MigrateNode(self.model)
        self.model.flow.undo_stack().push(cmd)

    def remove(self):
        for child in (self._icon, self._icon_renderer):
            if child is not None:
                del child
        super().remove()

    def _create_input(self, name):
        cmd = user_commands.CreateNamedInputPortCommand(self.model, name)
        self.model.flow.undo_stack().push(cmd)

    def _remove_input(self, name):
        last_port = _last_port(self.model.inputs, name)
        if last_port is not None:
            cmd = user_commands.DeleteInputPortCommand(last_port)
            self.model.flow.undo_stack().push(cmd)

    def _create_output(self, name):
        cmd = user_commands.CreateNamedOutputPortCommand(self.model, name)
        self.model.flow.undo_stack().push(cmd)

    def _remove_output(self, name):
        last_port = _last_port(self.model.outputs, name)
        if last_port is not None:
            cmd = user_commands.DeleteOutputPortCommand(last_port)
            self.model.flow.undo_stack().push(cmd)

    @QtCore.Slot()
    def _show_info_requested(self):
        dialog = NodeInfo(self._model)
        dialog.exec_()

    @QtCore.Slot()
    def _edit_node_requested(self):
        if isinstance(self.model.source_file, str):
            encoded_url = self.model.source_file.encode('ascii')
        else:
            encoded_url = self.model.source_file

        if (settings.instance()['Gui/system_editor'] or not
                editor_api.can_edit_file()):
            oss.open_url(QtCore.QUrl.fromEncoded(encoded_url).toString())
        else:
            path = prim.uri_to_path(self.model.source_file)
            if editor_api.edit_file(path) is False:
                print('Editor could not edit file.')

    def contextMenuEvent(self, event):
        self._abort_action.setEnabled(self._model.is_abortable())

        # Deletable means that the node is allowed to be changed such that
        # the flow structure is changed based on user input.
        conf_only = self._model.exec_conf_only

        self._conf_exec_action.setChecked(conf_only)
        self._conf_exec_action.setEnabled(not conf_only)
        self._normal_exec_action.setChecked(not conf_only)
        self._normal_exec_action.setEnabled(conf_only)

        self._exec_conf_menu.setEnabled(self._model.has_conf_output)
        can_migrate = self._model.migration_status in ('green', 'yellow')
        self._migrate_forward_action.setEnabled(can_migrate)

        if self._model.is_deletable():
            self._cut_action.setEnabled(True)
            self._delete_action.setEnabled(True)
            self._create_subflow_from_selection_action.setEnabled(True)
            self._configure_action.setEnabled(self._model.is_configurable())
            self._execute_action.setEnabled(self._model.is_executable())
            self._debug_action.setEnabled(self._model.is_debuggable())
            self._profile_action.setEnabled(self._model.is_profileable())
            self._reload_action.setEnabled(self._model.is_reloadable())
            self._edit_node_action.setEnabled(True)
        else:
            self._cut_action.setEnabled(False)
            self._delete_action.setEnabled(False)
            self._create_subflow_from_selection_action.setEnabled(False)
            self._configure_action.setEnabled(False)
            self._debug_action.setEnabled(self._model.is_debuggable())
            self._profile_action.setEnabled(self._model.is_profileable())
            self._reload_action.setEnabled(self._model.is_reloadable())
            self._edit_node_action.setEnabled(False)

        if not self.model.source_file.endswith('py'):
            self._debug_action.setEnabled(False)
            self._edit_node_action.setEnabled(False)
            self._edit_node_action.setText('Edit (Only for Python files)')
            self._debug_action.setText('Debug (Only for Python files)')

        if not editor_api.can_debug_file():
            self._debug_action.setEnabled(False)
            self._debug_action.setText('Debug (Editor plugin not installed)')

        for name, action in self._input_actions_add.items():
            action.setEnabled(self.model.can_create_input(name))

        for name, action in self._input_actions_rem.items():
            last_port = _last_port(self.model.inputs, name)
            action.setEnabled(last_port is not None and
                              self.model.can_delete_input(last_port))
        for name, action in self._output_actions_add.items():
            action.setEnabled(self.model.can_create_output(name))

        for name, action in self._output_actions_rem.items():
            last_port = _last_port(self.model.outputs, name)
            action.setEnabled(last_port is not None and
                              self.model.can_delete_output(last_port))
        self._context_menu.exec_(event.screenPos())

    def _tooltip(self):
        library_name = self._model.library_node_name
        if not self._model.ok:
            description = 'This node could not be found.'
        else:
            description = self._model.description.rstrip()

        return '<b>{}</b>{}'.format(
            self._html_escape(
                library_name),
            '<br/>{}'.format(self._html_escape(description))
            if description else '')
