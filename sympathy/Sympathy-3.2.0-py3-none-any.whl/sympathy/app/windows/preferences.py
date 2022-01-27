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
import distutils.spawn
import collections
import pygments.styles
from typing import Dict
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from sympathy.platform import feature
from sympathy.platform import version_support as vs
from sympathy.platform import editor as editor_api
from sympathy.platform import widget_library as sywidgets
from sympathy.platform import item_models as symodels
from sympathy.platform.item_delegates import UniqueItemDelegate
from sympathy.app.widgets import settings_widgets as setwidgets
from sympathy.app import settings
from sympathy.app.environment_variables import instance as env_instance
from sympathy.platform import library as library_platform
from sympathy.api import library as library_api
from sympathy.app.interfaces.preferences import PreferenceSectionWidget
from sympathy.app import package
import sympathy.app.util
import sympathy.app.actions
from .. import themes
num_recent_libs = 15
ENV = env_instance()


# Determines the order in which actions are applied
A_ENV, A_LIBRARY_PATH, A_LIBRARY_RELOAD, A_LIBRARY_TYPE, A_LIBRARY_HIGHLIGHTER = range(5)  # noqa


class PreferencesItem(QtGui.QStandardItem):
    """docstring for PreferencesItem"""

    def __init__(self, title):
        super().__init__(title)
        self._widget = None

    @property
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, value):
        self._widget = value


