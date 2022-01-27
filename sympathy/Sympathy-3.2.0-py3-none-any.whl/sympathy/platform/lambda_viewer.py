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

from .viewerbase import ViewerBase


class LambdaViewer(ViewerBase):
    def __init__(self, data=None, console=None, parent=None):
        super().__init__(parent)

        self._name_label = QtWidgets.QLabel()
        self._identifier_label = QtWidgets.QLabel()
        self.update_data(data)

        layout = QtWidgets.QFormLayout()
        layout.addRow('Name', self._name_label)
        layout.addRow('Full UUID', self._identifier_label)
        self.setLayout(layout)

    def data(self):
        return self._data

    def update_data(self, data):
        self._data = data
        if data is not None:
            try:
                flow, ports = data.get()
                self._name_label.setText(self._data.name())
                self._identifier_label.setText(self._data.identifier())
            except ValueError:
                pass
