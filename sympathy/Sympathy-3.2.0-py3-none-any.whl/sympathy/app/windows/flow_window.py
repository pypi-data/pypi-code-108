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
import functools

import Qt.QtGui as QtGui
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

from .. import flowview
from .. import flow
from .. import keymaps
from .. import themes


class FlowWindow(QtWidgets.QMainWindow):
    new_signal = QtCore.Signal()
    open_signal = QtCore.Signal()
    save_signal = QtCore.Signal()
    save_as_signal = QtCore.Signal()
    close_signal = QtCore.Signal()
    close_tree_signal = QtCore.Signal(flow.Flow)
    execute_signal = QtCore.Signal()
    profile_signal = QtCore.Signal()
    stop_signal = QtCore.Signal()
    reload_signal = QtCore.Signal()
    copy_signal = QtCore.Signal()
    cut_signal = QtCore.Signal()
    delete_signal = QtCore.Signal()
    paste_signal = QtCore.Signal()
    zoom_in_signal = QtCore.Signal()
    zoom_out_signal = QtCore.Signal()
    zoom_restore_signal = QtCore.Signal()
    zoom_fit_all_signal = QtCore.Signal()
    zoom_fit_selection_signal = QtCore.Signal()
    edit_subflow_requested = QtCore.Signal(flow.Flow)
    select_all_signal = QtCore.Signal()
    help_requested = QtCore.Signal(str)
    insert_node_signal = QtCore.Signal()
    toggle_insert_text_field_signal = QtCore.Signal(bool)
    inserting_text_field_signal = QtCore.Signal(bool)
    moving_signal = QtCore.Signal(bool)
    selection_tool_signal = QtCore.Signal()
    panning_tool_signal = QtCore.Signal()

    def __init__(self, flow_, gui_manager, app_core, color=None, parent=None):
        super(FlowWindow, self).__init__(parent, QtCore.Qt.Window)
        self._flow = flow_
        self._gui_manager = gui_manager
        self._app_core = app_core
        self.color = color
        keymap = keymaps.get_active_keymap()
        theme = themes.get_active_theme()

        self._flow_view = flowview.FlowView(
            self._flow, self._app_core, parent=self)
        self._flow_view.edit_subflow_requested[flow.Flow].connect(
            self.edit_subflow_requested)
        self._flow_view.help_requested[str].connect(
            self.help_requested)

        self._flow.before_remove.connect(self._before_remove)
        self.setCentralWidget(self._flow_view)

        self._init_flow_signals()

        self._cut_action = self._new_action(
            'Cu&t', keymap.cut, theme.cut)
        self._cut_action.triggered.connect(self._flow_view.handle_cut)
        self._copy_action = self._new_action(
            '&Copy', keymap.copy, theme.copy)
        self._copy_action.triggered.connect(self._flow_view.handle_copy)
        self._paste_action = self._new_action(
            '&Paste', keymap.paste, theme.paste)
        self._paste_action.triggered.connect(
            self._flow_view.handle_paste_at_cursor)
        self._delete_action = self._new_action(
            '&Delete', keymap.delete, theme.delete)
        self._delete_action.triggered.connect(self._flow_view.handle_delete)

        self._select_all_action = self._new_action(
            'Select &All',
            keymap.select_all)
        self._select_all_action.triggered.connect(self._flow_view.select_all),

    def _new_action(self, text, shortcut, icon=None,
                    shortcut_ctx=QtCore.Qt.WidgetWithChildrenShortcut):
        action = QtWidgets.QAction(text, self)
        action.setShortcut(shortcut)
        action.setShortcutContext(shortcut_ctx)
        if icon:
            action.setIcon(QtGui.QIcon(icon))
        self.addAction(action)
        return action

    def _init_flow_signals(self):
        self.zoom_in_signal.connect(self._flow_view.zoom_in)
        self.zoom_out_signal.connect(self._flow_view.zoom_out)
        self.zoom_restore_signal.connect(self._flow_view.zoom_restore)
        self.zoom_fit_all_signal.connect(self._flow_view.zoom_fit_all)
        self.zoom_fit_selection_signal.connect(
            self._flow_view.zoom_fit_selection)
        self.copy_signal.connect(self._flow_view.handle_copy)
        self.cut_signal.connect(self._flow_view.handle_cut)
        self.delete_signal.connect(self._flow_view.handle_delete)
        self.paste_signal.connect(self._flow_view.handle_paste_at_cursor)
        self.select_all_signal.connect(self._flow_view.select_all)

        self.stop_signal.connect(self._flow.abort_action)
        self.reload_signal.connect(self._flow.reload_action)
        self.execute_signal.connect(self._flow.execute_action)
        self.profile_signal.connect(self._flow.profile_action)

        self.insert_node_signal.connect(
            self._flow_view.insert_node_via_popup)
        self.toggle_insert_text_field_signal.connect(
            self._flow_view.toggle_insert_text_field)
        self._flow_view.state_changed.connect(
            lambda: self.inserting_text_field_signal.emit(
                self._flow_view.is_inserting_text_field))
        self._flow_view.state_changed.connect(
            lambda: self.moving_signal.emit(self._flow_view.is_moving))
        self.open_signal.connect(self._handle_open_flow)
        self.save_signal.connect(
            functools.partial(self._gui_manager.save_flow, self._flow))
        self.save_as_signal.connect(
            functools.partial(self._gui_manager.save_as_flow, self._flow))

        self.selection_tool_signal.connect(
            self._flow_view.handle_selection_tool)
        self.panning_tool_signal.connect(
            self._flow_view.handle_panning_tool)

        self.close_signal.connect(self.close_flow)

    def _handle_zoom_to_node(self, node):
        self._flow_view._handle_zoom_to_node(node)

    @QtCore.Slot()
    def _handle_open_flow(self):
        flow_filename = self._flow.root_or_linked_flow_filename
        if flow_filename:
            default_directory = os.path.dirname(flow_filename)
        else:
            default_directory = ''
        self._gui_manager.open_flow(default_directory)

    @QtCore.Slot()
    def close_flow(self):
        return self._gui_manager.close_tree(self._flow, False)

    def _before_remove(self):
        return self._gui_manager.close_tree(self._flow, True)

    def close_flow_view(self):
        self._flow_view.close()

    def flow(self):
        return self._flow

    def name(self):
        return self._flow.display_name

    def filename(self):
        return self._flow.filename

    def edit_menu_actions(self):
        return [self._select_all_action, None, self._cut_action,
                self._copy_action, self._paste_action, self._delete_action,
                None]

    def view_menu_actions(self):
        return []

    def preferences_updated(self):
        self._flow_view.preferences_updated()