class PreferencesNavigator(QtWidgets.QListView):
    preferences_widget_change = QtCore.Signal(PreferenceSectionWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = QtGui.QStandardItemModel()
        self.setModel(self._model)
        model = self.selectionModel()
        model.selectionChanged[
            QtCore.QItemSelection, QtCore.QItemSelection].connect(
            self.leaf_selected)

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def leaf_selected(self, selected_item, deselected_item):
        self.preferences_widget_change.emit(self._model.itemFromIndex(
            selected_item.indexes()[0]).widget)

    def _get_item(self, title, default_item):
        matches = self._model.findItems(
            title, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
        if len(matches) > 0:
            return True, matches[0]
        else:
            return False, default_item

    def add_widget(self, widget):
        root_exists = False
        item = None
        name = widget.name()
        item_found, item = self._get_item(name, PreferencesItem(name))
        root = item
        root_exists = item_found

        item.widget = widget
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        if not root_exists:
            self._model.appendRow(root)
            if root is not item:
                root.setFlags(QtCore.Qt.NoItemFlags)


class PreferencesDialog(QtWidgets.QDialog):
    """docstring for PreferencesDialog"""

    def __init__(self, app_core, preference_widgets=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Preferences')
        self._app_core = app_core
        self._preference_widgets = preference_widgets or []
        self._widgets = []
        self._imp_to_vis_widget = {}
        self._pane = None
        self._tree_widget = None
        self.setMinimumSize(QtCore.QSize(825, 425))
        self.setMaximumSize(QtCore.QSize(2000, 2000))

        self._pane = QtWidgets.QStackedWidget()
        self._pane.setMinimumSize(QtCore.QSize(600, 275))
        self._pane.setMaximumSize(QtCore.QSize(1900, 1900))
        self._tree_widget = PreferencesNavigator()
        self._tree_widget.setMinimumSize(QtCore.QSize(150, 275))
        self._tree_widget.setMaximumSize(QtCore.QSize(150, 1900))
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._tree_widget)
        ok_cancel_layout = QtWidgets.QVBoxLayout()
        ok_cancel_buttons = QtWidgets.QDialogButtonBox()
        ok_cancel_buttons.addButton(QtWidgets.QDialogButtonBox.Ok)
        ok_cancel_buttons.addButton(QtWidgets.QDialogButtonBox.Cancel)
        ok_cancel_buttons.accepted.connect(self.accept)
        ok_cancel_buttons.rejected.connect(self.reject)
        ok_cancel_layout.addItem(layout)
        ok_cancel_layout.addWidget(ok_cancel_buttons)
        for widget in self._preference_widgets:
            self._add_widget(widget)
        layout.addWidget(self._pane, 1)
        self.setLayout(ok_cancel_layout)
        self._tree_widget.preferences_widget_change[
            PreferenceSectionWidget].connect(self.change_widget)
        self.accepted.connect(self.save)

    def _add_widget(self, widget):
        self._widgets.append(widget)
        container = QtWidgets.QScrollArea()
        container.setWidgetResizable(True)
        container.setWidget(widget)
        container.ensureWidgetVisible(widget)
        self._pane.addWidget(container)
        self._tree_widget.add_widget(widget)
        self._imp_to_vis_widget[widget] = container

    @QtCore.Slot(PreferenceSectionWidget)
    def change_widget(self, widget):
        self._pane.setCurrentWidget(self._imp_to_vis_widget[widget])

    @QtCore.Slot()
    def save(self):
        actions = []
        for widget in self._widgets:
            actions.extend(widget.save() or [])
        settings.instance().sync()

        # Each action_id is performed only once.
        for action_id, action in sorted(
                collections.OrderedDict(actions).items()):
            action()


class GeneralSectionWidget(PreferenceSectionWidget):
    """General settings"""

    _name = 'General'

    def __init__(self, menu_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._menu_manager = menu_manager

        settings_ = settings.instance()

        self._layout = self._create_layout()
        self._init_gui_settings(settings_)

    def _init_gui_settings(self, settings_):
        self._snap_enabled = setwidgets.BoolCheckBox('Gui/snap_enabled')
        choices = settings.snap_types
        self._snap_type = setwidgets.StringComboBox('Gui/snap_type', choices)

        self._theme = setwidgets.StringComboBox(
            'Gui/theme', sorted(themes.available_themes().keys()))

        self._use_system_editor = setwidgets.BoolCheckBox('Gui/system_editor')
        self._platform_developer = setwidgets.BoolCheckBox(
            'Gui/platform_developer')
        self._autosave = setwidgets.BoolCheckBox('autosave')
        self._ask_for_save = setwidgets.BoolCheckBox('ask_for_save')
        self._on_start = setwidgets.StringComboBox(
            'Gui/on_start', settings.on_start_choice)
        self._show_splash = setwidgets.BoolCheckBox('Gui/show_splash_screen')

        self._docking = setwidgets.StringComboBox(
            'Gui/docking_enabled', ['Detachable', 'Movable', 'Locked'])
        self._conn_shape = setwidgets.StringComboBox(
            'Gui/flow_connection_shape', ['Spline', 'Line'])

        self._clear_recent = QtWidgets.QPushButton('Clear recent flow list')
        self._clear_recent.setMaximumWidth(150)
        self._clear_recent.clicked.connect(self.clear_recent)

        self._max_msgs = setwidgets.IntegerSpinBox('Gui/max_archived_messages')
        self._max_msgs.setRange(0, 1000)
        self._max_msgs.setStepType(QtWidgets.QSpinBox.AdaptiveDecimalStepType)

        self._layout.addRow('Snap nodes to grid', self._snap_enabled)
        self._layout.addRow('Grid type', self._snap_type)
        if settings_['Gui/experimental']:
            self._layout.addRow(
                'Theme (takes effect after restart) (EXPERIMENTAL!)',
                self._theme)
            self._layout.addRow('Platform developer mode (EXPERIMENTAL)',
                                self._platform_developer)
        if editor_api.can_edit_file():
            self._add_row('Ensure system editor',
                          self._use_system_editor,
                          'Determines the external program used to edit '
                          'python files.\nThe system editor is the program '
                          'associated with python files and it will be '
                          'used if this option is checked or\nwhen unchecked '
                          'if no editor plugin is installed.')
        self._add_row('Ask about saving flows on quit/close',
                      self._ask_for_save,
                      'If checked, closing a flow with unsaved changes will '
                      'trigger a dialog asking you if you would like to save '
                      'the changes. If unchecked, the unsaved changes would '
                      'silently be discarded.')
        self._add_row('Autosave flows', self._autosave,
                      'If checked, changes to flows are automatically saved '
                      'every few seconds.')
        self._layout.addRow('Open when program starts', self._on_start)
        self._add_row('Show splash screen', self._show_splash,
                      'Show a splash screen while Sympathy is starting.')
        self._add_row('Views docking behavior', self._docking,
                      'Set the behavior of dockable views like the library '
                      'view and messages view.')
        self._add_row('Max archived messages', self._max_msgs,
                      'Maximum number of archived messages stored by the '
                      'messages view. After this number has been reached '
                      'old messages will be discarded. Set this to zero '
                      'to never discard archived messages.')

        if settings_['Gui/experimental']:
            self._layout.addRow(
                'Connection shape (EXPERIMENTAL)', self._conn_shape)

        self._layout.addRow(self._clear_recent)
        self.setLayout(self._layout)

    def _settings_widgets(self):
        return [
            self._snap_enabled,
            self._snap_type,
            self._use_system_editor,
            self._platform_developer,
            self._ask_for_save,
            self._autosave,
            self._on_start,
            self._theme,
            self._show_splash,
            self._docking,
            self._conn_shape,
            self._max_msgs,
        ]

    def clear_recent(self):
        settings.instance()['Python/recent_library_path'] = []
        settings.instance()['Gui/recent_flows'] = []
        if self._menu_manager is not None:
            self._menu_manager.update_menus()


def get_recent_libs():
    settings_ = settings.instance()
    return settings_['Python/recent_library_path']


def set_recent_libs(recent_libs):
    settings_ = settings.instance()
    settings_['Python/recent_library_path'] = recent_libs[
        :num_recent_libs]


class NodeConfigsSectionWidget(PreferenceSectionWidget):
    """Node config settings"""

    _name = 'Node Configuration'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._available_themes = None

        if self._available_themes is None:
            self._available_themes = sorted(pygments.styles.get_all_styles())

        settings_ = settings.instance()
        self._layout = self._create_layout()
        self._init_gui_settings(settings_)

    def _init_gui_settings(self, settings_):
        self._code_editor_theme = setwidgets.StringComboBox(
            'Gui/code_editor_theme', self._available_themes)
        self._show_message_area = setwidgets.StringComboBox(
            'Gui/show_message_area', settings.show_message_area_choice)
        self._nodeconfig_confirm_cancel = setwidgets.BoolCheckBox(
            'Gui/nodeconfig_confirm_cancel')

        self._add_row('Code editor theme', self._code_editor_theme,
                      'Set the color theme for syntax highlighting in any '
                      'code editors inside node configurations.')
        self._add_row('Show message area', self._show_message_area,
                      'Set behavior of the message area that can show up '
                      'at the top of some node configurations, for example '
                      'if the configuration is incorrect.')
        self._add_row('Confirm cancel on node configurations',
                      self._nodeconfig_confirm_cancel,
                      'If checked, closing a node configuration with unsaved '
                      'changes will trigger a dialog asking you if you would '
                      'like to save the changes. If unchecked, the unsaved '
                      'changes would silently be discarded.')
        self.setLayout(self._layout)

    def _settings_widgets(self):
        return [
            self._nodeconfig_confirm_cancel,
            self._code_editor_theme,
            self._show_message_area,
        ]


class LibrariesSectionWidget(PreferenceSectionWidget):
    """Settings concerning the node libraries"""

    library_path_changed = QtCore.Signal()

    _name = 'Node Libraries'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings_ = settings.instance()
        self._layout = self._create_layout()
        self._initial_library = []
        self._initial_recent = get_recent_libs()
        self._path_list = sywidgets.PathListWidget(
            self._initial_library, root_path=settings_['install_folder'],
            recent=self._initial_recent, default_relative=False,
            parent=self)
        self._path_list.setToolTip(
            'Libraries added by path (global).\nSympathy will include these '
            'libraries among the active libraries')
        self._layout.addRow(
            self._centered_label('Libraries added by path'), self._path_list)

        self._installed_libs = QtWidgets.QListWidget(self)
        self._installed_libs.setToolTip(
            'Libraries added in to the python environment (global).\nSympathy '
            'will include these libraries among the active libraries.\n\n'
            'Can only be changed by uninstalling the packages from the python '
            'environment.')

        for entrypoint in library_platform.available_libraries(load=False):
            self._installed_libs.addItem(
                f'{entrypoint.dist} ({entrypoint.name})')

        self._layout.addRow(
            self._centered_label('Libraries added to python'),
            self._installed_libs)

        self.setLayout(self._layout)

    def update_data(self):
        settings_ = settings.instance()
        self._initial_library = settings_['Python/library_path']
        self._path_list.set_items(self._initial_library)

    def save(self):
        result = []
        settings_ = settings.instance()
        new_lib_path = self._path_list.paths()
        old_lib_path = settings_['Python/library_path']

        if new_lib_path != self._initial_library:
            old_conflicts = sympathy.app.util.library_conflicts(
                sympathy.app.util.library_paths())
            settings_['Python/library_path'] = new_lib_path
            self._initial_library = new_lib_path
            new_conflicts = sympathy.app.util.library_conflicts(
                sympathy.app.util.library_paths())

            if sympathy.app.util.library_conflicts_worse(old_conflicts,
                                                         new_conflicts):
                settings_['Python/library_path'] = old_lib_path
                self._app_core.display_message(
                    sympathy.app.util.DisplayMessage(
                        title='Global Node Libraries',
                        brief=(
                            'Library change introduced new conflicts and was '
                            'therefore ignored. Using previous setting.')))
                return result

            set_recent_libs(self._path_list.recent())

            result.append(
                (A_LIBRARY_RELOAD,
                 self._app_core.reload_node_library))
            result.append(
                (A_LIBRARY_PATH,
                 self.library_path_changed.emit))
        self._initial_recent = get_recent_libs()
        return result


class GridLayout(QtWidgets.QGridLayout):

    def __init__(self, columnCount, parent=None):
        self._columns = columnCount
        super().__init__(parent)

    def addWidgetRow(self, widget):
        row = self.rowCount()
        self.addWidget(widget, row, 0, 1, self._columns)

    def addWidgetFormRow(self, label, widget):
        row = self.rowCount()
        label_widget = QtWidgets.QLabel(label)
        self.addWidget(label_widget, row, 0)
        self.addWidget(widget, row, 1)
        return label_widget

    def addStretch(self):
        self.setRowStretch(self.rowCount(), 1)


class PythonSectionWidget(PreferenceSectionWidget):
    """Settings concerning python"""

    _name = 'Python'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings_ = settings.instance()
        layout = GridLayout(2)
        self._packages_widget = package.PackagesWidget()
        self._customize_widget = package.InstallWidget()
        self._initial_python_path = []
        self._python_path_widget = sywidgets.PathListWidget(
            self._initial_python_path,
            root_path=settings_['install_folder'], parent=self)

        python_path_label = QtWidgets.QLabel('Python paths')
        packages_label = QtWidgets.QLabel('Packages')

        for label, value in [
                ('Interpreter', package.Python.executable),
                ('Version', package.Python.version),
                ('Architecture', package.Python.architecture),
        ]:
            widget = sywidgets.ReadOnlyLineEdit()
            widget.setText(value)
            layout.addWidgetFormRow(label, widget)

        layout.addWidgetRow(python_path_label)
        layout.addWidgetRow(self._python_path_widget)
        layout.addWidgetRow(packages_label)
        layout.addWidgetRow(self._packages_widget)
        layout.addWidgetRow(self._customize_widget)
        self.setLayout(layout)

        self._customize_widget.install_changed.connect(self._update_packages)
        self._packages_widget.selected_package.connect(
            self._customize_widget.set_package)
        self._packages_updated = False

    def update_data(self):
        settings_ = settings.instance()
        if not self._packages_updated:
            self._packages_updated = True
            self._packages_widget.update()

        self._python_path_widget.clear()
        self._initial_python_path = settings_['Python/python_path']
        self._python_path_widget.set_items(self._initial_python_path)

    def _update_packages(self):
        self._app_core.restart_workers()
        self._packages_widget.update()

    def save(self):
        result = []
        settings_ = settings.instance()
        python_path = self._python_path_widget.paths()

        if python_path != self._initial_python_path:
            settings_['Python/python_path'] = python_path
            self._initial_python_path = python_path
            result.append(
                (A_LIBRARY_RELOAD,
                 self._app_core.reload_node_library))
        return result


class SystemSectionWidget(PreferenceSectionWidget):
    """Settings concerning system"""

    _name = 'System'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = GridLayout(2)
        for label, value in [
                ('System', package.System.system),
                ('Machine', package.System.machine),
                ('Release', package.System.release),
                ('Version', package.System.version),
                ('System', package.System.processor),
        ]:
            widget = sywidgets.ReadOnlyLineEdit()
            widget.setText(value)
            layout.addWidgetFormRow(label, widget)

        layout.addStretch()
        self.setLayout(layout)


class ReadOnlyCheckBox(QtWidgets.QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def nextCheckState(self):
        pass


class CheckedBox(ReadOnlyCheckBox):
    def __init__(self, checked, text, parent=None):
        super().__init__(parent=parent)
        self.setChecked(checked)
        self.setText(text)


class PrivacySectionWidget(PreferenceSectionWidget):
    """Settings concerning privacy"""

    _name = 'Privacy'

    def _optional_information(self, setting, label, tooltip):
        widget = setwidgets.BoolCheckBox(setting)
        widget.setText(label)
        widget.setToolTip(tooltip)
        return widget

    def _system_information(self, setting):
        return self._optional_information(
            setting,
            'System',
            'System information consists of the data shown '
            'in the System section in Preferences')

    def _python_information(self, setting):
        return self._optional_information(
            setting,
            'Python',
            'Python information consists of Version and Architecture shown '
            'in the Python section in Preferences')

    def _package_information(self, setting):
        return self._optional_information(
            setting,
            'Packages',
            'Package information consists of the Packages shown '
            'in the Python section in Preferences')

    def _mandatory_information(self, label, tooltip):
        widget = CheckedBox(True, label)
        widget.setToolTip(tooltip)
        return widget

    def _sympathy_information(self):
        return self._mandatory_information(
            'Sympathy (required)',
            'Sympathy information consists of the version and edition '
            'shown in the About dialog')

    def _issue_information(self):
        return self._mandatory_information(
            'Help to improve Sympathy by sending issues (required)',
            'Issue information includes selected general information and '
            'specific information entered by the user: '
            'email, subject and description.')

    def _user_statistics(self, setting):
        return self._optional_information(
            setting,
            'Help to improve Sympathy by sharing anonymous user '
            'statistics',
            'Anonymous statistics includes selected general information '
            'and information about how Sympathy is run and the user actions '
            'performed,\nfor example, which nodes were created, and when.\n\n'

            'Anonymous statistics never include any identifiable '
            'information. More information about this feature can '
            'be found under "Privacy Notice" in the '
            'documentation.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = GridLayout(2)

        label = QtWidgets.QLabel(
            'Choose how to share data with Sympathy for Data.'
            '\n\n'
            'More information about anonymous user statistics can be found '
            'under "Privacy Notice" in the documentation.')
        label.setWordWrap(True)

        self._send_stats = self._user_statistics(settings.Keys.send_stats)
        layout.addWidgetRow(label)

        layout.addWidgetRow(self._send_stats)

        general_group = QtWidgets.QGroupBox(
            'General information')
        general_layout = QtWidgets.QVBoxLayout()
        general_group.setLayout(general_layout)
        general_label = sywidgets.ClickableHtmlLabel()
        general_label.setText(
            '<html><body>'
            'Additional information included in anonymous user '
            'statistics and issue reports. '
            'Click to show the <a href="#show-data">additional data</a> '
            'based on the current selection.'
            '</body></html>'
        )
        general_layout.addWidget(general_label)

        self._sympathy = self._sympathy_information()
        self._system = self._system_information(
            settings.Keys.collect_include_system)
        self._python = self._python_information(
            settings.Keys.collect_include_python)
        self._packages = self._package_information(
            settings.Keys.collect_include_packages)

        general_layout.addWidget(self._sympathy)
        general_layout.addWidget(self._system)
        general_layout.addWidget(self._python)
        general_layout.addWidget(self._packages)

        layout.addWidgetRow(general_group)

        layout.addStretch()
        self.setLayout(layout)

        general_label.linkActivated.connect(
            self._handle_general_label_activated)

    def _handle_general_label_activated(self, link):
        if link == '#show-data':
            self._show_data_dialog()

    def _show_data_dialog(self):
        data = package.Collect.to_dict(
            include_python=self._python.isChecked(),
            include_system=self._system.isChecked(),
            include_packages=self._packages.isChecked())
        data = package.Collect.pretty_dict(data)
        dialog = sympathy.app.package.JsonDialog(data, parent=self)
        dialog.setWindowTitle('Showing additional data')
        dialog.exec_()

    def _settings_widgets(self):
        return [
            self._send_stats,
            self._system,
            self._python,
            self._packages,
        ]

    def update_data(self):
        self._send_stats.update_value()
        self._system.update_value()
        self._python.update_value()
        self._packages.update_value()


class UserSectionWidget(PreferenceSectionWidget):
    """Settings concerning the user"""

    _name = 'User'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = GridLayout(2)

        self._email = setwidgets.EmailWidget()
        layout.addWidgetFormRow('Email', self._email)
        layout.addStretch()
        self.setLayout(layout)

    def _settings_widgets(self):
        return [
            self._email,
        ]


class MatlabSectionWidget(PreferenceSectionWidget):
    """Settings concerning MATLAB"""

    _name = 'Matlab'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path_line = setwidgets.StringLineEdit('MATLAB/matlab_path')
        self._path_button = QtWidgets.QPushButton('...')
        self._jvm_checkbox = setwidgets.BoolCheckBox('MATLAB/matlab_jvm')
        self._layout = self._create_layout()
        path_widget = QtWidgets.QHBoxLayout()
        path_widget.addWidget(self._path_line)
        path_widget.addWidget(self._path_button)
        self._layout.addRow(
            self._centered_label('MATLAB path'), path_widget)
        self._layout.addRow('Disable JVM', self._jvm_checkbox)
        self.setLayout(self._layout)

        self._path_button.clicked.connect(self._get_path)

    def _get_path(self):
        default_directory = self._path_line.text()
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select MATLAB executable', default_directory)[0]
        if len(path):
            self._path_line.setText(path)

    def _settings_widgets(self):
        return [
            self._path_line,
            self._jvm_checkbox,
        ]

    def save(self):
        value_changed = any(
            w.dirty() for w in [self._path_line, self._jvm_checkbox])

        result = super().save()

        if value_changed:
            result.append(
                (A_LIBRARY_RELOAD,
                 self._app_core.reload_node_library))
        return result


class ModifyEnvironmentWidget(QtWidgets.QWidget):
    valueChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._table_view = QtWidgets.QTableView()
        self._table_model = symodels.KeyDictTableModel(
            horizontal_headers=['Name', 'Value'])

        self._table_view.setModel(self._table_model)
        self._unique_delegate = UniqueItemDelegate(self._table_view)

        self._table_view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)

        self._toolbar_widget = sympathy.app.actions.table_container_toolbar(
            self._table_view, self)

        self._table_view.setItemDelegateForColumn(
            0, self._unique_delegate)

        self._vlayout = QtWidgets.QVBoxLayout()
        self._vlayout.setContentsMargins(0, 0, 0, 0)
        self._vlayout.setSpacing(5)

        self._vlayout.addWidget(self._toolbar_widget)
        self._vlayout.addWidget(self._table_view)
        self.setLayout(self._vlayout)

    def variables(self):
        return {k: v for k, v in self._table_model.to_list() if k}

    def set_variables(self, data: Dict[str, str]):
        self._table_model.clear()
        self._table_model.from_list(data.items())


class EnvironmentSectionWidget(PreferenceSectionWidget):
    """Settings concerning environment variables."""

    _name = 'Environment'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._layout = self._create_layout()
        self._global_env_widget = ModifyEnvironmentWidget()
        self._global_env_widget.setMaximumHeight(300)
        self._textedit = QtWidgets.QTextEdit()
        self._table_widget = QtWidgets.QTableWidget()
        self._table_widget.setColumnCount(2)
        self._table_widget.setHorizontalHeaderLabels(['Name', 'Value'])
        self._table_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)

        self._update_table(ENV.shell_variables())

        self._layout.addRow(QtWidgets.QLabel('Global variables'))
        self._layout.addRow(self._global_env_widget)
        self._layout.addRow(QtWidgets.QLabel('Environment variables'))
        self._layout.addRow(self._table_widget)
        self.setLayout(self._layout)

    def save(self):
        result = []
        settings_ = settings.instance()
        global_env_vars = self._global_env_widget.variables()
        values = []
        for name, value in global_env_vars.items():
            values.append('{}={}'.format(name, value))
        ENV.set_global_variables(global_env_vars)
        settings_['environment'] = values
        return result

    def update_data(self):
        settings_ = settings.instance()
        env_vars = settings_['environment']
        self._global_env_widget.set_variables(
            dict([env_var.split('=', 1) for env_var in env_vars]))

    @QtCore.Slot(dict)
    def _update_table(self, env_variables):
        self._table_widget.setRowCount(len(env_variables))

        for row, (name, value) in enumerate(env_variables.items()):
            name_item = QtWidgets.QTableWidgetItem(name)
            value_item = QtWidgets.QTableWidgetItem(value)
            name_item.setFlags(QtCore.Qt.NoItemFlags)
            value_item.setFlags(QtCore.Qt.NoItemFlags)
            self._table_widget.setItem(row, 0, name_item)
            self._table_widget.setItem(row, 1, value_item)
        self._table_widget.sortItems(0)


class DebugSectionWidget(PreferenceSectionWidget):
    """Settings concerning debugging and profiling."""

    profile_path_types = ['Session folder', 'Workflow folder']

    _name = 'Debug'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dot_in_path = distutils.spawn.find_executable(vs.str_('dot'))

        def graphviz_path_dialog():
            default_directory = self._graphviz_path.text()
            dir_ = QtWidgets.QFileDialog.getExistingDirectory(
                self, 'Locate Graphviz directory containing dot',
                default_directory)
            if dir_:
                self._graphviz_path.setText(dir_)
                test_graphviz_path()

        def test_graphviz_path():
            gviz_path = self._graphviz_path.text()
            dot = distutils.spawn.find_executable(vs.str_('dot'), gviz_path)
            if dot:
                self._graphviz_status.setText("Graphviz found!")
                self._graphviz_status.setStyleSheet("QLabel { color: green; }")
            elif self._dot_in_path:
                self._graphviz_status.setText("Graphviz found in PATH!")
                self._graphviz_status.setStyleSheet("QLabel { color: green; }")
            else:
                self._graphviz_status.setText("Graphviz not found!")
                self._graphviz_status.setStyleSheet("QLabel { color: red; }")

        self._profile_path_type = setwidgets.StringComboBox(
            'Debug/profile_path_type', self.profile_path_types)

        gviz_path_layout = QtWidgets.QHBoxLayout()
        self._graphviz_path = setwidgets.StringLineEdit('Debug/graphviz_path')
        file_button = QtWidgets.QPushButton('...')
        gviz_path_layout.addWidget(self._graphviz_path)
        gviz_path_layout.addWidget(file_button)

        self._graphviz_status = QtWidgets.QLabel()

        self._layout = self._create_layout()
        self._layout.addRow('Store profiling data in', self._profile_path_type)
        self._layout.addRow(
            self._centered_label('Graphviz install path'),
            gviz_path_layout)
        self._layout.addRow('', self._graphviz_status)
        self.setLayout(self._layout)

        self._graphviz_path.textEdited.connect(test_graphviz_path)
        file_button.clicked.connect(graphviz_path_dialog)

        test_graphviz_path()

    def _settings_widgets(self):
        return [
            self._profile_path_type,
            self._graphviz_path,
        ]


class TempFilesSectionWidget(PreferenceSectionWidget):
    """Temporary session files settings"""

    _name = 'Temporary Files'
    _apply_order = 10000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings_ = settings.instance()
        self._layout = self._create_layout()
        self._init_sessions_folder(settings_)

    def _init_sessions_folder(self, settings_):
        self._path_layout = QtWidgets.QHBoxLayout()
        self._sessions_folder = setwidgets.StringLineEdit('temp_folder')
        self._sessions_folder.setToolTip(
            'Path to the folder where temporary files will be stored, the '
            'folder must exist and should be writable.\nChanges to this '
            'setting requires the application to be restarted afterwards.')

        self._path_layout.addWidget(self._sessions_folder)

        self._file_button = QtWidgets.QPushButton('...')
        self._file_button.clicked.connect(self._open_sessions_folder_dialog)
        self._path_layout.addWidget(self._file_button)

        self._default_button = QtWidgets.QPushButton('Default')
        self._default_button.setToolTip(
            'Restore Temporary files path to its default value.')
        self._default_button.clicked.connect(self._use_default_folder)
        self._path_layout.addWidget(self._default_button)

        if settings_.sessions_folder_override:
            self._file_button.setDisabled(True)
            self._sessions_folder.setDisabled(True)
            self._sessions_folder.setToolTip(
                settings_.sessions_folder_override_description)

        self._layout.addRow(
            self._centered_label('Temporary files path'),
            self._path_layout)

        self._session_files = setwidgets.StringComboBox(
            'session_temp_files',
            settings.session_temp_files_choice)

        self._layout.addRow(
            'Handling of session files',
            self._session_files)

        limits_group = QtWidgets.QGroupBox()
        limits_layout = self._create_layout()

        self._temp_age = setwidgets.IntegerSpinBox('max_temp_folder_age')
        self._temp_age.setMaximum(999999)
        limits_layout.addRow(
            'Age of temporary files (days)', self._temp_age)

        self._temp_size = setwidgets.StringLineEdit('max_temp_folder_size')
        self._temp_size.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self._temp_size.setMaximumSize(QtCore.QSize(70, 25))
        limits_layout.addRow(
            'Size of temporary files (x k/M/G)', self._temp_size)

        self._temp_number = setwidgets.IntegerSpinBox('max_temp_folder_number')
        self._temp_number.setMaximum(999999)
        limits_layout.addRow(
            'Number of session folders',
            self._temp_number)
        self._session_files.currentIndexChanged.connect(
            limits_group.setDisabled)

        limits_group.setLayout(limits_layout)
        self._layout.addRow('Limits for keeping session files', limits_group)
        limits_group.setDisabled(self._session_files.currentIndex())

        self.setLayout(self._layout)

    @QtCore.Slot()
    def _open_sessions_folder_dialog(self):
        default_directory = self._sessions_folder.text()
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Locate a directory for temporary files',
            default_directory)
        if len(dir_) > 0:
            self._sessions_folder.setText(dir_)

    def _use_default_folder(self):
        self._sessions_folder.setText(
            settings.instance().default_sessions_folder)

    def _settings_widgets(self):
        return [
            self._sessions_folder,
            self._session_files,
            self._temp_age,
            self._temp_size,
            self._temp_number,
        ]


class AdvancedSectionWidget(PreferenceSectionWidget):
    """Advanced settings"""

    _name = 'Advanced'
    _apply_order = 10000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._layout = self._create_layout()

        self._nbr_of_threads = setwidgets.IntegerSpinBox('max_nbr_of_threads')
        self._nbr_of_threads.setMaximum(999)

        self._char_limit = setwidgets.IntegerSpinBox('max_task_chars')
        self._char_limit.setMaximum(2**31 - 1)  # Max 32 bit signed int.

        self._deprecated_warning = setwidgets.BoolCheckBox(
            'deprecated_warning')

        # TODO: refactor! These are not settings just buttons that rely on
        # temporary settings to propagate value.
        self._clear_settings = QtWidgets.QCheckBox()
        self._clear_caches = QtWidgets.QCheckBox()

        self._show_experimental = setwidgets.BoolCheckBox('Gui/experimental')

        clear_layout = QtWidgets.QGridLayout()
        clear_layout.addWidget(QtWidgets.QLabel('Caches'), 0, 0)
        clear_layout.addWidget(self._clear_caches, 1, 0,
                               QtCore.Qt.AlignHCenter)
        clear_layout.addWidget(QtWidgets.QLabel('Settings'), 0, 1)
        clear_layout.addWidget(
            self._clear_settings, 1, 1, QtCore.Qt.AlignHCenter)
        clear_layout.setHorizontalSpacing(10)
        clear_layout.setVerticalSpacing(2)

        self._layout.addRow(
            'Number of worker processes (0 = automatic)\n'
            'Sympathy has to be restarted to apply this setting.',
            self._nbr_of_threads)

        self._layout.addRow(
            'Node output character limit (0 = unlimited)',
            self._char_limit)

        self._layout.addRow(
            'Display warnings for deprecated nodes',
            self._deprecated_warning)
        self._layout.addRow(
            'Reset on next close:\n'
            'CAUTION! This may affect all open instances of Sympathy',
            clear_layout)
        self._layout.addRow(
            'Show experimental options\n'
            'Sympathy has to be restarted to apply this setting',
            self._show_experimental)

        self.setLayout(self._layout)

    def _settings_widgets(self):
        return [
            self._nbr_of_threads,
            self._deprecated_warning,
            self._char_limit,
            self._show_experimental,
        ]

    def save(self):
        settings_ = settings.instance()
        result = super().save()
        settings_['clear_settings'] = self._clear_settings.isChecked()
        settings_['clear_caches'] = self._clear_caches.isChecked()
        return result

    def update_data(self):
        super().update_data()
        settings_ = settings.instance()
        self._clear_settings.setChecked(settings_.get('clear_settings', False))
        self._clear_caches.setChecked(settings_.get('clear_caches', False))


class LibraryViewSectionWidget(PreferenceSectionWidget):
    """Library view settings"""

    library_separated_changed = QtCore.Signal(bool)
    library_show_hidden_changed = QtCore.Signal()
    library_highlighter_changed = QtCore.Signal(tuple)

    _name = 'Library View'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings_ = settings.instance()

        self._layout = self._create_layout()
        self._init_gui_settings(settings_)

    def _init_gui_settings(self, settings_):
        self._library_separated = setwidgets.BoolCheckBox(
            'Gui/library_separated')

        self._show_hidden = setwidgets.BoolCheckBox(
            'Gui/library_show_hidden')

        self._library_matcher_type = setwidgets.StringComboBox(
            'Gui/library_matcher_type', ['character', 'word'])

        self._library_highlighter_type = setwidgets.StringComboBox(
            'Gui/library_highlighter_type',
            ['color', 'background-color', 'font-weight'])

        self._library_highlighter_color = setwidgets.StringLineEdit(
            'Gui/library_highlighter_color')
        self._library_highlighter_color.setFixedWidth(100)

        self._color_button = QtWidgets.QPushButton('...')
        self._color_button.clicked.connect(self._set_color)

        color_layout = QtWidgets.QHBoxLayout()
        color_layout.addWidget(self._library_highlighter_color)
        color_layout.addWidget(self._color_button)
        self._color_button.setFixedWidth(55)

        self._quickview_popup_position = setwidgets.StringComboBox(
            'Gui/quickview_popup_position',
            ['left', 'center', 'right'])

        self._layout.addRow(
            'Separate each node library', self._library_separated)
        self._layout.addRow('Show hidden nodes', self._show_hidden)

        if settings_['Gui/experimental']:
            self._layout.addRow(
                'Highlighter (EXPERIMENTAL!)', self._library_matcher_type)
            self._layout.addRow(
                'Highlighter type (EXPERIMENTAL!)',
                self._library_highlighter_type)
            self._layout.addRow(
                'Highlighter color (EXPERIMENTAL!)', color_layout)
        self._layout.addRow('Popup position', self._quickview_popup_position)

        self.setLayout(self._layout)

        self._library_highlighter_type.currentIndexChanged.connect(
            self._disable_colorfield)
        self._disable_colorfield()

    def _disable_colorfield(self):
        if self._library_highlighter_type.currentText() == 'font-weight':
            self._library_highlighter_color.setDisabled(True)
            self._color_button.setDisabled(True)
        else:
            self._library_highlighter_color.setDisabled(False)
            self._color_button.setDisabled(False)

    def _set_color(self):
        picker = QtWidgets.QColorDialog()
        res = picker.exec_()
        if res == QtWidgets.QDialog.Accepted:
            self._library_highlighter_color.setText(
                picker.currentColor().name().upper())

    def _settings_widgets(self):
        return [
            self._library_separated,
            self._show_hidden,
            self._library_highlighter_type,
            self._library_highlighter_color,
            self._library_matcher_type,
            self._quickview_popup_position,
        ]

    def save(self):
        separated_changed = self._library_separated.dirty()
        show_hidden_changed = self._show_hidden.dirty()
        highlighter_type_changed = self._library_highlighter_type.dirty()
        highlighter_color_changed = self._library_highlighter_color.dirty()
        matcher_type_changed = self._library_matcher_type.dirty()

        result = super().save()

        if separated_changed:
            result.append(
                (A_LIBRARY_TYPE,
                 lambda:
                 self.library_separated_changed.emit(
                     self._library_separated.editor_value())))

        if show_hidden_changed:
            result.append(
                (A_LIBRARY_TYPE,
                 lambda: self.library_show_hidden_changed.emit()))

        if (highlighter_type_changed or highlighter_color_changed or
                matcher_type_changed):
            result.append(
                (A_LIBRARY_HIGHLIGHTER,
                 lambda: self.library_highlighter_changed.emit((
                     self._library_matcher_type.editor_value(),
                     self._library_highlighter_type.editor_value(),
                     self._library_highlighter_color.editor_value()
                 ))))

        return result
