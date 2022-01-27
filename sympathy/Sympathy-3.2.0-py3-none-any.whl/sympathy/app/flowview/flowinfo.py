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
import os.path

import Qt.QtGui as QtGui
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

from sympathy.utils import uuid_generator
from sympathy.utils import prim
from sympathy.platform.widget_library import (PathListWidget, PathLineEdit,
                                              StackedTextViews)

from .types import get_label
from .. import settings
from .. wizards.flowwizard import TagComboBox
from sympathy.app import user_commands
from sympathy.app.windows import preferences
import sympathy.app.library


def _nativepath_or_empty(path):
    if path:
        path = prim.nativepath(path)
    return path


def show_info(model):
    dialog = FlowInfo(model, stub=False)
    result = dialog.exec_()
    cmds = []
    if result == QtWidgets.QDialog.Accepted:
        flow_info = dialog.get_properties()
        if model.is_linked:
            # Handle link label changes as a separate command since it belongs
            # to a different flow.
            link_label = flow_info.pop('label')
            if link_label != model.name:
                cmds.append(user_commands.EditNodeLabelCommand(
                    model, model.name, link_label))
        old_flow_info = model.get_properties()
        if any(old_flow_info[k] != flow_info[k] for k in flow_info):
            cmds.append(user_commands.SetElementProperties(
                model, model, flow_info))
        libraries = dialog.get_libraries()
        pythonpaths = dialog.get_pythonpaths()
        if (libraries != model.library_paths() or
                pythonpaths != model.python_paths()):
            cmds.append(user_commands.SetFlowLibraries(
                model, libraries, pythonpaths))
        old_env = model.environment
        env = dialog.get_environment()
        if env != old_env:
            cmds.append(user_commands.EditWorkflowEnvironment(
                model, env, old_env))

        macro_cmd = user_commands.MacroCommand(cmds, text='Changing flow properties')
        model.undo_stack().push(macro_cmd)


def pre(text):
    return u'<pre>{}</pre>'.format(html.escape(text))


class LinkInfoTab(QtWidgets.QWidget):
    def __init__(self, flow_model, stub, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)

        # Set up editable flow info.
        self._label_edit = QtWidgets.QLineEdit(flow_model.link_label)
        layout.addRow('Link label', self._label_edit)

        layout.addRow('Filename', get_label(
            _nativepath_or_empty(flow_model.root_or_linked_flow_filename)))

        if flow_model.is_linked and not flow_model.node_identifier:
            layout.addRow(
                'Path from parent flow', get_label(
                    _nativepath_or_empty(flow_model.source_uri)))
        self.setLayout(layout)

    @property
    def label(self):
        return self._label_edit.text()


class ShortTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Maximum)

    def sizeHint(self):
        size_hint = super().sizeHint()
        size_hint.setHeight(50)
        return size_hint


