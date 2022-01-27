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
import itertools
from sylib.icons import utils as icon_utils
from sympathy.api import qt2 as qt
from sympathy.platform import widget_library as sywidgets
from sympathy.utils import complete

QtCore = qt.QtCore
QtGui = qt.QtGui
QtWidgets = qt.QtWidgets


class SyBaseEditMixin(object):
    def set_options(self, options):
        pass

    def set_completer(self, completer):
        pass

    def completer(self):
        return None

    def set_parent_view_widget(self, widget):
        pass

    def select_text(self):
        pass


class SyTopEditMixin(SyBaseEditMixin):
    def set_value_eval(self, value, eval):
        pass

    def get_value_eval(self):
        return None


# All tree model editors should inherit this class to function with the
# tree_model.qt_model.ParameterTreeDelegate.

class SySubEditMixin(SyBaseEditMixin):
    def set_value(self, value):
        pass

    def get_value(self):
        return None

    def allow_focus_out(self, reason):
        return True


class SyBaseTextEdit(sywidgets.BaseLineTextEdit, SySubEditMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTabChangesFocus(True)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFixedHeight(self.sizeHint().height())
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Fixed)

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            event.ignore()
        else:
            super().keyPressEvent(event)

    def set_value(self, value):
        self.setPlainText(str(value))

    def get_value(self):
        return self.toPlainText()

    def set_options(self, options):
        # implement in subclasses if needed
        pass

    def select_text(self):
        self.selectAll()


class SyStackedPythonEdit(QtWidgets.QWidget, SyTopEditMixin):
    def __init__(self, value_editor_cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._code_edit = SyDropDownCodeEdit(parent=self)
        self._active_icon = icon_utils.create_icon(icon_utils.SvgIcon.python)
        self._tooltip = ("Toggle this button to choose if this field "
                         "should be evaluated as Python or as a simple "
                         "value.\n\nCurrently: {}")
        self._eval_names = {
            'py': 'Python',
            'value': 'Value'}

        if value_editor_cls is None:
            self._can_switch_icon = False
            self._sub_editor = None
            self._toolbutton = QtWidgets.QLabel()
            active_pixmap = self._active_icon.pixmap(QtCore.QSize(14, 14))
            self._toolbutton.setPixmap(active_pixmap)
            self._inactive_icon = None
        else:
            self._can_switch_icon = True
            self._sub_editor = value_editor_cls()
            self._toolbutton = QtWidgets.QToolButton()
            self._inactive_icon = icon_utils.create_icon(
                icon_utils.SvgIcon.python_grayscale)
            self._toolbutton.setIcon(self._inactive_icon)
            self._toolbutton.setIconSize(QtCore.QSize(14, 14))
            self._toolbutton.setCheckable(True)
            self._toolbutton.setChecked(False)
            self._toolbutton.toggled.connect(self.toggle_python)
        self._toolbutton.setToolTip(self._get_tooltip())

        self._stacked = QtWidgets.QStackedWidget()
        if self._sub_editor is not None:
            self._stacked.addWidget(self._sub_editor)
        self._stacked.addWidget(self._code_edit)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stacked)
        layout.addWidget(self._toolbutton)
        self.setLayout(layout)

        # Event filters are needed for the editor to close when it should. See
        # explanation in self.eventFilter
        self._code_edit.installEventFilter(self)
        self._toolbutton.installEventFilter(self)
        if self._sub_editor is not None:
            self._sub_editor.installEventFilter(self)

        self.toggle_python(self._sub_editor is None)

    def eventFilter(self, obj, event):
        # The default event filter of QStyledItemDelegate is looking for
        # FocusOut events from the editor widget to close the editor, but it
        # can't see any events from child widgets, so we propagate them here.
        if event.type() == QtCore.QEvent.FocusOut:
            try:
                allow = obj.allow_focus_out(event.reason())
            except AttributeError:
                allow = True
            if obj is self._code_edit or allow:
                QtWidgets.QApplication.postEvent(
                    self, QtGui.QFocusEvent(event.type(), event.reason()))
        return super().eventFilter(obj, event)

    def _get_tooltip(self):
        if self._sub_editor is None:
            return "This field is always evaluated as Python."
        else:
            return self._tooltip.format(
                self._eval_names[self._get_eval_toggle()])

    def _set_eval_toggle(self, eval):
        if self._sub_editor is not None:
            checked_state = eval == 'py'
            self._toolbutton.setChecked(checked_state)

    def _get_eval_toggle(self):
        if self._sub_editor is None:
            return 'py'
        elif self._toolbutton.isChecked():
            return 'py'
        else:
            return 'value'

    def toggle_python(self, state):
        if state:
            current_icon = self._active_icon
            current = self._code_edit
        else:
            current_icon = self._inactive_icon
            current = self._sub_editor
        if self._can_switch_icon:
            self._toolbutton.setIcon(current_icon)
        self._stacked.setCurrentWidget(current)
        self.setFocusProxy(current)
        self._toolbutton.setToolTip(self._get_tooltip())

    def set_options(self, options):
        if self._sub_editor is not None:
            self._sub_editor.set_options(options)

    def set_completer(self, completer):
        self._code_edit.set_completer(completer)
        if self._sub_editor is not None:
            self._sub_editor.set_completer(completer)

    def get_value_eval(self):
        if self._get_eval_toggle() == 'py':
            return self._code_edit.toPlainText(), 'py'
        else:
            return self._sub_editor.get_value(), 'value'

    def set_value_eval(self, value, eval):
        self._set_eval_toggle(eval)
        if eval == 'value':
            self._sub_editor.set_value(value)
        elif eval == 'py':
            self._code_edit.setPlainText(value)

    def set_parent_view_widget(self, widget):
        self._code_edit.set_parent_view_widget(widget)

    def select_text(self):
        current = self._stacked.currentWidget()
        if current:
            current.select_text()


