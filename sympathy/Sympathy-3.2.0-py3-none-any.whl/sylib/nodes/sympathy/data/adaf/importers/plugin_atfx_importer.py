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
import os
import re
import numpy as np
import warnings
import datetime
from collections import OrderedDict

from sylib import atfx
from sympathy.api import table
from sympathy.api import importers
from sympathy.api.nodeconfig import deprecated_warn
from sympathy.api.exceptions import SyDataError


class DataImportATFX(importers.ADAFDataImporterBase):
    """Import exported ATFX data into AFAF format."""
    IMPORTER_NAME = 'ATFX'

    def __init__(self, fq_in_filename, parameters):
        super(DataImportATFX, self).__init__(fq_in_filename, parameters)
        self._adaf = None
        self._asamatf = None
        self.DATA_WRITER_DICT = {}

    def name(self):
        return self.IMPORTER_NAME

    def valid_for_file(self):
        if self._fq_infilename is None or not os.path.isfile(
                self._fq_infilename):
            return False

        sample_size = 256
        result = False
        with open(self._fq_infilename, 'rb') as f:
            string = f.read(sample_size)
            result = re.findall(b'atfx_file', string) != []
        return result

    def import_data(self, out_adaffile, parameters=None, progress=None):
        def check_comps(root, comps):
            """
            Check for existence of the binary files connected to the considered
            atf-file.
            """
            for key, comp in comps.items():

                filename = os.path.join(root, comp['filename'])
                if not os.path.isfile(filename):
                    warnings.warn(
                        'The file {0} could not be found'.format(filename))

        deprecated_warn(
            'Support for ATFX import',
            '4.0.0')
        # Outgoing ADAF structure.
        self._adaf = out_adaffile
        fq_infilename = os.path.abspath(self._fq_infilename)

        try:
            self._model = atfx.ApplicationModel(fq_infilename)
        except atfx.ATFX_ImportFailed as e:
            raise self.import_failed(e)
        self._dirname = os.path.abspath(os.path.dirname(fq_infilename))
        self._comps = self._model.components()
        check_comps(self._dirname, self._comps)

        exporter = self._model.documentation().get('exporter', 'ATFX')
        system = self._adaf.sys.create(exporter)
        # Loop over the existing tests.
        meass = self._model.instances('AoMeasurement')
        meas_names = [meas.name() for meas in meass]
        count = dict.fromkeys(meas_names, 0)
        for meas_name in meas_names:
            count[meas_name] += 1

        meas_offset = {key: 0 if value > 1 else None
                       for key, value in count.items()}

        for meas in meass:
            test = meas

            try:
                while True:
                    test = test.test()
            except AttributeError:
                pass

            for key, value in sorted(test.get_attrs().items()):
                out_adaffile.meta.create_column(
                    '{}_Test_{}'.format(exporter, key), np.array([value]))

        for meas in meass:
            self.add_meas(meas, meas_offset, system)

        out_adaffile.set_source_id(os.path.basename(fq_infilename))

    def add_meas(self, meas, meas_offset, system):
        meas_name = meas.name()
        rasters_dict = OrderedDict()
        indep_dict = {}

        for meas_quantity in (
                meas.measurement_quantities()):
            quantity_name = meas_quantity.name()
            try:
                data, attributes = self.get_quantity(meas_quantity)
            except IOError:
                warnings.warn(
                    'quantity:{} could not be read'.format(quantity_name))
                continue

            for submatrix_id, (indep, array) in data:
                raster = rasters_dict.setdefault(
                    (submatrix_id, meas_name), table.File())

                raster.set_column_from_array(
                    quantity_name, array, attributes)
                if indep:
                    indep_dict[(submatrix_id, meas_name)] = quantity_name

        offset = meas_offset[meas_name]
        many = len(rasters_dict) > 1 or offset is not None
        for i, ((submatrix_id, meas_name), raster) in enumerate(
                rasters_dict.items()):
            i += offset or 0

            if meas_name in self.DATA_WRITER_DICT:
                self.DATA_WRITER_DICT[meas_name](raster, self._adaf)
            else:
                table_attributes = raster.get_table_attributes() or {}
                try:
                    table_attributes[
                        'reference_time'] = datetime.datetime.strptime(
                            meas.measurement_begin(),
                            '%Y%m%d%H%M%S%f').isoformat()
                except (AttributeError, KeyError, ValueError, TypeError):
                    pass
                raster.set_table_attributes(table_attributes)

                timebasis_name = None
                indep_name = indep_dict.get((submatrix_id, meas_name))

                if indep_name:
                    timebasis_name = indep_name
                elif 'Time' in raster:
                    timebasis_name = 'Time'

                if timebasis_name is None:
                    timebasis_name = 'Time'
                    # Timeseries with no basis, create index basis.
                    raster.set_column_from_array(
                        timebasis_name,
                        np.zeros(raster.number_of_rows(), dtype=float))
                else:
                    try:
                        column = raster.get_column_to_array(timebasis_name)
                        sampling_rate = column[1] - column[0]
                        attributes = raster.get_column_attributes(
                            timebasis_name)
                        attributes['sampling_rate'] = sampling_rate
                        raster.set_column_attributes(
                            timebasis_name, attributes)
                    except (KeyError, IndexError):
                        pass

                if many:
                    new_raster = system.create(
                        '{}{}'.format(meas_name, i))
                else:
                    new_raster = system.create(meas_name)

                new_raster.from_table(raster, timebasis_name)
                if offset is not None:
                    meas_offset[meas_name] += 1

    def get_quantity(self, meas_quantity):
        return (self.get_quantity_data(meas_quantity),
                self.get_quantity_attributes(meas_quantity))

    def get_quantity_attributes(self, meas_quantity):
        attributes = {}

        try:
            quantity = meas_quantity.quantity()
            attributes['description'] = quantity.description()
        except (KeyError, StopIteration, AttributeError):
            pass

        try:
            unit = meas_quantity.unit()
            attributes['unit'] = unit.name()
        except (KeyError, StopIteration, AttributeError):
            pass

        return attributes

    def get_localcolumn_data(self, localcolumn):
        representation = localcolumn.sequence_representation()
        if isinstance(representation, int):
            representation = atfx.sequence_representation_enum[representation]

        if representation == 'explicit':
            dtype, values = localcolumn.values()
            if dtype == 'component':
                values_dict = dict(values)
                for key in ['blocksize',
                            'valperblock',
                            'inioffset',
                            'length']:
                    try:
                        value = int(values_dict[key])
                    except KeyError:
                        value = None
                    values_dict[key] = value

                data_type = values_dict['datatype']
                values_dict['type'] = data_type
                values_dict['valoffsets'] = [int(x) for x in
                                             values_dict['valoffsets'].split()]
                filename = self._comps[
                    values_dict.get('identifier')]['filename']
                values = atfx.binary_to_array(
                    self._dirname, filename, values_dict)
                return atfx.dt_to_array(data_type, values)
            else:
                return atfx.values_dict[dtype](values)

        elif representation == 'implicit_linear':
            try:
                dtype, values = localcolumn.values()
            except KeyError:
                dtype = 'A_FLOAT64'
                values = localcolumn.generation_parameters()

            values = atfx.values_dict[dtype](values)
            offset, step = values

            no_rows = localcolumn.submatrix().number_of_rows()
            return np.arange(no_rows, dtype='f8') * step + offset

        elif representation == 'external_component':
            external = localcolumn.external_component()
            filename = external.filename_url()
            data_type = external.value_type()

            values = {'blocksize': external.block_size(),
                      'valperblock': external.valuesperblock(),
                      'inioffset': external.start_offset(),
                      'length': external.component_length(),
                      'type': data_type,
                      'valoffsets': [external.value_offset()],
                      'component': filename}
            values = atfx.binary_to_array(self._dirname, filename, values)
        else:
            raise Exception(
                'Unknown representation: {}'.format(representation))

        return atfx.dt_to_array(data_type, values)

    def get_quantity_data(self, meas_quantity):
        data_list = []
        try:
            localcolumns = meas_quantity.local_columns()
        except KeyError:
            warnings.warn(
                'Failed to get localcolumns for meas_quantity:{}'.
                format(meas_quantity.id()))
            localcolumns = []

        for localcolumn in localcolumns:
            try:
                data_list.append((localcolumn.submatrix().id(),
                                  (localcolumn.independent(),
                                   self.get_localcolumn_data(localcolumn))))
            except KeyError:
                raise
                warnings.warn('Failed processing localcolumn:{}'.format(
                    localcolumn.id()))
        return data_list
