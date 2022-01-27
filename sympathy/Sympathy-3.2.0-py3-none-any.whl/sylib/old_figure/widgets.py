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

from . import colors
from sylib.icons import utils as icon_utils
from sylib.old_tree_model import widgets as tree_widgets
from sympathy.api import qt2 as qt
from sympathy.platform import widget_library as sywidgets

QtCore = qt.QtCore
QtGui = qt.QtGui
QtWidgets = qt.QtWidgets


class _SyColorEdit(tree_widgets.SyBaseTextEdit):
    def __init__(self, *args, **kwargs):
        super(_SyColorEdit, self).__init__(*args, **kwargs)

        icon = icon_utils.create_icon(icon_utils.SvgIcon.color)
        self.toolbutton = sywidgets.LineEditDropDownMenuButton(
            icon, parent=self)
        self.toolbutton.setPopupMode(QtWidgets.QToolButton.DelayedPopup)
        self.toolbutton.setToolTip('<p>Select a color.</p>')
        self.add_widget(self.toolbutton)
        self.drop_down_menu = QtWidgets.QMenu(parent=self)
        self.toolbutton.setMenu(self.drop_down_menu)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.toolbutton.clicked.connect(self._on_color_pick)
        self.textChanged.connect(self._eval_color)

        self.populate_drop_down_menu()
        self.drop_down_menu.triggered.connect(self.insert_action_text)

    def populate_drop_down_menu(self):
        color_names = sorted(colors.COLORS.keys())
        for name in color_names:
            color = colors.COLORS[name]
            icon = icon_utils.color_icon(color)
            self.drop_down_menu.addAction(icon, name)

    def focusOutEvent(self, event):
        # workaround to prevent the widget to lose focus if the color pick
        # dialog or drop down menu is used
        if self.drop_down_menu.isVisible():
            return
        if not self.keep_focus and event.lostFocus() and not self.underMouse():
            self.parent_view_widget.end_edit()
        super(_SyColorEdit, self).focusOutEvent(event)

    def insert_action_text(self, action):
        self.set_value(action.text())

    def _eval_color(self):
        text = self.toPlainText()
        color = colors.parse_to_mpl_color(text)
        self._update_button_color(color)

    def _on_color_pick(self):
        self.keep_focus = True
        # store old value and type
        try:
            old_value = self.get_value()
            old_color_dev = colors.get_color_dev(old_value)
            color = colors.get_color_as_rgba_f(old_value)
        except ValueError:
            old_color_dev = 'rgbF'
            color = None
        if color is None:
            color = [1., 0., 0.]
        color = np.array(color) * 255
        qcolor = QtGui.QColor(*color.astype(int))
        # create dialog
        dialog = QtWidgets.QColorDialog(qcolor, parent=self)
        color = dialog.getColor()

        if not color.isValid():
            return
        if old_color_dev == 'name':
            color_name = mpl_colors.rgb2hex(color.getRgbF())
            new_value = colors.COLORS_INV.get(color_name, color_name)
        elif old_color_dev in ['rgbf', 'rgbaf']:
            new_value = color.getRgbF()
            new_value = [round(i, 2) for i in new_value]
        elif old_color_dev in ['rgb', 'rgba']:
            new_value = color.getRgb()
        elif old_color_dev == 'hex':
            new_value = mpl_colors.rgb2hex(color.getRgbF())
        else:
            new_value = color.name()
        self.set_value(new_value)
        self.keep_focus = False

    def _update_button_color(self, value):
        if value is not None:
            icon = icon_utils.color_icon(str(value))
        else:
            icon = icon_utils.create_icon(icon_utils.SvgIcon.color)
        self.toolbutton.setIcon(icon)


# The _SyMPLColorEdit has to wrapped in a QWidget so the widget doesn't lose
# focus when the QColorDialog is shown.
class SyColorEdit(QtWidgets.QWidget, tree_widgets.SyBaseEditMixin):
    def __init__(self, *args, **kwargs):
        super(SyColorEdit, self).__init__(*args, **kwargs)
        kwargs['parent'] = self
        self._textedit = _SyColorEdit(*args, **kwargs)

        self.setFixedHeight(self.sizeHint().height())

        self.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._textedit)
        self.setLayout(layout)

        self._completer = None
        self.parent_view_widget = None
        self.setFocusProxy(self._textedit)

    def sizeHint(self):
        return self._textedit.sizeHint()

    def set_completer(self, c):
        self._textedit.set_completer(c)

    def set_value(self, value):
        self._textedit.set_value(str(value))

    def get_value(self):
        return str(self._textedit.get_value())

    def set_parent_view_widget(self, widget):
        self.parent_view_widget = widget
        self._textedit.set_parent_view_widget(self.parent_view_widget)