class SyDropDownCodeEdit(sywidgets.BaseLineCodeEdit, SySubEditMixin):
    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)

        icon = icon_utils.create_icon(icon_utils.SvgIcon.plus)
        self.toolbutton = sywidgets.LineEditDropDownMenuButton(
            icon, parent=self)
        self.toolbutton.setToolTip('<p>Inserts the selected expression.</p>')
        self.toolbutton.setEnabled(False)
        self.add_widget(self.toolbutton)
        self.drop_down_menu = QtWidgets.QMenu(parent=self)
        self.drop_down_menu.setStyleSheet("QMenu {menu-scrollable: 1;}")
        self.toolbutton.setMenu(self.drop_down_menu)

        self._completer = None

    def keyPressEvent(self, event):
        # always ignore return and enter keys
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            if self._completer and self._completer.popup().isVisible():
                event.ignore()
                return
            else:
                if self.parent_view_widget is not None:
                    self.parent_view_widget.end_edit()
                return

        if (self._completer and self._completer.popup() and
                self._completer.popup().isVisible()):
            # The following keys are forwarded by the completer to the widget
            if event.key() in [QtCore.Qt.Key_Enter,
                               QtCore.Qt.Key_Return,
                               QtCore.Qt.Key_Escape,
                               QtCore.Qt.Key_Tab,
                               QtCore.Qt.Key_Backtab]:
                event.ignore()
                return

        # check the shortcut combination Ctrl+R
        is_shortcut = (event.modifiers() == QtCore.Qt.ControlModifier and
                       event.key() == QtCore.Qt.Key_R)

        if not self._completer or not is_shortcut:
            super().keyPressEvent(event)

        no_text = event.text() == ''
        ctrl_or_shift = event.modifiers() in (QtCore.Qt.ControlModifier,
                                              QtCore.Qt.ShiftModifier)
        if ctrl_or_shift and no_text:
            # ctrl or shift key on it's own
            return

        if not is_shortcut:
            if (self._completer and self._completer.popup() and
                    self._completer.popup().isVisible()):
                self._completer.popup().hide()

        completion_prefix = self.text_under_cursor()

        if event.key() == QtCore.Qt.Key_Escape:
            # Extra safeguard: Avoid creating new popup when escape is pressed.
            # Creating the popup while at the same time stopping the edit
            # results in a floating (no valid parent) widget and then a crash
            # when interacting with it.
            return

        # only start if at lest one letter is typed
        if self._completer is not None:
            if len(completion_prefix) > 0:
                self._completer.setCompletionPrefix(completion_prefix)
                popup = self._completer.popup()
                popup.setCurrentIndex(
                    self._completer.completionModel().index(0, 0))
                cr = self.cursorRect()
                cr.setWidth(popup.sizeHintForColumn(0) +
                            popup.verticalScrollBar().sizeHint().width())
                self._completer.complete(cr)  # popup it up!

    def insert_completion(self, completion):
        if self._completer.widget() is not self:
            return
        if (len(self.text_right_of_cursor()) and
                self.text_right_of_cursor()[0] != ' '):
            # Do not insert completion if there is anything but whitespace
            # after the cursor.
            return
        tc = self.textCursor()
        completion_prefix = self._completer.completionPrefix()
        tc.movePosition(QtGui.QTextCursor.Left,
                        QtGui.QTextCursor.KeepAnchor, len(completion_prefix))
        tc.removeSelectedText()
        tc.insertText(completion)

        self.setTextCursor(tc)

    def text_under_cursor(self):
        tc = self.textCursor()
        text = self.toPlainText()
        pos = tc.position()
        return complete.name_prefix_at_pos(text, pos)

    def text_right_of_cursor(self):
        tc = self.textCursor()
        text = self.toPlainText()
        pos = tc.position()
        return text[pos:]

    def insert_action_text(self, action):
        tc = self.textCursor()
        tc.insertText(action.text())
        self.setTextCursor(tc)

    def set_options(self, options):
        pass

    def set_completer(self, completer):
        if self._completer:
            self._completer.disconnect(self)
        self._completer = completer

        if not self._completer:
            return

        self._completer.setWidget(self)
        self._completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.insert_text.connect(self.insert_completion)

        items = list(itertools.islice(completer.model().calc_names(), 0, 100))
        self.toolbutton.setEnabled(len(items) > 0)
        for item in items:
            action = QtWidgets.QAction(item, self.drop_down_menu)
            self.drop_down_menu.addAction(action)
        self.drop_down_menu.triggered.connect(self.insert_action_text)

    def completer(self):
        return self._completer

    def set_value(self, value):
        self.setPlainText(str(value))

    def get_value(self):
        return self.toPlainText()

    def set_parent_view_widget(self, widget):
        self.parent_view_widget = widget

    def select_text(self):
        self.selectAll()


