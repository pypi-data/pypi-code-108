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
from sylib.export import table as exporttable
from sylib.matlab import matlab
from sympathy.api import qt2 as qt_compat

QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')


class DataExportMATWidget(QtWidgets.QWidget):
    filename_changed = qt_compat.Signal()

    def __init__(self, parameter_root, *args, **kwargs):
        super(DataExportMATWidget, self).__init__(*args, **kwargs)
        self._parameter_root = parameter_root
        self._init_gui()

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        table_names_gui = self._parameter_root['table_names'].gui()
        table_names_gui.valueChanged.connect(self._filename_changed)
        vlayout.addWidget(table_names_gui)
        vlayout.addWidget(self._parameter_root['header'].gui())
        self.setLayout(vlayout)

    def _filename_changed(self):
        self.filename_changed.emit()


class DataExportMAT(exporttable.TableDataExporterBase):
    """Exporter for MAT files."""

    EXPORTER_NAME = "MAT"
    FILENAME_EXTENSION = "mat"

    def __init__(self, parameters):
        super(DataExportMAT, self).__init__(parameters)
        if 'table_names' not in parameters:
            parameters.set_boolean(
                'table_names', label='Use table names as filenames',
                description='Use table names as filenames')
        if 'header' not in parameters:
            parameters.set_boolean(
                'header', value=True, label='Export header',
                description='Export column names')

    def parameter_view(self, node_context_input):
        return DataExportMATWidget(self._parameters)

    def export_data(self, in_sytable, fq_outfilename, progress=None):
        """Export Table to MAT."""
        header = self._parameters['header'].value
        matlab.write_table_to_matfile(in_sytable, fq_outfilename, header)
