# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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
from Qt import QtCore, QtGui, QtWidgets

from .. import signals
from .. import keymaps
from .. import themes
from sympathy.platform.hooks import status_extra_text


class ControlPanel(QtWidgets.QToolBar):
    new_signal = QtCore.Signal()
    open_signal = QtCore.Signal()

    def __init__(self, parent):
        super(ControlPanel, self).__init__('Tool bar', parent=parent)
        self._actions = []
        self._separators = []
        self._flow_signals = signals.SignalHandler()
        self._progress_signals = signals.SignalHandler()

        theme = themes.get_active_theme()
        keymap = keymaps.get_active_keymap()
        self._new_action = self._add_action(
            '&New Flow', self.new_signal, theme.new_flow, append=False)
        self._open_action = self._add_action(
            '&Open', self.open_signal, theme.open_flow, append=False)
        self._save_action = self._add_action(
            '&Save', None, theme.save_flow, keymap.save_flow)

        # Not in the toolbar:
        self._save_as_action = QtWidgets.QAction('Save &As...', self)
        self._save_as_action.setShortcut(keymap.save_flow_as)

        self._add_toolbar_separator()

        self._execute_action = self._add_action(
            '&Execute', None, theme.execute, keymap.execute_flow)
        self._profile_action = self._add_action(
            '&Profile', None, theme.profile,
            keymap.profile_flow, add=False)
        self._stop_action = self._add_action(
            '&Abort', None, theme.stop, keymap.stop)
        self._reload_action = self._add_action(
            '&Reload', None, theme.reload, keymap.reload_flow)

        self._add_toolbar_separator()

        self._cut_action = self._add_action(
            'Cu&t', None, theme.cut, add=False)
        self._copy_action = self._add_action(
            '&Copy', None, theme.copy, add=False)
        # self._paste_action = self._add_action(
        #     '&Paste', None, theme.paste)

        self._insert_text_field_action = self._add_action(
            'Insert Text Field', None, theme.text_field)
        self._insert_text_field_action.setCheckable(True)

        self._insert_node_action = self._add_action(
            'Insert Node', None, theme.insert_node,
            keymap.insert_node)
        self._delete_action = self._add_action(
            '&Delete', None, theme.delete)

        self._add_toolbar_separator()

        self._tools_group = QtWidgets.QActionGroup(self)
        self._selection_tool_action = self._add_action(
            'Selection Tool', None,
            theme.selection, keymap.selection_tool)
        self._tools_group.addAction(self._selection_tool_action)
        self._selection_tool_action.setCheckable(True)
        self._selection_tool_action.setChecked(True)
        self._panning_tool_action = self._add_action(
            'Panning Tool', None, theme.panning)
        self._tools_group.addAction(self._panning_tool_action)
        self._panning_tool_action.setCheckable(True)

        self._add_toolbar_separator()

        self._add_toolbar_spacer()

        self._progress_status = QtWidgets.QLabel()
        self._progress_status_action = QtWidgets.QWidgetAction(self)

        policy = self._progress_status.sizePolicy()
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Minimum)
        self._progress_status.setSizePolicy(policy)
        self._progress_status_action.setDefaultWidget(self._progress_status)
        self.addAction(self._progress_status_action)
        self._progress_status_action.setVisible(False)

        self._progress_action = QtWidgets.QWidgetAction(self)
        self._progress_bar = QtWidgets.QProgressBar()
        policy = self._progress_bar.sizePolicy()
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Minimum)
        self._progress_bar.setSizePolicy(policy)
        self._progress_action.setDefaultWidget(self._progress_bar)
        self.addAction(self._progress_action)
        self._progress_action.setVisible(False)

        extra_text = status_extra_text.value()
        if extra_text:
            self.addWidget(QtWidgets.QLabel(extra_text))

        self._add_toolbar_separator()

        self._zoom_in_action = self._add_action(
            'Zoom &In', None,
            theme.zoom_in,
            keymap.zoom_in)
        self._zoom_out_action = self._add_action(
            'Zoom &Out', None,
            theme.zoom_out,
            keymap.zoom_out)
        self._zoom_restore_action = self._add_action(
            'Zoom &Restore', None,
            theme.zoom_default,
            keymap.zoom_default,
            add=False)
        self._zoom_fit_selection_action = self._add_action(
            'Zoom To &Selection', None,
            theme.zoom_fit_selection,
            keymap.zoom_fit_selection,
            add=False)
        self._zoom_fit_all_action = self._add_action(
            'Zoom Fit &All', None,
            theme.zoom_fit,
            keymap.zoom_fit_all)

        # Not in the toolbar:
        self._close_action = QtWidgets.QAction('Close', self)
        self._close_action.setIcon(QtGui.QIcon(theme.close_flow))
        self._close_action.setShortcut(keymap.close_flow)

        self.setIconSize(QtCore.QSize(16, 16))
        self._toggle_control_panel_action = self.toggleViewAction()
        self._toggle_control_panel_action.setText("&Tool bar")

    def _add_action(self, name, signal=None, icon=None, shortcut=None,
                    append=True, add=True):
        action = QtWidgets.QAction(name, self)
        if signal is not None:
            action.triggered.connect(signal)
        if icon:
            action.setIcon(QtGui.QIcon(icon))
        if shortcut:
            action.setShortcut(shortcut)
        if add:
            self.addAction(action)
        if append:
            self._actions.append(action)
        return action

    def _add_toolbar_separator(self, append=True):
        action = self.addSeparator()
        if append:
            self._separators.append(action)

    def _add_toolbar_spacer(self):
        spacer = QtWidgets.QWidget(parent=self)
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Expanding)
        self.addWidget(spacer)

    def file_menu_actions(self):
        return [self._save_action,
                self._save_as_action,
                self._close_action]

    def edit_menu_actions(self):
        return [self._insert_node_action,
                self._insert_text_field_action]

    def control_menu_actions(self):
        return [self._execute_action, self._profile_action, self._stop_action,
                self._reload_action]

    def view_menu_actions(self):
        return [self._toggle_control_panel_action,
                None,
                self._zoom_in_action,
                self._zoom_out_action, self._zoom_restore_action,
                self._zoom_fit_selection_action, self._zoom_fit_all_action]

    def set_current_flow(self, flow_window):
        self._flow_signals.disconnect_all()

        has_flow = flow_window is not None
        for action in self._actions + self._separators:
            action.setVisible(has_flow)

        if not has_flow:
            return

        for action, handler in [
                (self._save_action, flow_window.save_signal),
                (self._save_as_action, flow_window.save_as_signal),
                (self._close_action, flow_window.close_signal),

                # (self._select_all_action, flow_window.select_all_signal),
                (self._cut_action, flow_window.cut_signal),
                (self._copy_action, flow_window.copy_signal),
                # (self._paste_action, flow_window.paste_signal),
                (self._delete_action, flow_window.delete_signal),
                (self._insert_node_action, flow_window.insert_node_signal),

                (self._execute_action, flow_window.execute_signal),
                (self._profile_action, flow_window.profile_signal),
                (self._stop_action, flow_window.stop_signal),
                (self._reload_action, flow_window.reload_signal),

                (self._selection_tool_action,
                 flow_window.selection_tool_signal),
                (self._panning_tool_action, flow_window.panning_tool_signal),

                (self._zoom_in_action, flow_window.zoom_in_signal),
                (self._zoom_out_action, flow_window.zoom_out_signal),
                (self._zoom_fit_all_action, flow_window.zoom_fit_all_signal),
                (self._zoom_fit_selection_action,
                 flow_window.zoom_fit_selection_signal),
                (self._zoom_restore_action, flow_window.zoom_restore_signal)]:

            self._flow_signals.connect(
                flow_window, action.triggered, handler)

        # Needs to be connected using toggled.
        # For some reason, disconnecting when using triggered does not work.

        self._flow_signals.connect_reference(
            flow_window, [
                (self._insert_text_field_action.toggled,
                 flow_window.toggle_insert_text_field_signal),
                (flow_window.inserting_text_field_signal,
                 self._insert_text_field_action.setChecked),
                (flow_window.moving_signal,
                 self._insert_text_field_action.setDisabled)])

    def set_current_progress_object(self, progress_object):
        self._progress_signals.disconnect_all()
        self._progress_action.setVisible(True)
        self._progress_status_action.setVisible(True)
        self._progress_bar.setToolTip(progress_object.desc)
        self._progress_status.setToolTip(progress_object.desc)
        self._progress_bar.setValue(0)
        self._progress_status.setText(progress_object.name)

        self._progress_signals.connect(
            progress_object, progress_object.progress,
            self._progress_bar.setValue)
        self._progress_signals.connect(
            progress_object, progress_object.done, self._progress_object_done)

        progress_object.done.connect(self._progress_object_done)

    def _progress_object_done(self, status):
        self._progress_signals.disconnect_all()
        self._progress_action.setVisible(False)
        self._progress_status_action.setVisible(False)
        self._progress_bar.setToolTip('')
        self._progress_status.setToolTip('')
        self._progress_bar.reset()
        self._progress_status.setText('')