class SyLabelEdit(SyBaseTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        icon = icon_utils.create_icon(icon_utils.SvgIcon.plus)
        self.toolbutton = sywidgets.LineEditDropDownMenuButton(
            icon, parent=self)
        self.toolbutton.setToolTip('<p>Inserts the selected name.</p>')
        self.toolbutton.setEnabled(False)
        self.add_widget(self.toolbutton)
        self.drop_down_menu = QtWidgets.QMenu(parent=self)
        self.drop_down_menu.setStyleSheet("QMenu {menu-scrollable: 1;}")
        self.toolbutton.setMenu(self.drop_down_menu)

    def insert_action_text(self, action):
        tc = self.textCursor()
        tc.insertText(action.text())
        self.setTextCursor(tc)

    def set_completer(self, completer):
        if completer is None:
            return

        items = list(itertools.islice(completer.model().names(), 0, 100))
        self.toolbutton.setEnabled(len(items) > 0)
        for item in items:
            action = QtWidgets.QAction(item, self.drop_down_menu)
            self.drop_down_menu.addAction(action)
        self.drop_down_menu.triggered.connect(self.insert_action_text)


class SyIterableEdit(QtWidgets.QWidget, SyTopEditMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs['parent'] = self
        self._varedit = SyBaseTextEdit(*args, **kwargs)
        self._varedit.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                    QtWidgets.QSizePolicy.Fixed)
        self._varedit.setMinimumWidth(20)
        self._varedit.setToolTip('Specify the iterables name.')
        self._codeedit = SyStackedPythonEdit(
            value_editor_cls=None, *args, **kwargs)
        self._codeedit.setToolTip('Define the iterable.')

        eq_label = QtWidgets.QLabel(' = ')
        # override background color to hide underlying display widget during
        # editing mode
        eq_label.setStyleSheet("""QLabel {background-color: white;}""")

        self._varedit.installEventFilter(self)
        self._codeedit.installEventFilter(self)

        self.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._varedit)
        layout.addWidget(eq_label)
        layout.addWidget(self._codeedit)
        self.setLayout(layout)

        self._completer = None
        self.parent_view_widget = None

    def eventFilter(self, obj, event):
        # The default event filter of QStyledItemDelegate is looking for
        # FocusOut events from the editor widget to close the editor, but it
        # can't see any events from child widgets, so we propagate them here.
        if event.type() == QtCore.QEvent.FocusOut:
            try:
                allow = obj.allow_focus_out(event.reason())
            except AttributeError:
                allow = True
            if obj is self._codeedit or allow:
                QtWidgets.QApplication.postEvent(
                    self, QtGui.QFocusEvent(event.type(), event.reason()))
        return super().eventFilter(obj, event)

    def set_completer(self, completer):
        self._codeedit.set_completer(completer)

    def set_options(self, options):
        self._codeedit.set_options(options)

    def set_value_eval(self, value, eval):
        if '=' in value:
            name, exp = value.split('=', 1)
        else:
            name = 'e'
            exp = ''
        self._varedit.set_value(str(name.strip()))
        self._codeedit.set_value_eval(str(exp.strip()), 'py')

    def get_value_eval(self):
        name = self._varedit.get_value()
        exp, eval = self._codeedit.get_value_eval()
        return str('{} = {}'.format(name, exp)), eval

    def set_parent_view_widget(self, widget):
        self._codeedit.set_parent_view_widget(widget)

    def select_text(self):
        self._codeedit.select_text()