class GeneralInfoTab(QtWidgets.QWidget):
    def __init__(self, flow_model, stub, parent=None):
        super().__init__(parent)
        self._flow = flow_model

        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)

        # Set up editable flow info.
        flow_info = flow_model.get_properties()
        if flow_model.is_linked:
            label = flow_info['source_label']
        else:
            label = flow_info['label']
        self._label_edit = QtWidgets.QLineEdit(label)
        layout.addRow('Label', self._label_edit)
        self._description_edit = ShortTextEdit()
        self._description_edit.setPlainText(flow_info['description'])
        self._description_edit.setToolTip(
            "Short description used in GUI and documentation.")
        layout.addRow('Description', self._description_edit)
        self._documentation_edit = QtWidgets.QPlainTextEdit()
        self._documentation_edit.setPlainText(flow_info['documentation'])
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        self._documentation_edit.setToolTip(
            "Extended help text used in documentation.")
        layout.addRow('Documentation', self._documentation_edit)
        self._version_edit = QtWidgets.QLineEdit(flow_info['version'])
        layout.addRow('Version', self._version_edit)
        self._author_edit = QtWidgets.QLineEdit(flow_info['author'])
        layout.addRow('Author', self._author_edit)
        if flow_model.maintainer:
            self._maintainer_edit = QtWidgets.QLabel(flow_model.maintainer)
            layout.addRow('Maintainer', self._maintainer_edit)
        self._copyright_edit = QtWidgets.QLineEdit(flow_info['copyright'])
        layout.addRow('Copyright', self._copyright_edit)

        self._tag_combo = TagComboBox(
            flow_info['tag'], self._flow.app_core.library_root().tags.root)
        layout.addRow('Tag', self._tag_combo)

        self._identifier_edit = QtWidgets.QLineEdit(flow_info['identifier'])
        layout.addRow('Identifier', self._identifier_edit)

        layout.addRow('Filename', get_label(
            _nativepath_or_empty(flow_model.root_or_linked_flow_filename)))

        if not _is_file_flow(flow_model):
            self._identifier_edit.setEnabled(False)
            self._tag_combo.setEnabled(False)

        self._icon_edit = PathLineEdit(
            self._flow.icon_filename,
            root_path=os.path.dirname(self._flow.root_or_linked_flow_filename),
            placeholder_text='SVG filename',
            filter='SVG icon files (*.svg);;All files (*.*)',
            default_relative=True)

        layout.addRow('Icon', self._icon_edit)

        if not self._flow.root_or_linked_flow_filename:
            self._icon_edit.setEnabled(False)

        if settings.instance()['Gui/platform_developer']:
            # Show different UUIDs depending on whether subflow is linked and
            # whether we are showing stub or full flow.
            namespace_uuid, item_uuid = uuid_generator.split_uuid(
                flow_model.full_uuid)
            layout.addRow('Namespace UUID', get_label(pre(namespace_uuid)))
            if flow_model.is_linked:
                if stub:
                    layout.addRow('UUID', get_label(pre(item_uuid)))
                    layout.addRow(
                        'Source UUID', get_label(pre(flow_model.source_uuid)))
                else:
                    if flow_model.source_uuid is not None:
                        layout.addRow('UUID', get_label(
                            pre(flow_model.source_uuid)))
            else:
                layout.addRow('UUID', get_label(pre(item_uuid)))
        layout.addRow(
            'State', get_label(pre(flow_model.state_string())))

        self.setLayout(layout)

    @property
    def label(self):
        return self._label_edit.text()

    @property
    def description(self):
        return self._description_edit.toPlainText()

    @property
    def documentation(self):
        return self._documentation_edit.toPlainText()

    @property
    def author(self):
        return self._author_edit.text()

    @property
    def version(self):
        return self._version_edit.text()

    @property
    def copyright(self):
        return self._copyright_edit.text()

    @property
    def icon(self):
        return self._icon_edit.path()

    @property
    def tag(self):
        return self._tag_combo.value()

    @property
    def identifier(self):
        return self._identifier_edit.text()


def _is_file_flow(flow):
    return (flow.root_or_linked_flow_filename and
            flow.root_or_linked_flow() is flow)


class LibrariesTab(QtWidgets.QWidget):
    def __init__(self, flow_model, parent=None):
        super().__init__(parent)
        self._flow = flow_model
        self._library_widget = PathListWidget(
            flow_model.library_paths(),
            recent=preferences.get_recent_libs(),
            root_path=os.path.dirname(self._flow.root_or_linked_flow_filename),
            default_relative=True)
        self._pythonpaths_widget = PathListWidget(
            flow_model.python_paths(),
            root_path=os.path.dirname(self._flow.root_or_linked_flow_filename),
            default_relative=True)

        if not _is_file_flow(self._flow):
            self._library_widget.setEnabled(False)
            self._pythonpaths_widget.setEnabled(False)

        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        layout.addRow('Workflow libraries', self._library_widget)
        layout.addRow('Python paths', self._pythonpaths_widget)
        self.setLayout(layout)

    @property
    def library_paths(self):
        return self._library_widget.paths()

    @property
    def recent_library_paths(self):
        return self._library_widget.recent()

    @property
    def python_paths(self):
        return self._pythonpaths_widget.paths()


