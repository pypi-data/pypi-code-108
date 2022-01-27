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
"""Keymaps"""
import Qt.QtGui as QtGui
import Qt.QtCore as QtCore

from sympathy.utils import prim


class Default:
    """
    Default key map.

    Attribute values are shortcuts (QKeySequence) for standard actions.

    Other key map implementations should provide the same attribute names, but
    can use different shortcuts. Any key map should avoid using the same
    shortcut for different attributes that are likely to be used in the same
    context.

    It is up to the user to ensure that conflicting sequences are not used in
    the same shortcut context. For example, new_flow and new_item.
    """

    def __init__(self):
        # File menu
        self.new_flow = QtGui.QKeySequence.New
        self.open_flow = QtGui.QKeySequence.Open
        self.save_flow = QtGui.QKeySequence.Save
        self.save_flow_as = QtGui.QKeySequence.SaveAs

        self.new_library = None
        self.new_node = None
        self.new_function = None

        self.reload_library = QtGui.QKeySequence('Ctrl+Shift+R')

        if prim.is_osx():
            # Use same shortcut as finder and safari
            self.fullscreen = QtGui.QKeySequence("Ctrl+Shift+F")
        else:
            self.fullscreen = QtGui.QKeySequence(QtCore.Qt.Key_F11)

        self.preferences = QtGui.QKeySequence.Preferences

        self.close_flow = QtGui.QKeySequence.Close
        self.quit = QtGui.QKeySequence.Quit

        # Edit menu
        self.undo = QtGui.QKeySequence.Undo
        self.redo = QtGui.QKeySequence.Redo

        self.select_all = QtGui.QKeySequence.SelectAll
        self.cut = QtGui.QKeySequence.Cut
        self.copy = QtGui.QKeySequence.Copy
        self.paste = QtGui.QKeySequence.Paste
        self.delete = QtGui.QKeySequence.Delete

        self.insert_node = QtGui.QKeySequence(
            int(QtCore.Qt.CTRL) + int(QtCore.Qt.SHIFT) +
            int(QtCore.Qt.Key_N))
        self.find_node = QtGui.QKeySequence.Find

        self.selection_tool = None
        self.panning_tool = None

        # Control menu
        self.execute_flow = QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.profile_flow = QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_P)
        self.stop = None
        self.reload_flow = QtGui.QKeySequence(
            int(QtCore.Qt.CTRL) + int(QtCore.Qt.ALT) +
            int(QtCore.Qt.Key_R))

        # View menu
        self.zoom_in = QtGui.QKeySequence.ZoomIn
        self.zoom_out = QtGui.QKeySequence.ZoomOut
        self.zoom_default = QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_0)
        self.zoom_fit_all = QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_2)
        self.zoom_fit_selection = QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_1)

        self.toggle_grid = QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.ALT + QtCore.Qt.Key_G)

        # Mouse bindings in flowview

        # Flow
        self.auto_connect_mode = QtGui.QKeySequence(
            QtCore.Qt.Key_Shift)
        self.auto_connect_make_connection = QtGui.QKeySequence("c")

        # Containers: lists, tables, etc.
        self.delete_item = QtGui.QKeySequence.Delete
        self.new_item = QtGui.QKeySequence.StandardKey.New


def get_active_keymap():
    return Default()
