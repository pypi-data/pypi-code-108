# This file is part of Sympathy for Data.
# Copyright (c) 2015 Combine Control Systems AB
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
"""
This module contains functionality for working with the undo stacks of
sympathy flows.

A flow can have linked subflows in multiple files and we have to track whether
there has been any changes to each of those files. On the other hand we also
want to present a single undo stack for such a flow hierarchy.
"""
from __future__ import annotations
import contextlib
from collections import defaultdict
from typing import TYPE_CHECKING, List, Set, Optional

import PySide2.QtGui as QtGui
import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from .. import keymaps
from .. import settings
from .. import themes
from sympathy.utils import event, log
from sympathy.utils.prim import format_display_string

if TYPE_CHECKING:
    from sympathy.app.flow.flow import Flow

logger = log.get_logger('app.undo')


class CommandFailed(Exception):
    """
    If a command raises CommandFailed when pushed to an UndoStack, the command
    will be discarded, with no changes to the undo stack.

    The command is responsible for ensuring that nothing has been changed
    before raising CommandFailed, possibly by undoing any partially executed
    changes.
    """


class UndoCommand:
    """
    Subclass this for all undo commands in UndoStack.

    Implementors should override _undo() and _redo(), and
    possibly _first_redo(), affected_flows(), and added_removed_flows().

    If supplied, context should be a callable which returns a context manager.
    All _undo, _redo, and _first_redo will then be run within that context.
    """
    def __init__(self, *, flow: Flow = None, text: str = '', context=None):
        self._context = context or contextlib.nullcontext
        self._flow = flow
        self.__root_flow = flow and flow.root_or_linked_flow()
        self.__text = text
        self.__first_time = True
        self.__succeeded = None

    def flow(self) -> Optional[Flow]:
        """Return the flow sent to the constructor, if any."""
        return self._flow

    def affected_flows(self) -> List[Flow]:
        """
        Return all linked/root flows that are made dirty by this command.

        Default implementation returns only the flow passed to the constructor.
        Override this to implement any other behavior.

        This method is only called after a command is pushed, so it can be
        lazily populated after the first redo.

        Note that any linked subflows that are added or removed by this command
        should also be included to ensure that backup files are created/removed
        as they should.
        """
        if self.__root_flow is not None:
            return [self.__root_flow]
        raise NotImplementedError(
            f"Couldn't determine affected flows for {self}. "
            f"You need to either pass a flow to UndoCommand constructor or "
            f"override affected_flow().")

    def added_removed_flows(self) -> List[Flow]:
        """
        Return all added or removed linked subflows.

        Including subflows that changed from being linked to being non-linked
        or vice versa.
        """
        return []

    def _first_redo(self):
        """
        Override this if the first redo should differ from subsequent redos.
        """
        self._redo()

    def _redo(self):
        """Override this with the command's redo functionality."""
        raise NotImplementedError()

    def _undo(self):
        """Override this with the command's undo functionality."""
        raise NotImplementedError()

    def redo(self):
        """
        Redo the command by entering its context and calling _first_redo() the
        first time and _redo() on subsequent calls.

        Sets succeeded flag based on the result.
        """
        with self._context():
            return self.redo_no_context()

    def redo_no_context(self):
        """Redo the command without using its context."""
        try:
            if self.__first_time:
                self._first_redo()
                self.__first_time = False
            else:
                self._redo()
        except CommandFailed:
            self.__succeeded = False
            raise
        else:
            self.__succeeded = True

    def undo(self):
        """Undo the command by entering its context and calling _undo()."""
        with self._context():
            return self.undo_no_context()

    def undo_no_context(self):
        """Undo the command without using its context."""
        self._undo()

    def text(self) -> str:
        return self.__text

    def set_text(self, text: str):
        self.__text = text

    def succeeded(self) -> Optional[bool]:
        """
        Return True if this command was be pushed successfully, False if
        pushing it failed and None if the command has not been pushed yet.
        """
        return self.__succeeded

    def debug_str(self) -> str:
        cls = self.__class__.__name__
        affected = ", ".join(
            f.display_name for f in set(self.affected_flows()))
        added_removed = ", ".join(
            f.display_name for f in set(self.added_removed_flows()))
        if added_removed:
            added_removed = f" (\u00b1 {added_removed})"
        return f"{cls} (* {affected}){added_removed}"


