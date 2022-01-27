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
from sympathy.api.exceptions import SyConfigurationError
from sympathy.api import qt2 as qt_compat
from sylib.export import table as exporttable

QtWidgets = qt_compat.import_module('QtWidgets')


class DataExportXLSWidget(QtWidgets.QWidget):
    def __init__(self, parameter_root, input_list):
        super(DataExportXLSWidget, self).__init__()
        self._parameter_root = parameter_root
        self._init_gui()

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self._parameter_root['header'].gui())
        self.setLayout(vlayout)


class DataExportXLS(exporttable.TableDataExporterBase):
    """Exporter for XLS files."""
    EXPORTER_NAME = 'XLS'
    FILENAME_EXTENSION = 'xls'

    def __init__(self, parameters):
        super(DataExportXLS, self).__init__(parameters)

        if 'header' not in parameters:
            parameters.set_boolean(
                'header', value=True, label='Export header',
                description='Export column names')

    def parameter_view(self, input_list):
        return QtWidgets.QLabel(
            "Support for legacy Excel file format (XLS) has been removed "
            "from Sympathy 2.0.0. Please use the newer Excel file format "
            "(XLSX) instead.")

    def export_data(self, in_sytable, fq_outfilename, progress=None):
        raise SyConfigurationError(
            "Support for legacy Excel file format (XLS) has been removed "
            "from Sympathy 2.0.0. Please use the newer Excel file format "
            "(XLSX) instead.")
