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
"""Main window (menu bar, dock widgets)"""
import os
import functools

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

from . import flow
from . windows import flow_window
from . windows import messages_window
from . windows import control_panel
from . windows import flow_overview
from . windows import about_window
from . windows import library_view
from . windows import preferences
from . windows import issues
from . import settings
from . credentials import credentials
from . import signals
from . wizards import nodewizard
from . wizards import functionwizard
from . wizards import librarywizard
from . import common
from . import version
from . import keymaps
from . import themes
from . import util
from . import gui_manager
from . import user_statistics
from sympathy.app.environment_variables import instance as env_instance
from sympathy.utils import prim
from sympathy.platform import exceptions
from sympathy.platform import os_support as oss
import sympathy.platform.feature
from sympathy.platform.hooks import request_http


class FlowTabWidget(QtWidgets.QTabWidget):
    """Keeper of flow tabs."""

    flow_deleted = QtCore.Signal(flow.Flow)
    current_flow_changed = QtCore.Signal(flow_window.FlowWindow)

    def __init__(self, parent=None):
        super(FlowTabWidget, self).__init__(parent)
        self._signals = signals.SignalHandler()
        self.setTabBar(MainTabBar())
        self.tabBar().tabCloseRequested[int].connect(self.close_tab)
        self.tabBar().currentChanged[int].connect(self.change_tab)
        self.setMovable(True)
        self.setTabsClosable(True)
        self._flow_windows = {}

    def get_flows(self):
        return [self.widget(index).flow() for index in range(self.count())]

    def get_current_flow(self):
        current_widget = self.currentWidget()
        if not current_widget:
            return None
        else:
            return current_widget.flow()

    def close_flow_tab(self, flow_):
        """Close tab with given flow"""
        self._signals.disconnect_all(flow_)
        flow_window_ = self._flow_windows.get(flow_)
        del self._flow_windows[flow_]
        if flow_window_:
            index = self.indexOf(flow_window_)
            flow_window_.close_flow_view()
            self.removeTab(index)
        self.update_flow_labels()

    def open_flow_window_tab(self, flow_window_):
        """Add a new tab"""
        flow_ = flow_window_.flow()
        self._flow_windows[flow_] = flow_window_
        index = self.addTab(flow_window_, '')
        self.tabBar().set_tab_color(index, flow_window_.color)
        self.update_flow_labels()

    @QtCore.Slot(int)
    def close_tab(self, tab_index):
        """Close tab with index"""
        flow_window_ = self.widget(tab_index)
        return flow_window_.close_flow()

    @QtCore.Slot(int)
    def change_tab(self, index):
        """Bring tab #index to front"""
        self.current_flow_changed.emit(self.widget(index))

    def show_flow(self, flow_):
        """Bring tab with flow to front"""
        flow_window_ = self._flow_windows.get(flow_)
        if flow_window_:
            index = self.indexOf(flow_window_)
            self.setCurrentIndex(index)

    def update_flow_labels(self):
        """
        Update tab labels for all flows.

        Doing this in one sweep for all flows makes it easier to add
        distinguishing parts.
        """
        def get_distinguishing_parts(name_tuple, all_name_tuples):
            same_shortname_tuples = [
                t for t in all_name_tuples if t[-1] == name_tuple[-1]]
            same_shortname_tuples.remove(name_tuple)  # Remove the current flow

            distinguishing_parts = []
            for pos, part in enumerate(name_tuple):
                other_parts = []
                for same_shortname_tuple in same_shortname_tuples:
                    try:
                        other_parts.append(same_shortname_tuple[pos])
                    except IndexError:
                        # Can happen if same_shortname_tuple is shorter than
                        # name_tuple.
                        other_parts.append(None)

                same_parts = [other_part == part for other_part in other_parts]
                if not all(same_parts):
                    # Since this part differs for some of the flows, it can be
                    # used to distinguish between them.
                    distinguishing_parts.append(part)

                    # Any subflows that differ for this part have now been
                    # distinguished, so we can remove them from further
                    # consideration.
                    same_shortname_tuples = [
                        t for i, t in enumerate(same_shortname_tuples)
                        if same_parts[i]]
            return distinguishing_parts

        flows = [self.widget(i).flow() for i in range(self.count())]
        flow_name_tuples = [f.full_display_name_tuple for f in flows]

        for name_tuple, flow_ in zip(flow_name_tuples, flows):
            distinguishing_parts = get_distinguishing_parts(
                name_tuple, flow_name_tuples)
            flow_dirty = not flow_.is_clean()
            subflows_dirty = not flow_.subflows_are_clean()

            # Tab label
            label = name_tuple[-1]
            if distinguishing_parts:
                label += " <{}>".format("/".join(distinguishing_parts))
            if flow_dirty or subflows_dirty:
                label += "*"
            flow_window = self._flow_windows[flow_]
            tab_index = self.indexOf(flow_window)
            self.setTabText(tab_index, label)

            # Tab tooltip
            tooltip_parts = [" -> ".join(name_tuple), ""]
            filename = flow_.root_or_linked_flow_filename
            if filename:
                tooltip_parts.append("Saved in {}".format(filename))
            else:
                tooltip_parts.append("Not yet saved")
            if flow_dirty:
                tooltip_parts.append("There are unsaved changes in this flow.")
            elif subflows_dirty:
                tooltip_parts.append("There are unsaved changes in some "
                                     "linked subflows.")
            # # TODO(magnus): Useful debug info, but needs to be updated
            # # whenever flow state or clean state changes.
            # settings_ = settings.instance()
            # if settings_['Gui/platform_developer']:
            #     tooltip_parts.append("")
            #     tooltip_parts.append(flow_.undo_stack().flow_debug_str(flow_))
            self.setTabToolTip(tab_index, "\n".join(tooltip_parts))

    def preferences_updated(self):
        for flow_window_ in self._flow_windows.values():
            flow_window_.preferences_updated()


