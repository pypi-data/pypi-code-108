# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
from Qt import QtWidgets
from . import widget_library as sywidgets
from .viewerbase import ViewerBase


class TextViewer(ViewerBase):
    def __init__(self, text_data=None, console=None, parent=None):
        super().__init__(parent)
        self._text = text_data

        self._text_edit = sywidgets.SyTextEdit(
            '' if text_data is None else text_data.get())
        self._text_edit.setReadOnly(True)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._text_edit)
        self.setLayout(layout)

    def text(self):
        return self._text

    def data(self):
        return self.text()

    def update_data(self, data):
        if data is not None:
            self._text_edit.setPlainText(data.get())