class MacroCommand(UndoCommand):
    """
    A simple macro command recording multiple commands as a single entry in the
    undo history.

    If any subcommand raises CommandFailed, the macro command will undo any
    previous subcommands and also reraise CommandFailed.

    Subcommand contexts are not used. Instead pass a context for the
    MacroCommand itself.
    """
    def __init__(self, commands: List[UndoCommand], **kwargs):
        super().__init__(**kwargs)
        self._cmds = commands or []
        self.__affected_flows: Optional[List[Flow]] = None
        self.__added_removed_flows: Optional[List[Flow]] = None

    def affected_flows(self) -> List[Flow]:
        # Check affected flows lazily to allow it to be populated by e.g.
        # first redo
        if self.__affected_flows is None:
            self.__affected_flows = []
            for cmd in self._cmds:
                self.__affected_flows.extend(cmd.affected_flows())
        return self.__affected_flows

    def added_removed_flows(self) -> List[Flow]:
        # Check added/removed flows lazily to allow it to be populated by e.g.
        # first redo
        if self.__added_removed_flows is None:
            self.__added_removed_flows = []
            for cmd in self._cmds:
                self.__added_removed_flows.extend(cmd.added_removed_flows())
        return self.__added_removed_flows

    def _redo(self):
        if not self._cmds:
            raise CommandFailed()
        done = []
        for cmd in self._cmds:
            try:
                logger.info("Redo subcommand %s", cmd)
                cmd.redo_no_context()
            except CommandFailed:
                for cmd_ in reversed(done):
                    cmd_.undo_no_context()
                raise
            else:
                done.append(cmd)

    def _undo(self):
        for cmd in reversed(self._cmds):
            logger.info("Undo subcommand %s", cmd)
            cmd.undo_no_context()

    def text(self) -> str:
        if len(self._cmds) == 1:
            return self._cmds[0].text()
        return super().text()

    def debug_str(self) -> str:
        base_debug_str = super().debug_str()
        subcommands = "\n  ".join(
            cmd.debug_str().replace("\n", "\n  ") for cmd in self._cmds)
        return f"{base_debug_str}\n  {subcommands}"


