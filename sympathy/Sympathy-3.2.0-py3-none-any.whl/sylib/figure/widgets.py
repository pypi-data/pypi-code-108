# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
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
import numpy as np
from matplotlib import colors as mpl_colors

from sylib.figure import colors
from sylib.icons import utils as icon_utils
from sylib.tree_model import widgets as tree_widgets
from sympathy.api import qt2 as qt
from sympathy.platform import widget_library as sywidgets

QtCore = qt.QtCore
QtGui = qt.QtGui
QtWidgets = qt.QtWidgets


class SyColorEdit(tree_widgets.SyBaseTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        icon = icon_utils.create_icon(icon_utils.SvgIcon.color)
        self.toolbutton = sywidgets.LineEditDropDownMenuButton(
            icon, parent=self)
        self.toolbutton.setToolTip('Click to select a color.')
        self.add_widget(self.toolbutton)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.toolbutton.clicked.connect(self._on_color_pick)
        self.textChanged.connect(self._eval_color)

        self._keep_focus = False

    def allow_focus_out(self, reason):
        # Workaround to prevent the widget from losing focus if the color pick
        # dialog or drop down menu is used
        if reason == QtCore.Qt.ActiveWindowFocusReason and self._keep_focus:
            # Opening the color picker dialog will trigger one FocusOutEvent
            # with ActiveWindowFocusReason, but it will only reach the event
            # filter in SyStackedPythonEdit after _on_color_pick has returned
            # control to the event loop. Therefore we ignore the first such
            # event after each call to _on_color_pick until the timeout event
            # has triggered and reset self._keep_focus to False.
            return False
        return True

    def _eval_color(self):
        text = self.toPlainText()
        color = colors.parse_to_mpl_color(text)
        self._update_button_color(color)

    def _on_color_pick(self):
        # Don't open a new color picker if one has already been opened:
        if self._keep_focus:
            return

        self._keep_focus = True
        # store old value and type
        try:
            old_value = self.get_value()
            color = colors.get_color_as_rgba_f(old_value)
        except ValueError:
            color = [0, 0, 0]
        if color is None:
            color = [0, 0, 0]
        color = np.array(color) * 255
        qcolor = QtGui.QColor(*color.astype(int))
        # create dialog
        dialog = QtWidgets.QColorDialog(qcolor, parent=self)
        dialog.setOptions(QtWidgets.QColorDialog.ShowAlphaChannel)
        color = dialog.getColor()

        # Queue an event which will be handled after possible FocusOutEvents
        QtCore.QTimer.singleShot(0, self._end_color_pick)

        if not color.isValid():
            return
        new_value = mpl_colors.rgb2hex(color.getRgbF())
        self.set_value(new_value)

    def _end_color_pick(self):
        self._keep_focus = False

    def _update_button_color(self, value):
        if value is not None:
            icon = icon_utils.color_icon(str(value))
        else:
            icon = icon_utils.create_icon(icon_utils.SvgIcon.color)
        self.toolbutton.setIcon(icon)