class EnvironmentTab(QtWidgets.QWidget):
    root_msg = ('Note: Only the root flow and linked flows can have '
                'workflow environment variables')

    def __init__(self, flow_model, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        self._env_widget = preferences.ModifyEnvironmentWidget(self)

        if flow_model is not flow_model.root_or_linked_flow():
            self._env_widget.setEnabled(False)
            layout.addWidget(QtWidgets.QLabel(self.root_msg))

        layout.addWidget(self._env_widget)
        self._env_widget.set_variables(flow_model.environment)
        self.setLayout(layout)

    @property
    def environment(self):
        return self._env_widget.variables()


def other_info_tab(flow_model, stub):
    stacked_widget = StackedTextViews()

    full_json = pre(json.dumps(flow_model.to_dict(stub=stub), indent=2))
    stacked_widget.add_text('Full JSON', full_json)

    aggregation = pre(json.dumps(
        flow_model.aggregation_settings, indent=2))
    stacked_widget.add_text('Aggregation Settings', aggregation)

    overrides = pre(json.dumps(flow_model.override_parameters, indent=2))
    stacked_widget.add_text('Parameter Overrides', overrides)

    pretty_graph = pre(flow_model.print_graph())
    stacked_widget.add_text('Graph', pretty_graph)

    overrides_migrations = {}
    for tree_uuid, overrides_model in flow_model.override_parameters.items():
        overrides_migrations[tree_uuid] = None
        migration_chain = flow_model._get_overrides_migration_chain(
            tree_uuid=tree_uuid)
        if migration_chain is not None:
            overrides_migrations[tree_uuid] = migration_chain.debug_dict()
    migrations_text = pre(json.dumps(overrides_migrations, indent=2))
    stacked_widget.add_text('Override migrations', migrations_text)

    return stacked_widget


class FlowInfo(QtWidgets.QDialog):
    """Show and allow changing basic flow information."""

    def __init__(self, flow_model, stub, parent=None, flags=QtCore.Qt.Widget):
        super().__init__(parent, flags)
        self._is_linked = flow_model.is_linked

        self.setWindowTitle(u'Properties {}'.format(
            prim.format_display_string(flow_model.name)))
        self._main_layout = QtWidgets.QVBoxLayout()

        if self._is_linked:
            self._link_info = LinkInfoTab(flow_model, stub, parent)

        self._general_info = GeneralInfoTab(flow_model, stub, parent)
        self._libraries_tab = LibrariesTab(flow_model, parent)
        self._environment_tab = EnvironmentTab(flow_model, parent)

        if flow_model.library_node:
            for tab in [self._general_info,
                        self._libraries_tab,
                        self._environment_tab]:
                tab.setEnabled(False)

        tab_widget = QtWidgets.QTabWidget(self)
        tab_widget.addTab(self._general_info, 'General')
        if self._is_linked:
            tab_widget.addTab(self._link_info, 'Link')
        tab_widget.addTab(self._libraries_tab, 'Libraries')

        tab_widget.addTab(self._environment_tab, 'Environment variables')
        tab_widget.addTab(other_info_tab(flow_model, stub), 'Advanced')

        self._main_layout.addWidget(tab_widget)
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.apply)
        button_box.rejected.connect(self.reject)
        self._main_layout.addWidget(button_box)
        self.setLayout(self._main_layout)

    def apply(self):
        self.accept()
        preferences.set_recent_libs(
            self._libraries_tab.recent_library_paths)

    def get_properties(self):
        """Return a dictionary with the (possibly updated) flow info."""
        flow_info = {
            'label': self._general_info.label,
            'description': self._general_info.description,
            'documentation': self._general_info.documentation,
            'author': self._general_info.author,
            'version': self._general_info.version,
            'copyright': self._general_info.copyright,
            'icon_filename': self._general_info.icon,
            'tag': self._general_info.tag,
            'identifier': self._general_info.identifier}
        if self._is_linked:
            flow_info.update({
                'source_label': self._general_info.label,
                'label': self._link_info.label})
        return flow_info

    def get_libraries(self):
        """Return a list with the (possibly updated) workflow libraries."""
        return self._libraries_tab.library_paths

    def get_pythonpaths(self):
        """Return a list with the (possibly updated) workflow python paths."""
        return self._libraries_tab.python_paths

    def get_environment(self):
        """Return a list with the (possibly updated) workflow python paths."""
        return self._environment_tab.environment
