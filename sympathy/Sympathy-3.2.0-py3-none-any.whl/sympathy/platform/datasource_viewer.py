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
import numpy as np
from sympathy.api import table
from .viewerbase import ViewerBase
from .table_viewer import TableViewer
from sympathy.api import qt2 as qt

QtCore = qt.QtCore
QtGui = qt.import_module('QtGui')
QtWidgets = qt.import_module('QtWidgets')


def create_table_from_datasource(ds):
    ds_path = np.array([ds.decode_path() or ''])
    ds_type = np.array([ds.decode_type() or ''])
    return table.File.from_recarray(
        np.rec.array((ds_path, ds_type), names=('path', 'type')))


class DatasourceViewer(ViewerBase):
    def __init__(self, datasource_data=None, console=None, parent=None):
        super().__init__(parent)

        self._datasource = datasource_data
        self._viewer = None

        self._init_gui()
        try:
            self.update_data(self._datasource)
        except Exception:
            self._datasource.encode_path('')
            self.update_data(self._datasource)

    def datasource(self):
        return self._datasource

    def data(self):
        return self.datasource()

    def update_data(self, data):
        if data is not None:
            self._datasource = data
            self._viewer.update_data(
                create_table_from_datasource(data))

    def _init_gui(self):
        layout = QtWidgets.QVBoxLayout()
        self._viewer = TableViewer(plot=False)
        self._viewer.show_colors(False)
        layout.addWidget(self._viewer)
        self.setLayout(layout)