class UndoStack:
    """
    Stack of undoable commands.

    Commands should fulfill the interface of class UndoCommand.

    UndoStack doesn't have any requirements on the flows other than that they
    are hashable.

    Events:
    -------
    command_list_changed(): is emitted whenever a command is pushed to the
                            stack.
    index_changed(): is emitted whenever the current undo index changes.
    clean_changed(): is emitted whenever the clean state of any subflow
                     changes.
    flow_state_changed(flow): is emitted whenever the state of flow is changed
                              by an UndoCommand or when flow becomes
                              clean/dirty.
    """
    def __init__(self):
        self.command_list_changed = event.Event()
        self.index_changed = event.Event()
        self.clean_changed = event.Event()
        self.flow_state_changed = event.Event()

        self._cmds = []
        self._index = 0

        # self._flow_states represents the states of all file-backed flows
        # (root flow + linked subflows). They are represented as integers and
        # increment each time that flow is changed. Unchanged flows are at
        # state 0, which can be implicit if the flow hasn't yet been added to
        # self._flow_states.
        self._flow_states = defaultdict(int)

        # self._clean_states stores the clean states of all file-backed flows.
        # A flow is clean if its state in self._flow_states is at its clean
        # state. If the flow has no clean state, this is represented as a -1.
        # Unchanged flows are clean by default, which is represented by a clean
        # state of 0. This can be implicit if the flow hasn't yet been added to
        # self._clean_states.
        self._clean_states = defaultdict(int)

    def push(self, cmd: UndoCommand):
        """
        Push an undo command onto the stack, running its redo method.

        If any commands were previously available to be redone, they are
        discarded.

        If the command raises CommandFailed during its redo, the command will
        be discarded, with no changes to the undo stack.
        """
        try:
            logger.info("Push command %s", cmd)
            cmd.redo()
        except CommandFailed:
            logger.info("Command %s raised CommandFailed, skipping.", cmd)
            return
        else:
            # Command succeeded. We should add it to the stack!
            pass

        # First remove any "future" commands currently in the stack:
        if self.can_redo():
            self._cmds = self._cmds[:self._index]

            # Also remove any clean states occurring after discarded commands:
            for flow, clean_state in self._clean_states.items():
                if clean_state > self._flow_states[flow]:
                    logger.debug("Discarding clean state for flow %s", flow)
                    self._clean_states[flow] = -1

        self._cmds.append(cmd)
        self.command_list_changed.emit()
        self._step(cmd, 1)

    def undo(self):
        """Undo the previous command."""
        if not self.can_undo():
            return

        cmd = self._cmds[self._index - 1]
        logger.info("Undo command %s", cmd)
        cmd.undo()
        self._step(cmd, -1)

    def redo(self):
        """Redo the next command."""
        if not self.can_redo():
            return

        cmd = self._cmds[self._index]
        logger.info("Redo command %s", cmd)
        cmd.redo()
        self._step(cmd, 1)

    def _step(self, cmd, diff):
        assert diff in (-1, 1)
        clean_changed = False
        self._index += diff

        # Each affected flow gets assigned a new state number.
        for flow in cmd.affected_flows():
            old_clean = self.is_clean(flow)
            self._flow_states[flow] += diff
            logger.debug(
                "Flow %s changed state to: %s", flow, self._flow_states[flow])
            self.flow_state_changed.emit(flow)
            new_clean = self.is_clean(flow)
            if old_clean != new_clean:
                logger.debug(
                    "Flow %s is now %s", flow,
                    "clean" if new_clean else "dirty")
                clean_changed = True

        # Emit flow_state_changed event for all flows in added_removed_flows
        # without assigning new state numbers.
        for flow in cmd.added_removed_flows():
            self.flow_state_changed.emit(flow)
            clean_changed = True

        if clean_changed:
            self.clean_changed.emit()
        self.index_changed.emit()

    def set_index(self, target):
        """
        Undo/redo until index is at target.

        May emit flow_state_changed and clean_changed multiple times.
        """
        if target == self._index:
            return
        if not 0 <= target <= len(self._cmds):
            raise IndexError(f"Invalid undo index: {target}")

        step = self.redo if target > self._index else self.undo
        for _ in range(abs(target - self._index)):
            step()

    def set_clean(self, flow: Flow, clean: bool = True):
        """
        Mark the current state as clean for flow.

        This is useful e.g. after save and load. Calling with clean=False can
        be useful e.g. after restore from backup, when the only existing undo
        state should be considered dirty.
        """
        if clean:
            new_clean_state = self._flow_states[flow]
        else:
            new_clean_state = -1
        self._set_clean_state(flow, new_clean_state)

    def _set_clean_state(self, flow, clean_state):
        old_clean = self.is_clean(flow)
        self._clean_states[flow] = clean_state
        new_clean = self.is_clean(flow)
        if old_clean != new_clean:
            logger.debug(
                "Flow %s is now %s", flow,
                "clean" if new_clean else "dirty")
            self.clean_changed.emit()
            self.flow_state_changed.emit(flow)

    def is_clean(self, flow: Flow) -> bool:
        return self._clean_states[flow] == self._flow_states[flow]

    def get_dirty_flows(self) -> Set[Flow]:
        """
        Return all dirty flows tracked by this undo stack.

        Note that the returned flows might have been deleted from their parent
        flow.
        """
        known_flows = (set(self._flow_states.keys())
                       | set(self._clean_states.keys()))
        return {flow for flow in known_flows if not self.is_clean(flow)}

    def can_undo(self) -> bool:
        return self._index > 0

    def can_redo(self) -> bool:
        return self._index < len(self._cmds)

    def get_undo_text(self) -> str:
        if not self.can_undo():
            return ""
        return self._cmds[self._index - 1].text()

    def get_redo_text(self) -> str:
        if not self.can_redo():
            return ""
        return self._cmds[self._index].text()

    def get_command_list(self) -> List[str]:
        """
        Get a list of strings representing the commands in the undo stack.
        """
        return [cmd.text() for cmd in self._cmds]

    def get_index(self) -> int:
        return self._index

    def command_debug_str(self, index: int) -> str:
        return "<pre>{}</pre>".format(self._cmds[index].debug_str())

    def flow_debug_str(self, flow: Flow) -> str:
        state = self._flow_states.get(flow)
        clean = self._clean_states.get(flow)
        return f"Current state: {state}\nClean state: {clean}"


