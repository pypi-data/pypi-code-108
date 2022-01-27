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
import json
from Qt import QtWidgets
from . import widget_library as sywidgets
from .viewerbase import ViewerBase


class JsonViewer(ViewerBase):
    def __init__(self, data=None, console=None, parent=None):
        super().__init__(parent)
        self._data = data
        self._text_edit = sywidgets.SyTextEdit(self._text())
        self._text_edit.setReadOnly(True)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._text_edit)
        self.setLayout(layout)

    def _text(self):
        if self._data is not None:
            try:
                return json.dumps(self._data.get(), indent=4, sort_keys=True)
            except ValueError:
                pass
        return ''

    def data(self):
        return self._data()

    def update_data(self, data):
        self._data = data
        self._text_edit.setText(self._text())