class MainTabBar(QtWidgets.QTabBar):
    """TabBar which closes a tab if it is clicked with middle mouse button."""

    def __init__(self):
        super().__init__()
        self._tab_being_clicked = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            self._tab_being_clicked = self.tabAt(event.pos())
            event.accept()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            if self.tabAt(event.pos()) == self._tab_being_clicked:
                self.tabCloseRequested.emit(self._tab_being_clicked)
            self._tab_being_clicked = None
            event.accept()
        return super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Add colored lines under tabs."""
        super().paintEvent(event)
        if self._color_count() >= 2:
            painter = QtGui.QPainter(self)
            theme_colors = themes.get_active_theme().project_colors()
            for i in range(self.count()):
                color_id = self.tabData(i)
                if color_id is None:
                    continue
                color = theme_colors[color_id]
                tab_rect = self.tabRect(i)
                tab_rect.adjust(0.15*tab_rect.width(), 0,
                                -0.15*tab_rect.width(), -1)
                tab_rect.setTop(tab_rect.bottom() - 1)
                painter.fillRect(tab_rect, color)

    def _color_count(self):
        """Return the number of unique colors currently in use."""
        colors = set()
        for index in range(self.count()):
            colors.add(self.tabData(index))
        return len(colors)

    def set_tab_color(self, tab_index, color):
        self.setTabData(tab_index, color)


class MenuManager(QtCore.QObject):
    """Manages the main menu bar."""

    new_flow = QtCore.Signal()
    new_node = QtCore.Signal()
    new_function = QtCore.Signal()
    new_library = QtCore.Signal()
    open_flow = QtCore.Signal()
    open_named_flow = QtCore.Signal(str)
    reload_library = QtCore.Signal()
    open_preferences = QtCore.Signal()
    quit_application = QtCore.Signal()
    find_nodes = QtCore.Signal()
    toggle_grid = QtCore.Signal(bool)
    about_sympathy = QtCore.Signal()
    user_documentation = QtCore.Signal()
    privacy_notice = QtCore.Signal()
    node_library = QtCore.Signal()
    create_documentation = QtCore.Signal()
    report_issue = QtCore.Signal()

    def __init__(self, main_window, parent=None):
        super(MenuManager, self).__init__(parent)
        self._main_window = main_window
        self._control_panel = main_window._control_panel
        self._platform_is_mac = prim.is_osx()
        self._init()

    def _create_action(self, name, signal, icon=None, shortcut=None):
        action = QtWidgets.QAction(name, self)
        action.triggered.connect(signal)
        if icon:
            action.setIcon(QtGui.QIcon(icon))
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def _init(self):
        self._menu_bar = None
        self._window_file_menu_actions = []
        self._window_edit_menu_actions = []
        self._window_control_menu_actions = []
        self._window_view_menu_actions = []
        self._window_view_extra_menu_actions = []
        keymap = keymaps.get_active_keymap()
        theme = themes.get_active_theme()

        self._new_flow = self._create_action(
            '&New Flow', self.new_flow, theme.new_flow, keymap.new_flow)

        self._new_library = self._create_action(
            'New Library', self.new_library)
        self._new_library.setEnabled(True)

        self._new_node = self._create_action(
            'New Node', self.new_node)
        self._new_node.setEnabled(True)

        self._new_function = self._create_action(
            'New Function', self.new_function)
        self._new_function.setEnabled(True)

        self._open_flow = self._create_action(
            '&Open...',
            self.open_flow,
            theme.open_flow,
            keymap.open_flow)

        self._control_panel.new_signal.connect(self.new_flow)
        self._control_panel.open_signal.connect(self.open_flow)
        self._control_panel.set_current_flow(None)

        self._reload_library = self._create_action(
            'Reload &Library', self.reload_library,
            shortcut=keymap.reload_library)

        self._preferences = self._create_action(
            '&Preferences', self.open_preferences,
            theme.preferences,
            shortcut=keymap.preferences)
        self._preferences.setMenuRole(QtWidgets.QAction.PreferencesRole)

        if self._platform_is_mac:
            quit_menu_item_text = 'Quit'
            about_menu_item_text = 'About'
        else:
            quit_menu_item_text = '&Quit'
            about_menu_item_text = '&About'
        self._quit = self._create_action(
            quit_menu_item_text, self.quit_application,
            theme.quit, keymap.quit)
        self._quit.setMenuRole(QtWidgets.QAction.QuitRole)

        self._privacy_notice = self._create_action(
            'Privacy Notice', self.privacy_notice)

        self._find_nodes = self._create_action(
            '&Find',
            self.find_nodes,
            theme.find,
            keymap.find_node)

        self._toggle_grid = self._create_action(
            '&Grid',
            self.toggle_grid,
            theme.grid,
            keymap.toggle_grid)
        self._toggle_grid.setCheckable(True)

        self._about = self._create_action(about_menu_item_text,
                                          self.about_sympathy)
        self._about.setMenuRole(QtWidgets.QAction.AboutRole)
        self._user_documentation = self._create_action(
            '&User Manual', self.user_documentation, theme.help)

        self._create_documentation = self._create_action(
            '&Create Documentation', self.create_documentation)

        self._report_issue = self._create_action(
            'Report Issue', self.report_issue, theme.report_issue)

    def _add_actions_from_list(self, menu, action_list):
        for action in action_list:
            if action:
                menu.addAction(action)
            else:
                menu.addSeparator()

    def _update_file_menu(self):
        file_menu = self._menu_bar.addMenu('&File')
        file_menu.addAction(self._new_flow)
        file_menu.addAction(self._open_flow)
        recent_flows_menu = file_menu.addMenu('Open &Recent')
        for (idx, flow_name) in enumerate(
                settings.instance()['Gui/recent_flows']):
            action = QtWidgets.QAction('&{}: {}'.format(idx + 1, flow_name),
                                       self)
            action.triggered.connect(
                functools.partial(self.open_named_flow.emit, flow_name))
            recent_flows_menu.addAction(action)

        self._add_actions_from_list(file_menu, self._window_file_menu_actions)
        file_menu.addSeparator()
        wizard_menu = file_menu.addMenu('Wizards')
        wizard_menu.addAction(self._new_library)
        wizard_menu.addAction(self._new_node)
        wizard_menu.addAction(self._new_function)

        file_menu.addSeparator()
        file_menu.addAction(self._preferences)

        file_menu.addSeparator()
        file_menu.addAction(self._quit)
        self._menu_bar.addMenu(file_menu)

    def _update_edit_menu(self):
        edit_menu = self._menu_bar.addMenu('&Edit')
        edit_menu.addAction(self._main_window.undo_action)
        edit_menu.addAction(self._main_window.redo_action)
        if self._window_edit_menu_actions:
            self._add_actions_from_list(
                edit_menu, self._window_edit_menu_actions)
            edit_menu.addSeparator()
            edit_menu.addAction(self._find_nodes)
            self._menu_bar.addMenu(edit_menu)

    def _update_control_menu(self):
        if self._window_control_menu_actions:
            control_menu = self._menu_bar.addMenu('&Control')
            self._add_actions_from_list(
                control_menu, self._window_control_menu_actions)
            self._menu_bar.addMenu(control_menu)

            control_menu.addSeparator()
            control_menu.addAction(self._reload_library)

    def _update_view_menu(self):
        view_menu = self._menu_bar.addMenu('&View')
        self._add_actions_from_list(
            view_menu, self._window_view_extra_menu_actions +
            self._window_view_menu_actions)
        self._menu_bar.addMenu(view_menu)
        view_menu.addSeparator()
        view_menu.addAction(self._toggle_grid)
        view_menu.addAction(self._main_window.fullscreen_toggle)

    def _update_help_menu(self):
        help_menu = self._menu_bar.addMenu('&Help')
        help_menu.addAction(self._user_documentation)
        # help_menu.addAction(self._node_library)
        ex_menu = help_menu.addMenu('Examples flows')
        for lib_name, examples_path in self._main_window.get_examples_paths():
            if lib_name is None:
                ex_menu.addSeparator()
            else:
                action = QtWidgets.QAction(lib_name, self)
                action.triggered.connect(functools.partial(
                    self._open_example_folder, examples_path))
                ex_menu.addAction(action)

        # help_menu.addAction(self._create_documentation)
        help_menu.addSeparator()
        help_menu.addAction(self._about)
        help_menu.addAction(self._privacy_notice)
        self._menu_bar.addMenu(help_menu)
        help_menu.addSeparator()
        help_menu.addAction(self._report_issue)

    def _open_example_folder(self, examples_path):
        if not oss.open_directory(examples_path):
            msg = 'The examples path "{}" seem to be missing.'.format(
                examples_path)
            QtWidgets.QMessageBox.information(
                self._main_window, "This library has no examples", msg)
            exceptions.sywarn(msg)

    def update_menus(self):
        self._menu_bar = self._main_window.menuBar()
        self._menu_bar.clear()
        self._update_file_menu()
        self._update_edit_menu()
        self._update_control_menu()
        self._update_view_menu()
        self._update_help_menu()

    def set_window_menus(self, flow_window_):
        self._window_file_menu_actions = []
        self._window_edit_menu_actions = []
        self._window_control_menu_actions = []
        self._window_view_menu_actions = []

        if flow_window_:
            self._window_file_menu_actions = (
                self._control_panel.file_menu_actions())

            self._window_edit_menu_actions = flow_window_.edit_menu_actions()
            self._window_edit_menu_actions.extend(
                self._control_panel.edit_menu_actions())

            self._window_control_menu_actions = (
                self._control_panel.control_menu_actions())

            self._window_view_menu_actions = flow_window_.view_menu_actions()
            self._window_view_menu_actions.extend(
                self._control_panel.view_menu_actions())

        self._control_panel.set_current_flow(flow_window_)

        self.update_menus()

    def set_window_view_extra_menu_actions(self, view_menu_actions):
        self._window_view_extra_menu_actions = view_menu_actions
        self.update_menus()

    def preferences_updated(self):
        self._toggle_grid.setChecked(settings.instance()['Gui/snap_enabled'])


class MainWindow(QtWidgets.QMainWindow):
    """Main window."""

    new_flow = QtCore.Signal()
    open_flow = QtCore.Signal(str)
    open_named_flow = QtCore.Signal(str)
    open_flow_window = QtCore.Signal(flow.Flow)
    closed = QtCore.Signal()

    def __init__(self, app_core, args, splash, parent=None):
        splash.showMessage("Building main window...")
        super(MainWindow, self).__init__(parent)
        self._app_core = app_core
        self._args = args
        self._wd = os.getcwd()
        self._scratch_uuid = None
        self._init()
        self._init_flow_overview()
        self._init_error_view()
        splash.showMessage("Loading node library...")
        app_core.reload_node_library()
        splash.showMessage("Building main window...")
        self._init_library_view()
        self._init_undo_view()

        theme = themes.get_active_theme()
        keymap = keymaps.get_active_keymap()
        self.fullscreen_toggle = QtWidgets.QAction(
            'Toggle &Fullscreen', self)
        self.fullscreen_toggle.triggered.connect(self._toggle_fullscreen)
        self.fullscreen_toggle.setIcon(QtGui.QIcon(theme.fullscreen))
        self.fullscreen_toggle.setShortcut(keymap.fullscreen)
        self.fullscreen_toggle.setCheckable(True)
        self._init_menu_manager()

        library_toggle_action = self._library_dock.toggleViewAction()
        library_toggle_action.setText("&Library")
        error_toggle_action = self._error_dock.toggleViewAction()
        error_toggle_action.setText("&Messages")
        flow_overview_toggle_action = (
            self._flow_overview_dock.toggleViewAction())
        flow_overview_toggle_action.setText("&Flow overview")
        undo_view_toggle_action = self._undo_dock.toggleViewAction()
        undo_view_toggle_action.setText("&Undo stack")

        self._menu_manager.set_window_view_extra_menu_actions(
            [library_toggle_action, flow_overview_toggle_action,
             error_toggle_action, undo_view_toggle_action])
        self._docs_builder_view = None
        self._has_quit = False
        self._set_docking_state()

        settings_ = settings.instance()
        if 'Gui/geometry' in settings_:
            self.restoreGeometry(settings_['Gui/geometry'])
        if 'Gui/window_state' in settings_:
            self.restoreState(settings_['Gui/window_state'])
        self.fullscreen_toggle.setChecked(
            self.windowState() & QtCore.Qt.WindowFullScreen)
        if 'environment' in settings_:
            env = env_instance()
            env_vars = settings_['environment']
            env_dict = {}
            for env_var in env_vars:
                name, value = env_var.split('=', 1)
                env_dict[name] = value
            env.global_variables().update(env_dict)
        self._gui_manager = gui_manager.GuiManager(self, app_core)

    def _init(self):
        self.setWindowTitle(version.window_title())
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._control_panel = control_panel.ControlPanel(self)
        self._control_panel.setObjectName('Gui::MainWindow::ControlPanel')
        self.addToolBar(QtCore.Qt.TopToolBarArea, self._control_panel)
        self._tab_widget = FlowTabWidget(parent=self)
        self._tab_widget.current_flow_changed.connect(
            self.current_flow_changed)

        self.setCentralWidget(self._tab_widget)
        self.setAcceptDrops(True)
        self.setGeometry(QtCore.QRect(10, 10, 800, 600))

        self._menu_manager = MenuManager(self, parent=self)

        general_settings_widget = preferences.GeneralSectionWidget(
            self._menu_manager,
            self._app_core)

        library_view_widget = preferences.LibraryViewSectionWidget(
            self._app_core)
        self._library_separated_changed = (
            library_view_widget.library_separated_changed)
        self._library_show_hidden_changed = (
            library_view_widget.library_show_hidden_changed)
        self._library_highlighter_changed = (
            library_view_widget.library_highlighter_changed)

        libraries_settings_widget = preferences.LibrariesSectionWidget(
            self._app_core)

        self._preference_dialog = None
        self._preference_widgets = [
            general_settings_widget,
            preferences.NodeConfigsSectionWidget(self._app_core),
            library_view_widget,
            libraries_settings_widget,
            preferences.PythonSectionWidget(self._app_core),
            preferences.SystemSectionWidget(self._app_core),
            preferences.PrivacySectionWidget(self._app_core),
            preferences.UserSectionWidget(self._app_core),
            preferences.MatlabSectionWidget(self._app_core),
            preferences.EnvironmentSectionWidget(self._app_core),
            credentials.CredentialSectionWidget(self._app_core),
            preferences.DebugSectionWidget(self._app_core),
            preferences.TempFilesSectionWidget(self._app_core),
            preferences.AdvancedSectionWidget(self._app_core)]

        for f in sympathy.platform.feature.available_features():
            fm = f.manager()
            self._preference_widgets.extend(
                fm.preference_sections())

        libraries_settings_widget.library_path_changed.connect(
            self._global_library_path_changed)
        self._app_core.help_requested.connect(self.open_documentation)

    def _toggle_fullscreen(self):
        if self.windowState() & QtCore.Qt.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()

    def _toggle_grid(self):
        settings_ = settings.instance()
        settings_['Gui/snap_enabled'] = not settings_['Gui/snap_enabled']
        self._preferences_updated()

    def _init_menu_manager(self):
        self._menu_manager.update_menus()
        self._menu_manager.new_flow.connect(self.new_flow)
        self._menu_manager.new_node.connect(self._show_nodewizard)
        self._menu_manager.new_function.connect(self._show_functionwizard)
        self._menu_manager.new_library.connect(self._show_librarywizard)
        self._menu_manager.open_flow.connect(self._handle_open_flow)
        self._menu_manager.open_named_flow.connect(self.open_named_flow)
        self._menu_manager.reload_library.connect(self.reload_library)
        self._menu_manager.open_preferences.connect(self.show_preferences)
        self._menu_manager.toggle_grid.connect(self._toggle_grid)
        self._menu_manager.quit_application.connect(self.quit_application)
        self._menu_manager.about_sympathy.connect(self._show_about_sympathy)
        self._menu_manager.privacy_notice.connect(
            functools.partial(self._open_url, version.privacy_url()))
        self._menu_manager.find_nodes.connect(self._find_nodes)
        self._menu_manager.user_documentation.connect(
            functools.partial(self.open_documentation, 'index'))
        self._menu_manager.node_library.connect(
            functools.partial(self.open_documentation, 'node_library'))
        self._menu_manager.create_documentation.connect(self._build_docs)
        self._menu_manager.report_issue.connect(self._report_issue)
        self._menu_manager.preferences_updated()

    def _find_nodes(self):
        self._flow_overview_dock.show()
        self._flow_overview.focus_filter()

    def _global_library_path_changed(self):
        current_flow = self._tab_widget.get_current_flow()
        self._library_view.update_libraries(flow=current_flow)

    @QtCore.Slot()
    def _handle_open_flow(self):
        current_flow = self._tab_widget.get_current_flow()
        default_directory = ''
        if current_flow is not None:
            flow_filename = current_flow.root_or_linked_flow_filename
            if flow_filename:
                default_directory = os.path.dirname(flow_filename)
        self.open_flow.emit(default_directory)

    def _init_library_view(self):
        self._library_dock = QtWidgets.QDockWidget('Library', parent=self)
        self._library_dock.setObjectName('Gui::MainWindow::Library')
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self._library_dock)
        self._library_view = library_view.LibraryView(
            parent=self._library_dock)

        settings_ = settings.instance()
        model_type = (
            'Separated' if settings_['Gui/library_separated'] else 'Tag')
        matcher_type = settings_['Gui/library_matcher_type']
        highlighter_type = settings_['Gui/library_highlighter_type']
        highlighter_color = settings_['Gui/library_highlighter_color']

        self._library_view.set_highlighter(
            (matcher_type, highlighter_type, highlighter_color))

        library_item_model = library_view.FlatTagLibraryModel(
            self._app_core.library_root(), self.style(),
            model_type=model_type,
            parent=self._library_dock)
        self._app_core.node_library_added.connect(
            self._library_view.update_model)
        self._examples_paths = self.get_examples_paths()
        self._app_core.node_library_added.connect(
            self._handle_node_library_added)

        self._app_core.flow_libraries_changed.connect(
            self._library_view.update_libraries)

        self._library_view.set_model(library_item_model)
        self._library_separated_changed.connect(
            self._handle_library_separated_changed)
        self._library_show_hidden_changed.connect(
            self._library_view.update_model)
        self._library_highlighter_changed.connect(
            self._library_view.set_highlighter)
        self._library_dock.setWidget(self._library_view)

    def _handle_library_separated_changed(self, separated):
        self._library_view.set_model_type(
            'Separated' if separated else 'Tag')

    def get_examples_paths(self):
        libs = {library.identifier: (library.name, library.examples_path)
                for library in self._app_core.library_root().libraries}
        stdlib = libs.pop('org.sysess.sympathy', (None, None))
        toolkits = sorted([
            lib for lib_id, lib in libs.items()
            if lib_id.startswith('com.sympathyfordata.')])
        third_party = sorted([
            lib for lib_id, lib in libs.items()
            if not lib_id.startswith('com.sympathyfordata.')])
        return [stdlib, (None, None), *toolkits, (None, None), *third_party]

    def _handle_node_library_added(self):
        examples = self.get_examples_paths()
        if set(examples) != set(self._examples_paths):
            self._examples_paths = examples
            self._menu_manager.update_menus()

    def _init_error_view(self):
        self._error_dock = QtWidgets.QDockWidget('Messages', parent=self)
        self._error_dock.setObjectName('Gui::MainWindow::Message')
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self._error_dock)
        self._error_view = messages_window.MessageView(
            self._app_core, parent=self._error_dock)
        self._error_view.goto_node_requested.connect(self._handle_zoom_to_node)

        self._error_dock.setWidget(self._error_view)
        self._app_core.display_message_received.connect(
            self._error_view.add_display_message)
        self._app_core.clear_node_messages_requested.connect(
            self._error_view.clear_node_messages)
        self._app_core.node_library_output.connect(
            self._error_view.add_display_message)
        self._tab_widget.current_flow_changed.connect(
            self._error_view.set_flow)

        for f in sympathy.platform.feature.available_features():
            fm = f.manager()
            fm.changed.connect(functools.partial(
                self._error_view.add_message,
                fm.name, fm.message()))
            fm.changed.emit()

        for msg in util.check_requires():
            self._error_view.add_display_message(msg)

    def _init_flow_overview(self):
        self._flow_overview_dock = QtWidgets.QDockWidget(
            'Flow overview', parent=self)
        self._flow_overview_dock.hide()
        self._flow_overview_dock.setObjectName('Gui::MainWindow::FlowOverview')
        self.addDockWidget(
            QtCore.Qt.LeftDockWidgetArea, self._flow_overview_dock)

        self._flow_overview = flow_overview.FlowOverview(self.style())
        self._flow_overview.select_node.connect(self._handle_zoom_to_node)
        self._flow_overview_dock.setWidget(self._flow_overview)
        self._flow_overview_dock.visibilityChanged.connect(
            self._flow_overview.set_enabled)
        self._tab_widget.current_flow_changed.connect(
            self._flow_overview.set_flow)
        self._flow_overview.select_flow.connect(
            self.open_flow_window)
        self._app_core.bulk_operation_requested.connect(
            self._flow_overview.stop_updates)
        self._app_core.bulk_operation_finished.connect(
            self._flow_overview.start_updates)

    def _init_undo_view(self):
        self._undo_dock = QtWidgets.QDockWidget('Undo stack', parent=self)
        self._undo_dock.hide()
        self._undo_dock.setObjectName('Gui::MainWindow::UndoStack')
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self._undo_dock)

        self._undo_view = flow.undo.UndoStackView(parent=self._undo_dock)
        self._undo_dock.setWidget(self._undo_view)
        self.undo_action = self._undo_view.get_undo_action()
        self.redo_action = self._undo_view.get_redo_action()

    def started(self):
        self._app_core.interface_started()

        # Restore session
        settings_ = settings.instance()
        if settings_['Gui/on_start'] == settings.on_start_last_session:
            files = settings_['session_files']
            for file_ in files:
                if os.path.exists(file_):
                    self.open_named_flow.emit(file_)

        # Restore backups
        self._gui_manager.restore_backups()

        # Open scratch flow
        if settings.instance()['Gui/on_start'] == settings.on_start_new_flow:
            # Don't open scratch flow if another flow (e.g. a restored backup)
            # was already opened
            if not self._tab_widget.count():
                scratch_flow = self._gui_manager.create_flow()
                self._scratch_uuid = scratch_flow.full_uuid

    def add_flow_window(self, flow_window_):
        self._tab_widget.open_flow_window_tab(flow_window_)
        self._tab_widget.setCurrentWidget(flow_window_)
        self._menu_manager.set_window_menus(flow_window_)

    def close_flow_window(self, flow_window_):
        return self.close_flow(flow_window_.flow())

    def close_flow(self, flow_):
        """
        Close workflow. If it is a root flow also close the tabs for all
        subflows as well. Make sure to ask the user to save any changes before
        calling this method.
        """
        self._tab_widget.close_flow_tab(flow_)
        self._menu_manager.set_window_menus(self._tab_widget.currentWidget())
        if not flow_.is_subflow():
            self._app_core.remove_flow(flow_)

    def show_flow(self, flow_):
        self._tab_widget.show_flow(flow_)

    @QtCore.Slot(flow_window.FlowWindow)
    def current_flow_changed(self, flow_window_):
        self._menu_manager.set_window_menus(flow_window_)
        if flow_window_:
            flow_ = flow_window_.flow()
            filename = flow_.root_flow().filename
            if filename != '':
                dirname = os.path.dirname(filename)
            else:
                dirname = settings.instance()['default_folder']
            try:
                os.chdir(dirname)
            except Exception as e:
                self._error_view.add_display_message(
                    util.NodeMessage(
                        # title='Failed to change directory',
                        node=flow_,
                        level=util.Levels.error,
                        brief=(
                            f'Failed to change to workflow directory: '
                            f'{dirname}.\n'
                            f'Ensure that the directory exists and is '
                            f'accessible to make this workflow function '
                            f'properly.\n\n'
                            f'{str(e)}'
                        )))
            else:
                flow_ = flow_window_.flow()
                self._library_view.current_flow_changed(
                    flow_ and flow_.root_or_linked_flow())
                self._undo_view.set_root_flow(flow_.root_flow())
        else:
            self._undo_view.set_root_flow(None)

    def update_flow_labels(self):
        self._tab_widget.update_flow_labels()

    def _pre_quit(self):
        if not self._has_quit:
            self._has_quit = True
            settings_ = settings.instance()
            settings_['Gui/geometry'] = self.saveGeometry()
            settings_['Gui/window_state'] = self.saveState()
            if settings_['Gui/on_start'] == settings.on_start_last_session:
                flows = self._tab_widget.get_flows()
                files = [flow.filename for flow in flows if flow.filename]
                settings_['session_files'] = files
            flows = self._tab_widget.get_flows()
            root_flows = [f for f in flows if f.flow is None]
            if settings_['ask_for_save']:
                try:
                    common.ask_about_saving_flows(
                        root_flows, include_root=True, discard=True)
                except common.SaveCancelled:
                    self._has_quit = False
            if self._has_quit:
                for f in flows:
                    self._tab_widget.close_flow_tab(f)
                self._stop_docs_builder()
            return not self._has_quit

    def _on_quit(self):
        flows = self._app_core.opened_flows()
        for f in flows:
            if f.is_root_flow() and f.filename:
                user_statistics.user_closed_workflow(f)

    @QtCore.Slot()
    def quit_application(self):
        user_cancelled = self._pre_quit()
        if not user_cancelled:
            self._on_quit()
            self.close()

    @QtCore.Slot()
    def show_preferences(self):
        for widget in self._preference_widgets:
            widget.update_data()

        if self._preference_dialog is None:
            self._preference_dialog = preferences.PreferencesDialog(
                self._app_core,
                self._preference_widgets, parent=self)
        self._preference_dialog.exec_()
        self._set_docking_state()
        self._preferences_updated()

    @QtCore.Slot()
    def _show_about_sympathy(self):
        dialog = about_window.AboutWindow(parent=self)
        dialog.exec_()

    @QtCore.Slot()
    def _show_nodewizard(self):
        library_model = library_view.LibraryModel(
            self._app_core.library_root(), self.style(),
            exclude_builtins=(
                not settings.instance()['Gui/platform_developer']))
        wizard = nodewizard.NodeWizard(
            library_model, settings.instance(),
            util.library_paths(flow=self._tab_widget.get_current_flow()),
            self._app_core)
        wizard.exec_()
        if wizard.result() == QtWidgets.QDialog.Accepted:
            self._app_core.reload_node_library()

    @QtCore.Slot()
    def _show_functionwizard(self):
        functionwizard.FunctionWizard().exec_()

    @QtCore.Slot()
    def _show_librarywizard(self):
        wizard = librarywizard.LibraryWizard()
        wizard.exec_()
        if wizard.result() == QtWidgets.QDialog.Accepted:
            self._app_core.reload_node_library()
            self._global_library_path_changed()

    @QtCore.Slot(flow.Flow)
    def handle_flow_name_changed(self, flow_):
        self._tab_widget.update_flow_labels()
        if flow_ and flow_.filename:
            os.chdir(os.path.dirname(flow_.filename))

    @QtCore.Slot()
    def reload_library(self):
        self._app_core.reload_node_library()
        self._app_core.restart_workers()

    @QtCore.Slot()
    def _open_url(self, url):
        oss.open_url(url)

    @QtCore.Slot(str)
    def open_documentation(self, docs_section):
        """
        Open a section of the documentation. docs_section should be a node_id
        or one of the special values 'index', 'viewer' or 'node_library'.
        """
        def check_local_path(path):
            docs = os.path.join(path, 'Docs')
            if not os.path.isfile(os.path.join(docs, 'index.html')):
                docs = None
            return docs

        local_path = prim.sympathy_path()
        public_url = version.documentation_url()
        section = None

        platform_docs = {
            'index': 'index.html',
            'viewer': 'viewer.html',
            'node_library': 'Library/index.html'}

        if docs_section in platform_docs:
            section = platform_docs[docs_section]
        else:
            # doc_section must be a node_id
            library_node = self._app_core.library_node(docs_section)
            source_file = prim.uri_to_path(library_node.source_uri)
            ext = os.path.splitext(source_file)[1]
            if ext in ['.py', '.so', '.pyd']:
                # Python node
                page_name = library_node.class_name
            elif source_file.endswith(".syx"):
                # Subflow node
                page_name = os.path.basename(source_file)
            else:
                assert False

            try:
                root_tags = self._app_core.library_root().tags.root
            except Exception:
                root_tags = None

            if library_node.tags and root_tags:
                split_tags = library_node.tags[0].split('.')
                tags = root_tags
                tag_names = []
                try:
                    for seg in split_tags:
                        tags = tags[seg]
                        tag_names.append(tags.name)
                    tag_path = '/'.join(tag_names)
                except Exception:
                    tag_path = 'Unknown'
            else:
                tag_path = 'Unknown'

            section = f'Library/Nodes/{tag_path}/{page_name}.html'

            if library_node.library_id not in [
                    'org.sysess.builtin', 'org.sysess.sympathy']:
                local_path = library_node.library

            public_url = next(iter([
                lib.documentation_url
                for lib in self._app_core.library_root().libraries
                if lib.identifier == library_node.library_id]), None)

        local_path = check_local_path(local_path)
        url = None
        message = ''

        if local_path:
            local_file = os.path.join(
                local_path, prim.nativepath_separators(section))

            url = prim.localuri(
                prim.unipath_separators(local_file))

            if not os.path.isfile(local_file):
                message = f'local {local_file} could not be found'
                url = None

        elif public_url:
            public_url = public_url.rstrip('/')
            url = f'{public_url}/{section}'

            response = request_http.value.get(url)
            if not response.ok:
                message = f'public {url} is unavailable'
                url = None
        else:
            message = f'{section} could not be found'

        if url:
            self._open_url(url)
        else:
            # TODO(magnus): Add something about asking library maintainer
            # to build docs when appropriate.
            QtWidgets.QMessageBox.information(
                self, "No documentation found",
                "The documentation for {}. "
                "Please build the documentation first.".format(
                    message))

    def _stop_docs_builder(self):
        if self._docs_builder_view:
            self._docs_builder_view.stop()

    def _build_docs(self, callback=None):
        if self._docs_builder_view:
            self._docs_builder_view.stop()

        self._docs_builder_view = DocsBuilderView(
            self._app_core.get_documentation_builder(),
            callback=callback, parent=self)

        self._control_panel.set_current_progress_object(
            self._docs_builder_view)

    def _report_issue(self):
        dialog = issues.IssueReportSender()

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if all(url.toLocalFile().endswith(".syx")
                   for url in event.mimeData().urls()):
                event.acceptProposedAction()
            else:
                event.setAccepted(False)
        else:
            event.setAccepted(False)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                self.open_named_flow.emit(
                    url.toLocalFile())
        else:
            event.setAccepted(False)

    def closeEvent(self, event):
        user_cancelled = self._pre_quit()
        if not user_cancelled:
            self._on_quit()
            super(MainWindow, self).closeEvent(event)
            event.accept()
            self.closed.emit()
        else:
            event.ignore()

    def close_scratch_flow(self):
        """
        Close the flow that was automatically created on start if empty.

        To be considered empty, the flow must be unsaved, clean, and have an
        empty undo stack.
        """
        if self._scratch_uuid is None:
            return

        try:
            flow_ = self._app_core.get_flow(self._scratch_uuid)
        except KeyError:
            return

        if (not flow_.filename
                and flow_.is_clean()
                and not flow_.undo_stack().get_command_list()):
            self.close_flow(flow_)
            self._scratch_uuid = None

    def _handle_zoom_to_node(self, node):
        # Check with appcore that this node still exists:
        try:
            # TODO (magnus): We need an API in appcore for checking if a node
            # exists. get_node could return None in that case.
            self._app_core.get_node(node.full_uuid)
        except Exception:
            return

        if node.flow:
            self.open_flow_window.emit(node.flow)
        self._tab_widget.currentWidget()._handle_zoom_to_node(node)

    def _set_docking_state(self):
        state = QtWidgets.QDockWidget.DockWidgetClosable
        docking = settings.instance()['Gui/docking_enabled']
        movable = True
        floatable = True

        if docking == 'Movable':
            state |= QtWidgets.QDockWidget.DockWidgetMovable
            floatable = False
        elif docking == 'Locked':
            movable = False
            floatable = False
        else:
            state |= (QtWidgets.QDockWidget.DockWidgetFloatable |
                      QtWidgets.QDockWidget.DockWidgetMovable)

        self._library_dock.setFeatures(state)
        self._error_dock.setFeatures(state)
        self._flow_overview_dock.setFeatures(state)
        self._undo_dock.setFeatures(state)

        self._control_panel.setMovable(movable)
        self._control_panel.setFloatable(floatable)

    def _preferences_updated(self):
        self._tab_widget.preferences_updated()
        self._menu_manager.preferences_updated()


class ProgressObject(QtCore.QObject):

    progress = QtCore.Signal(float)
    done = QtCore.Signal(str)

    statuses = ('Completed', 'Cancelled', 'Failed', 'In progress')
    (status_complete, status_cancel, status_fail,
     status_in_progress) = statuses

    @property
    def name(self):
        return self._name

    @property
    def desc(self):
        return self._desc

    @property
    def status(self):
        return self._status

    def stop(self):
        pass


class DocsBuilderView(ProgressObject):
    def __init__(self, docs_builder, callback=None, parent=None):
        super(DocsBuilderView, self).__init__(parent)

        self._docs_builder = docs_builder
        self._docs_builder.start()
        self._timer = QtCore.QTimer(parent=parent)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self.update)
        self._timer.start()

        self._name = 'Documenting'
        self._desc = (
            'Building documentation for the platform and standard library.')
        self._status = self.status_in_progress

    @QtCore.Slot()
    def update(self):
        if self._docs_builder.is_alive():
            progress = self._docs_builder.get_progress()
            self.progress.emit(progress)
        else:
            self._timer.stop()
            self._docs_builder.join()
            self.done.emit(self.status_complete)

    def stop(self):
        self._docs_builder.stop()
        self._timer.stop()
        self._callback = None
        self._docs_builder.join()
        self.done.emit(self.status_cancel)