class UndoStackModel(QtCore.QAbstractListModel):
    def __init__(self):
        self._undo_stack = None
        self._command_list = []
        self._index = 0

        super().__init__()
        theme = themes.get_active_theme()
        self._current_icon = QtGui.QIcon(theme.current_in_list)
        no_icon_pixmap = self._current_icon.pixmap(QtCore.QSize(16, 16))
        no_icon_pixmap.fill(QtGui.QColor(0, 0, 0, 0))
        self._no_icon = QtGui.QIcon(no_icon_pixmap)

    def set_undo_stack(self, undo_stack: Optional[UndoStack]):
        if self._undo_stack is not None:
            self._undo_stack.command_list_changed.remove_handler(
                self._update_command_list)
            self._undo_stack.index_changed.remove_handler(
                self._update_index)

        self._undo_stack = undo_stack
        self._update_command_list()
        self._update_index()

        if self._undo_stack is not None:
            self._undo_stack.command_list_changed.add_handler(
                self._update_command_list)
            self._undo_stack.index_changed.add_handler(
                self._update_index)

    def _update_command_list(self):
        self.beginResetModel()
        if self._undo_stack is None:
            self._command_list = []
        else:
            self._command_list = self._undo_stack.get_command_list()
        self.endResetModel()

    def _update_index(self):
        if self._undo_stack is None:
            self._index = 0
            return

        old_index = self._index
        self._index = self._undo_stack.get_index()
        self.dataChanged.emit(
            self.index(old_index),
            self.index(self._index),
            [QtCore.Qt.DecorationRole])

    def rowCount(self, _index):
        if self._undo_stack is None:
            return 0
        return len(self._command_list) + 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if row == 0:
                return "<Empty>"
            return format_display_string(self._command_list[row - 1])
        elif role == QtCore.Qt.ToolTipRole:
            if not settings.instance()['Gui/platform_developer']:
                return ""
            if row == 0:
                return "<Empty>"
            return self._undo_stack.command_debug_str(row - 1)
        elif role == QtCore.Qt.DecorationRole:
            if row == self._index:
                return self._current_icon
            else:
                return self._no_icon
        elif role == QtCore.Qt.FontRole:
            font = QtGui.QFont()
            if row == self._index:
                font.setBold(True)
            return font
        return None

    def set_index(self, target):
        """
        Wrapper for UndoStack.set_index, ensuring that the model is only
        updated once at the end.
        """
        if self._undo_stack is None:
            return

        with self._undo_stack.index_changed.block_handler(
                self._update_index):
            self._undo_stack.set_index(target)
        self._update_index()


class UndoStackView(QtWidgets.QListView):
    """
    Visualizes the undo history as a list.

    Provides QActions for an UndoStack and keeps them up to date when the state
    of the undo stack changes (current undo text, enable/disable actions etc.).
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setSelectionMode(self.NoSelection)
        self.setIconSize(QtCore.QSize(16, 16))
        self.setModel(UndoStackModel())
        self._undo_stack = None

        theme = themes.get_active_theme()
        keymap = keymaps.get_active_keymap()
        self._undo_action = QtWidgets.QAction()
        self._undo_action.setIcon(QtGui.QIcon(theme.undo))
        self._undo_action.setShortcut(keymap.undo)
        self._undo_action.triggered.connect(self._undo)
        self._redo_action = QtWidgets.QAction()
        self._redo_action.setIcon(QtGui.QIcon(theme.redo))
        self._redo_action.setShortcut(keymap.redo)
        self._redo_action.triggered.connect(self._redo)
        self._update_actions()

    def _update_actions(self):
        if self._undo_stack and self._undo_stack.can_undo():
            self._undo_action.setEnabled(True)
            cmd_text = self._undo_stack.get_undo_text()
            self._undo_action.setText(f'&Undo "{cmd_text}"')
        else:
            self._undo_action.setEnabled(False)
            self._undo_action.setText("&Undo")
        if self._undo_stack and self._undo_stack.can_redo():
            self._redo_action.setEnabled(True)
            cmd_text = self._undo_stack.get_redo_text()
            self._redo_action.setText(f'&Redo "{cmd_text}"')
        else:
            self._redo_action.setEnabled(False)
            self._redo_action.setText("&Redo")

    def _handle_index_changed(self):
        if self._undo_stack:
            index = self.model().index(self._undo_stack.get_index())
            self.setCurrentIndex(index)
            self.scrollTo(index)
        self._update_actions()

    def currentChanged(self, current, _old):
        self.model().set_index(current.row())

    def _undo(self):
        if self._undo_stack:
            self._undo_stack.undo()

    def _redo(self):
        if self._undo_stack:
            self._undo_stack.redo()

    def get_undo_action(self) -> QtWidgets.QAction:
        return self._undo_action

    def get_redo_action(self) -> QtWidgets.QAction:
        return self._redo_action

    def set_root_flow(self, flow: Optional[Flow]):
        """Convenience method for setting the undo stack via a flow."""
        if flow is None:
            self.set_undo_stack(None)
        else:
            self.set_undo_stack(flow.undo_stack())

    def set_undo_stack(self, undo_stack: Optional[UndoStack]):
        logger.debug("Setting undo stack to %s", undo_stack)
        if self._undo_stack:
            self._undo_stack.index_changed.remove_handler(
                self._handle_index_changed)

        self._undo_stack = undo_stack
        self.model().set_undo_stack(undo_stack)

        if self._undo_stack:
            self._undo_stack.index_changed.add_handler(
                self._handle_index_changed)
        self._update_actions()
