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
from sympathy.api import qt2 as qt_compat
from sympathy.api import table
from sylib.export import table as exporttable

QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')


class DataExportHDF5Widget(QtWidgets.QWidget):
    filename_changed = qt_compat.Signal()

    def __init__(self, parameter_root, *args, **kwargs):
        super(DataExportHDF5Widget, self).__init__(*args, **kwargs)
        self._parameter_root = parameter_root

        self._init_gui()

    def _init_gui(self):
        table_names_gui = self._parameter_root['table_names'].gui()
        table_names_gui.valueChanged.connect(self._filename_changed)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(table_names_gui)
        self.setLayout(vlayout)

    def _filename_changed(self):
        self.filename_changed.emit()


class DataExportHDF5(exporttable.TableDataExporterBase):
    """Exporter for HDF5 files."""
    EXPORTER_NAME = "HDF5"
    DISPLAY_NAME = "SyData"
    FILENAME_EXTENSION = "sydata"

    def __init__(self, parameters):
        super(DataExportHDF5, self).__init__(parameters)
        if 'table_names' not in parameters:
            parameters.set_boolean(
                'table_names', label='Use table names as filenames',
                description='Use table names as filenames')

    def parameter_view(self, node_context_input):
        return DataExportHDF5Widget(self._parameters)

    def export_data(self, in_sytable, fq_outfilename, progress=None):
        """Export Table to HDF5."""
        with table.File(filename=fq_outfilename, mode='w',
                        source=in_sytable):
            pass
