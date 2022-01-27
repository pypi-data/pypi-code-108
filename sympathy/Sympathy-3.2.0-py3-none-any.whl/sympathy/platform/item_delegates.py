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
"""
Gather various item delegates to encourage sharing.
"""
from . import widget_library as sywidgets
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets
import Qt.QtGui as QtGui

EditRole = QtCore.Qt.EditRole
DisplayRole = QtCore.Qt.DisplayRole


class UniqueItemDelegate(QtWidgets.QItemDelegate):
    """
    Ensure values in column are not duplicated.
    """
    def createEditor(self, parent, option, index):
        model = index.model()
        values = [model.data(model.index(row, index.column()),
                             EditRole)
                  for row in range(model.rowCount())]
        del values[index.row()]
        values = set(values)

        def unique_validator(value):
            try:
                valid = value not in values
                if not valid:
                    raise sywidgets.ValidationError(
                        f'"{value}" is not a unique value')
            except Exception as e:
                raise sywidgets.ValidationError(str(e))
            return value

        editor = sywidgets.ValidatedTextLineEdit(parent=parent)
        editor.setBuilder(unique_validator)
        return editor

    def setEditorData(self, editor, index):
        data = index.model().data(index, EditRole)
        if data is None:
            text = ''
        editor.setText(str(data or ''))
        editor.selectAll()

    def setModelData(self, editor, model, index):
        value = editor.value()
        index.model().setData(index, value, EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
