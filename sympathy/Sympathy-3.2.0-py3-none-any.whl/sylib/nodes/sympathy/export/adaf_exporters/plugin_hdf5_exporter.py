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
from sympathy.api import adaf
from sylib.export import adaf as exportadaf
from sympathy.api import qt2 as qt_compat
QtGui = qt_compat.import_module('QtGui')


class DataExportHDF5Widget(exportadaf.TabbedDataExportWidget):
    pass


class DataExportHDF5(exportadaf.TabbedADAFDataExporterBase):
    """Exporter for HDF5 files."""
    EXPORTER_NAME = "HDF5"
    DISPLAY_NAME = 'SyData'
    FILENAME_EXTENSION = 'sydata'

    def __init__(self, parameters):
        super(DataExportHDF5, self).__init__(parameters)

    def parameter_view(self, input_list):
        return DataExportHDF5Widget(self._parameters,
                                    input_list)

    def export_data(self, adafdata, fq_outfilename, progress=None):
        """Export ADAF to HDF5."""
        with adaf.File(filename=fq_outfilename, mode='w',
                       source=adafdata):
            pass
        progress(100.)
