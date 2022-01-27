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
import warnings

# Ignore a warning from numpy>=1.14 when importing h5py<=2.7.1:
with warnings.catch_warnings():
    warnings.simplefilter('ignore', FutureWarning)
    import h5py

from sympathy.api import importers
from sympathy.api import adaf
from sympathy.api import qt2 as qt_compat
from sympathy.api.exceptions import SyDataError
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')


class ImportWidget(QtWidgets.QWidget):

    def __init__(self, parameters, fq_infilename):
        super(ImportWidget, self).__init__()
        self._filename = fq_infilename
        self._parameters = parameters
        self._init_gui()

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self._parameters['import_links'].gui())
        self.setLayout(vlayout)


class DataImporterADAF(importers.ADAFDataImporterBase):
    """Importer for an ADAF file. This is a special class and does
    not have a valid import_data method."""
    IMPORTER_NAME = "ADAF"
    DISPLAY_NAME = "SyData"

    def __init__(self, fq_infilename, parameters):
        super(DataImporterADAF, self).__init__(fq_infilename, parameters)
        if parameters is not None:
            self._init_parameters()

    def valid_for_file(self):
        if h5py.is_hdf5(self._fq_infilename):
            with h5py.File(self._fq_infilename, 'r') as f:
                if {'meta', 'root'}.difference(f.keys()) != set():
                    return False
                if not ('sys' in f or 'tb' in f):
                    return False

            if not adaf.is_adaf('hdf5', self._fq_infilename):
                return False
            return True

        return False

    def is_type(self):
        return True

    def import_data(self, out_datafile, parameters=None, progress=None):
        raise self.invalid_file(self._fq_infilename)

    def _init_parameters(self):
        parameters = self._parameters

        # Init headers checkbox
        if 'import_links' not in parameters:
            parameters.set_boolean(
                'import_links', value=False,
                label='Import with links to source file',
                description=(
                    'Import with links to source file, this file and '
                    'any files that it may link to  must not be moved '
                    'while the flow is opened.'))

    def parameter_view(self, parameters):
        return ImportWidget(parameters, self._fq_infilename)

    @property
    def import_links(self):
        return self._parameters['import_links'].value
