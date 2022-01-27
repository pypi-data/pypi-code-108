# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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


class ViewerBase(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def update_data(self, data):
        raise NotImplementedError('Not implemented in base class')

    def data(self):
        raise NotImplementedError('Not implemented in base class')

    def custom_menu_items(self):
        return []
