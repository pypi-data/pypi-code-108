# This file is part of Sympathy for Data.
# Copyright (c) 2020 Combine Control Systems AB
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
from sympathy.app import settings
from Qt import QtWidgets


class EditorValue:
    def __init__(self, editor):
        self._editor = editor

    def get(self):
        raise NotImplementedError()

    def set(self, value):
        raise NotImplementedError()


class CheckBoxValue(EditorValue):
    def get(self):
        return self._editor.isChecked()

    def set(self, value):
        self._editor.setChecked(value)


class ComboBoxValue(EditorValue):
    def get(self):
        return self._editor.currentText()

    def set(self, value):
        i = self._editor.findText(value)
        if i < 0:
            assert False, 'Setting invalid value'
        self._editor.setCurrentIndex(i)


class LineEditValue(EditorValue):
    def get(self):
        return self._editor.text()

    def set(self, value):
        self._editor.setText(value)


class SpinBoxValue(EditorValue):
    def get(self):
        return self._editor.value()

    def set(self, value):
        self._editor.setValue(value)


class ListValue(EditorValue):
    def get(self):
        return [self._editor(i).text()
                for i in range(self._editor.count())]

    def set(self, value):
        self._editor.clear()
        for text in value:
            item = QtWidgets.QListWidgetItem(text)
            self._editor.addItem(item)


class SettingsEditor:

    _editor_value_cls: EditorValue = None

    def __init__(self, param, *args, **kwargs):
        self._param = param
        super().__init__(*args, **kwargs)
        self._editor_value_obj = self._editor_value_cls(self)
        # Subclass should call update_value() appropriately.

    def _settings_value(self):
        return settings.instance()[self._param]

    def editor_value(self):
        return self._editor_value_obj.get()

    def update_value(self):
        self._editor_value_obj.set(self._settings_value())

    def dirty(self):
        return self.editor_value() != self._settings_value()

    def save(self):
        settings.instance()[self._param] = self.editor_value()


class BasicSettingsEditor(SettingsEditor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_value()


class StringComboBox(SettingsEditor, QtWidgets.QComboBox):
    _editor_value_cls = ComboBoxValue

    def __init__(self, param, options, parent=None):
        super().__init__(param, parent=parent)
        self.addItems(options)
        self.update_value()


class BoolCheckBox(BasicSettingsEditor, QtWidgets.QCheckBox):
    _editor_value_cls = CheckBoxValue


class IntegerSpinBox(BasicSettingsEditor, QtWidgets.QSpinBox):
    _editor_value_cls = SpinBoxValue


class StringLineEdit(BasicSettingsEditor, QtWidgets.QLineEdit):
    _editor_value_cls = LineEditValue


class ListEdit(BasicSettingsEditor, QtWidgets.QListWidget):
    _editor_value_cls = ListValue


class EmailWidget(StringLineEdit):
    def __init__(self, parent=None):
        super().__init__(settings.Keys.user_email, parent=parent)
        self.setPlaceholderText('Your email address')
        self.setToolTip(
            'Please enter a valid email if you want to send an issue')
