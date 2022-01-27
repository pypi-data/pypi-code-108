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
    warnings.simplefilter('ignore')
    import h5py

from sympathy.api import importers
from sympathy.api import table
from sympathy.api.exceptions import SyDataError


def all_equal(iterator):
    try:
        iterator = iter(iterator)
        first = next(iterator)
        return all(first == rest for rest in iterator)
    except StopIteration:
        return True


class DataImportTable(importers.TableDataImporterBase):
    """Importer for Table files."""
    IMPORTER_NAME = "Table"
    DISPLAY_NAME = 'SyData'

    def __init__(self, fq_infilename, parameters):
        super(DataImportTable, self).__init__(fq_infilename, parameters)

    def name(self):
        return self.IMPORTER_NAME

    def valid_for_file(self):
        """Is fq_filename a valid Table."""
        try:
            can_open_hdf5 = h5py.is_hdf5(self._fq_infilename)
        except Exception:
            can_open_hdf5 = False

        if can_open_hdf5:
            if self.is_type():
                return True
            valid = True
            # Fallback method of determining if the data can be considered a
            # table by data inspection. Can be useful for reading data from
            # other programs that have the right form.
            with h5py.File(self._fq_infilename, 'r') as infile:
                # Filter reserved items
                items = [infile[name] for name in infile
                         if not name.startswith('__sy_')]
                # All remaining items must be datasets.
                valid &= all([isinstance(ds, h5py.Dataset) for ds in items])

                # All datasets must have the same length.
                valid &= all_equal([len(ds) for ds in items])
            return valid
        return False

    def is_type(self):
        if not table.is_table('hdf5', self._fq_infilename):
            return False
        return True

    def import_data(self, out_file, parameters=None, progress=None):
        raise self.invalid_file(self._fq_infilename)