class SyComboBox(QtWidgets.QComboBox, SySubEditMixin):
    def set_value(self, value):
        idx = self.findText(value)
        if idx != -1:
            self.setCurrentIndex(idx)
        else:
            self.setCurrentIndex(0)

    def get_value(self):
        return str(self.currentText())

    def set_options(self, options):
        self.clear()
        self.addItems(options)


class SyBoolComboBox(SyComboBox, SySubEditMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addItems(['True', 'False'])

    def set_options(self, options):
        # Options are fixed
        pass


class SyComboBoxEditable(SyComboBox):
    def __init__(self, *args, **kwargs):
        super(SyComboBoxEditable, self).__init__(*args, **kwargs)
        self.setEditable(True)

    def set_value(self, value):
        value = str(value)
        idx = self.findText(value)
        if idx != -1:
            self.setCurrentIndex(idx)
        else:
            self.addItem(value)
            idx = self.findText(value)
            self.setCurrentIndex(idx)

    def select_text(self):
        self.lineEdit().selectAll()


class SyIntLineEdit(sywidgets.ValidatedIntLineEdit, SySubEditMixin):
    def set_value(self, value):
        self.setText(value)

    def get_value(self):
        return str(self.value())

    def select_text(self):
        self.selectAll()


class SyIntSpinBox(sywidgets.ValidatedIntSpinBox, SySubEditMixin):
    def set_value(self, value):
        self.setValue(int(value))

    def get_value(self):
        return str(self.value())

    def set_options(self, options):
        if options is None:
            return
        if len(options) > 0 and options[0] is not None:
            self.setMinimum(int(options[0]))
        if len(options) > 1 and options[1] is not None:
            self.setMaximum(int(options[1]))
        if len(options) > 2 and options[2] is not None:
            self.setSingleStep(int(options[2]))

    def select_text(self):
        self.selectAll()


class SyFloatLineEdit(sywidgets.ValidatedFloatLineEdit, SySubEditMixin):
    def set_value(self, value):
        self.setText(value)

    def get_value(self):
        return str(self.value())

    def select_text(self):
        self.selectAll()


class SyDoubleSpinBox(sywidgets.ValidatedFloatSpinBox, SySubEditMixin):
    def set_value(self, value):
        self.setValue(float(value))

    def get_value(self):
        return str(self.value())

    def set_options(self, options):
        if options is None:
            return
        if len(options) > 0 and options[0] is not None:
            self.setMinimum(float(options[0]))
        if len(options) > 1 and options[1] is not None:
            self.setMaximum(float(options[1]))
        if len(options) > 2 and options[2] is not None:
            self.setSingleStep(float(options[2]))

    def select_text(self):
        self.selectAll()


class SyCheckBox(QtWidgets.QCheckBox, SySubEditMixin):
    def set_value(self, value):
        self.setChecked(bool(value))

    def get_value(self):
        return str(self.isChecked())


def editor_factory(value_editor_cls, *args, **kwargs):
    if value_editor_cls is SyIterableEdit:
        return SyIterableEdit(*args, **kwargs)
    return SyStackedPythonEdit(
        value_editor_cls=value_editor_cls, *args, **kwargs)
