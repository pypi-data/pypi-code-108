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
"""
Importer of the ASAM ATF file format.
"""
import io
import struct
import os
import re
import numpy as np
import warnings
import itertools
import datetime
from collections import OrderedDict

from sylib.atfparser.parser import stringparser
from sympathy.api import table
from sympathy.api import importers
from sympathy.api import node as synode
from sympathy.api import qt2 as qt_compat
from sympathy.api.exceptions import SyDataError
from sympathy.api.nodeconfig import deprecated_warn


sequence_representation_enum = [
    'explicit',
    'implicit_constant',
    'implicit_linear',
    'implicit_saw',
    'raw_linear',
    'raw_polynomial',
    'formula',
    'external_component',
    'raw_linear_external',
    'raw_polynomial_external',
    'raw_linear_calibrated',
    'raw_linear_calibrated_external']


QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')
ENCODING = 'latin1'
DT_DICT = {'DT_BOOLEAN': {'np_type': bool,
                          'format': 'b'},
           'DT_BYTE': {'np_type': np.int8,
                       'format': 'b'},
           'DT_SHORT': {'np_type': np.int16,
                        'format': 'i'},
           'DT_LONG': {'np_type': np.int32,
                       'format': 'l'},
           'DT_LONGLONG': {'np_type': np.int64,
                           'format': 'q'},
           'DT_FLOAT': {'np_type': np.float32,
                        'format': 'f'},
           'DT_DOUBLE': {'np_type': np.float64,
                         'format': 'd'},
           'IEEEFLOAT4': {'np_type': np.float32,
                          'format': 'f'},
           'IEEEFLOAT8': {'np_type': np.float64,
                          'format': 'd'},
           'DT_SHORT_BEO': {'np_type': np.int16,
                            'format': 'i'},
           'DT_LONG_BEO': {'np_type': np.int32,
                           'format': 'l'},
           'DT_LONGLONG_BEO': {'np_type': np.int64,
                               'format': 'q'},
           'IEEEFLOAT4_BEO': {'np_type': np.float32,
                              'format': 'f'},
           'IEEEFLOAT8_BEO': {'np_type': np.float64,
                              'format': 'd'},
           'DT_STRING': {'np_type': str,
                         'format': 's'},
           'DT_BYTESTR': {'np_type': str,
                          'format': ''},
           'DT_BLOB': {'np_type': str,
                       'format': ''}}


def iterempty(iterable):
    """Return iterable from list, single element or UNDEFINED."""
    if iterable is None:
        return []
    elif iterable == 'UNDEFINED':
        return []
    elif isinstance(iterable, int):
        return [iterable]
    elif isinstance(iterable, float):
        return [iterable]
    elif isinstance(iterable, str):
        return [iterable]
    else:
        return iterable


def dt_to_array(datatype, value):
    """Return value as array of datatype."""
    foundtype = DT_DICT[datatype]['np_type']
    if isinstance(value, list) or isinstance(value, tuple):
        if foundtype == str:
            data_array = np.array(value)
        else:
            data_array = np.array(value, dtype=foundtype)
    else:
        if foundtype == str:
            data_array = np.array([value])
        else:
            data_array = np.array([value], dtype=foundtype)

    return data_array


def dt_to_value(datatype, value):
    """Return value as single datatype."""
    foundtype = DT_DICT[datatype]['np_type']
    return foundtype(value)


def binary_to_array(dirname, filename, info):
    """Read binary data."""
    block_size = info['BLOCKSIZE']
    values_per_block = info['VALPERBLOCK']
    file_offset = info['INIOFFSET']
    nr_elements = info['LENGTH']
    data_type = info['TYPE']
    block_offset = info['VALOFFSETS']
    np_type = DT_DICT[data_type]['np_type']
    type_format = DT_DICT[data_type]['format']
    data_type_size = np.dtype(np_type).itemsize
    endian_format = '<'
    if 'BEO' in data_type.split('_'):
        endian_format = '>'

    with open(os.path.join(dirname, filename), 'rb') as data_file:
        data_file.seek(file_offset, os.SEEK_SET)
        if data_type == 'DT_STRING' and values_per_block is None:
            result = data_file.read(nr_elements).split(b'\x00')[:-1]

        elif block_size == values_per_block * data_type_size:
            block = data_file.read(data_type_size * nr_elements)
            string_format = '{0}{1}{2}'.format(
                endian_format, nr_elements, type_format)
            result = struct.unpack(string_format, block)

        else:
            result = []

            if data_type == 'DT_STRING' and block_offset == [0]:
                result = data_file.read(nr_elements).split(b'\x00')[:-1]
            else:
                nr_blocks = nr_elements / values_per_block
                string_format = '{0}{1}'.format(endian_format, type_format)
                for ii in range(nr_blocks):
                    data_file.seek(ii * block_size, os.SEEK_SET)
                    for offset in block_offset:
                        data_file.seek(offset, os.SEEK_CUR)
                        block = data_file.read(data_type_size)
                        result.append(struct.unpack(string_format, block)[0])

        if data_type == 'DT_STRING':
            try:
                result = [x.decode(ENCODING) for x in result]
            except (AttributeError, UnicodeDecodeError):
                warnings.warn(
                    'decoding failed for binary array')
        return result


def to_unicode(value):
    value = value.decode(ENCODING)
    try:
        return str(value)
    except UnicodeEncodeError:
        return value


class ATFImportWidget(QtWidgets.QWidget):
    """GUI widget for the atf importer."""
    def __init__(self, parameters, parent=None):
        super(ATFImportWidget, self).__init__(parent)
        self._parameters = parameters
        self._init_gui()

    def _init_gui(self):
        layout = QtWidgets.QVBoxLayout()
        timeseries_gui = self._parameters['timeseries'].gui()
        measurement_gui = self._parameters['measurements'].gui()
        timeseries_gui.setEnabled(False)
        measurement_gui.setEnabled(False)
        layout.addWidget(timeseries_gui)
        layout.addWidget(measurement_gui)

        self.setLayout(layout)
        self.adjustSize()


class DataImportATF(importers.ADAFDataImporterBase):
    """Import exported ATF data into h5 format."""
    IMPORTER_NAME = 'ATF'

    def __init__(self, fq_in_filename, parameters):
        super(DataImportATF, self).__init__(fq_in_filename, parameters)
        self._adaf = None
        self._asamatf = None
        self.DATA_WRITER_DICT = {}

        if parameters is not None:
            self._init_parameters()

    def name(self):
        return self.IMPORTER_NAME

    def _init_parameters(self):
        try:
            self._parameters['measurements']
        except KeyError:
            list_editor = synode.Util.multilist_editor()
            list_editor.set_attribute('filter', False)
            list_editor.set_attribute('mode', False)
            list_editor.set_attribute('buttons', True)
            list_editor.set_attribute('invertbutton', True)
            self._parameters.set_list(
                'measurements', label='Select measurements:',
                description='The measurements to import.',
                editor=list_editor.value(), value=[])
            self._parameters['measurements'].list = sorted(
                self.DATA_WRITER_DICT.keys())
        try:
            self._parameters['timeseries']
        except KeyError:
            self._parameters.set_boolean(
                'timeseries', value=True, label='Import timeseries:',
                description='Import timeseries.')

    def valid_for_file(self):
        if self._fq_infilename is None or not os.path.isfile(
                self._fq_infilename):
            return False

        sample_size = 256
        result = False
        with io.open(self._fq_infilename, 'r', encoding=ENCODING) as f:
            string = f.read(sample_size)
            result = re.findall('ATF_FILE V1\\.41;', string) != []
        return result

    def parameter_view(self, parameters):
        if not self.valid_for_file():
            return QtWidgets.QWidget()
        return ATFImportWidget(parameters)

    def _measurement_to_meta(self, table, out_adaffile):
        out_adaffile.meta.from_table(table)

    def _measurement_to_none(self, table, out_adaffile):
        pass

    def _measurement_to_result(self, table, out_adaffile):
        out_adaffile.res.from_table(table)

    def import_data(self, out_adaffile, parameters=None, progress=None):
        def check_files(root, files):
            """
            Check for existence of the binary files connected to the considered
            atf-file.
            """
            for header, filename in files.items():
                filename = os.path.join(root, filename)
                if not os.path.isfile(filename):
                    warnings.warn(
                        'The file {0} could not be found'.format(filename))

        deprecated_warn(
            'Support for ATF import',
            '4.0.0')

        # Outgoing ADAF structure.
        self._adaf = out_adaffile
        # Parse ATF source.

        with io.open(self._fq_infilename, 'r', encoding=ENCODING) as f:
            fdata = f.read()
            index = fdata.find('\x00')
            if index > 0:
                raise SyDataError('File contains:"\\x00" in byte:{} and is '
                                  'likely broken.\nIf possible, check the '
                                  'version of the tool that produced it.'
                                  ''.format(index))
            self._asamatf = stringparser(fdata)

        # Initialize names to different levels in parsed data.

        if self._asamatf is None:
            raise self.import_failed('no document')

        instelem = self._asamatf[1]['instelem']
        applelem = self._asamatf[1]['applelem']
        model = ApplicationModel(applelem, instelem)

        self._files = self._asamatf[1].setdefault('files', {})
        self._dirname = os.path.dirname(self._fq_infilename)
        self._measurement_offset = {}

        check_files(self._dirname, self._files)

        system = self._adaf.sys.create('CONCERTO')
        # Loop over the existing tests.
        for test in model.subtest:
            ignore, special, other_as_raster = self.get_measurement_selection(
                test.id(), self._parameters)
            try:
                measurements = list(test.backref_children())
            except AttributeError:
                continue

            for key in test.get_instance_field_names():
                value = test.get_instance_field_by_name(key)

                if not isinstance(value, list) and value is not None:
                    # Output scalar instance field attribute to metadata.

                    out_adaffile.meta.create_column(
                        'ATF_Test_{}'.format(key), np.array([value]))

            measurement_names = [measurement.name()
                                 for measurement in measurements]
            count = dict.fromkeys(measurement_names, 0)
            for measurement_name in measurement_names:
                count[measurement_name] += 1

            self._measurement_offset = {key: 0 if value > 1 else None
                                        for key, value in count.items()}

            for measurement in measurements:
                self.get_measurement(measurement, system, ignore, special,
                                     other_as_raster)

            out_adaffile.set_source_id(os.path.basename(self._fq_infilename))

    def get_measurement(self, measurement, system, ignore, special, as_raster):
        measurement_name = measurement.name()
        rasters_dict = OrderedDict()
        if measurement_name in ignore:
            return
        if measurement_name not in special and not as_raster:
            return

        try:
            list(measurement.backref_measurement_quantities())
        except (AttributeError, KeyError):
            return

        for measurement_quantity in (
                measurement.backref_measurement_quantities()):
            quantity_name = measurement_quantity.name()
            try:
                data, attributes = self.get_quantity(measurement_quantity)
            except IOError:
                warnings.warn(
                    'quantity:{} could not be read'.format(quantity_name))
                continue

            for submatrix_id, array in data:
                raster = rasters_dict.setdefault(
                    (submatrix_id, measurement_name), table.File())
                raster.set_column_from_array(
                    quantity_name, array, attributes)

        offset = self._measurement_offset[measurement_name]
        many = len(rasters_dict) > 1 or offset is not None
        for i, ((submatrix_id, measurement_name), raster) in enumerate(
                rasters_dict.items()):
            i += offset or 0

            if measurement_name in self.DATA_WRITER_DICT:
                self.DATA_WRITER_DICT[measurement_name](raster, self._adaf)
            else:
                table_attributes = raster.get_table_attributes() or {}
                try:
                    table_attributes[
                        'reference_time'] = datetime.datetime.strptime(
                            measurement.measurement_begin(),
                            '%Y%m%d%H%M%S%f').isoformat()
                except (AttributeError, KeyError, ValueError, TypeError):
                    pass

                for key in measurement.get_instance_field_names():
                    value = measurement.get_instance_field_by_name(key)

                    if not isinstance(value, list) and value is not None:
                        # Output scalar instance field attribute to metadata.
                        table_attributes['ATF_Meas_{}'.format(key)] = value

                raster.set_table_attributes(table_attributes)

                timebasis_name = None

                if 'Time' in raster:
                    timebasis_name = 'Time'

                elif 'recorder_time' in raster:
                    # Timeseries with index basis.
                    timebasis_name = 'recorder_time'

                if timebasis_name is None:
                    timebasis_name = 'recorder_time'
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
                        measurement_name + str(i))
                else:
                    new_raster = system.create(
                        measurement_name)

                new_raster.from_table(raster, timebasis_name)
                if offset is not None:
                    self._measurement_offset[measurement_name] += 1

    def get_quantity(self, measurement_quantity):
        return (self.get_quantity_data(measurement_quantity),
                self.get_quantity_attributes(measurement_quantity))

    def get_quantity_attributes(self, measurement_quantity):
        attributes = {}

        try:
            quantity = next(measurement_quantity.quantity())
            attributes['description'] = quantity.description() or ''
        except (KeyError, StopIteration, TypeError):
            pass

        try:
            unit = next(measurement_quantity.unit())
            attributes['unit'] = unit.name() or ''
        except (KeyError, StopIteration, TypeError):
            pass

        return attributes

    def get_localcolumn_data(self, localcolumn):
        representation = localcolumn.sequence_representation()
        if isinstance(representation, int):
            representation = sequence_representation_enum[representation]

        if representation == 'explicit':
            data_type, values = localcolumn.values()

            if isinstance(values, dict):
                component = values['COMPONENT']
                filename = self._files.get(component, component)
                values = binary_to_array(self._dirname, filename, values)

        elif representation == 'implicit_linear':
            try:
                data_type, values = localcolumn.values()
            except KeyError:
                data_type = 'DT_DOUBLE'
                values = localcolumn.generation_parameters()

            offset, step = values
            no_rows = next(localcolumn.submatrix()).number_of_rows()
            values = (np.arange(no_rows, dtype=float) * step + offset).tolist()

        elif representation == 'external_component':
            external = next(localcolumn.external_component())
            filename = external.filename_url()
            data_type = external.value_type()
            values = {'BLOCKSIZE': external.block_size(),
                      'VALPERBLOCK': external.valuesperblock(),
                      'INIOFFSET': external.start_offset(),
                      'LENGTH': external.component_length(),
                      'TYPE': data_type,
                      'VALOFFSETS': [external.value_offset()],
                      'COMPONENT': filename}
            values = binary_to_array(self._dirname, filename, values)
        else:
            raise Exception(
                'Unknown representation: {}'.format(representation))

        return dt_to_array(data_type, values)

    def get_quantity_data(self, measurement_quantity):
        data_list = []
        try:
            localcolumns = measurement_quantity.backref_local_columns()
        except KeyError:
            warnings.warn(
                'Failed to get localcolumns for measurement_quantity:{}'.
                format(measurement_quantity.id()))
            localcolumns = []

        for localcolumn in localcolumns:
            try:
                data_list.append((next(localcolumn.submatrix()).id(),
                                  self.get_localcolumn_data(localcolumn)))
            except KeyError:
                warnings.warn('Failed processing localcolumn:{}'.format(
                    localcolumn.id()))
        return data_list

    def get_measurement_selection(self, test, parameter_root):
        selected_measurements = parameter_root['measurements'].value_names
        defined_measurements = self.DATA_WRITER_DICT.keys()
        ignore = set(defined_measurements).difference(selected_measurements)
        special = selected_measurements
        include_timeseries = parameter_root['timeseries'].value
        return (ignore, special, include_timeseries)


class ApplicationModel(object):

    backrefs = {
        'AoMeasurement': {'test': 'children'},
        'AoMeasurementQuantity': {'measurement': 'measurement_quantities'},
        'AoSubmatrix': {'measurement': 'submatrixes'},
        'AoLocalColumn': {'submatrix': 'local_columns',
                          'measurement_quantity': 'local_columns'}}

    def __init__(self, applelem, instelem):
        self.__applelem = applelem
        self.__instelem = instelem
        self.__classes = {}
        self.__progress = {}
        self.__backrefs = {}
        self.__create_element_classes()
        self.__translate = self.__get_translations()

        self.environment = self.__get_element_iterator('AoEnvironment')
        self.test = self.__get_element_iterator('AoTest')
        self.subtest = self.__get_element_iterator('AoSubTest')
        self.measurement = self.__get_element_iterator('AoMeasurement')
        self.measurementquantity = self.__get_element_iterator(
            'AoMeasurementQuantity')
        self.unit = self.__get_element_iterator('AoUnit')
        self.quantity = self.__get_element_iterator('AoQuantity')
        self.submatrix = self.__get_element_iterator('AoSubmatrix')
        self.localcolumn = self.__get_element_iterator('AoLocalColumn')

    def __create_element_classes(self):
        for element in self.__applelem.values():
            self.__create_element(element, self.__classes, self.__backrefs)
        for element, fields in self.__backrefs.items():
            other_class = self.__classes[element]
            for field, function in fields.items():
                setattr(other_class, field, function)

    def __create_element(self, element, classes, backrefs):
        name, base, fields = element
        if name in classes:
            return

        self.__progress[name] = None
        result = {}
        current_backrefs = self.backrefs[base] if base in self.backrefs else {}

        def __init__(self, curr, instelem):
            self.curr = curr
            self.__instelem = instelem

        def get_name(name):
            def inner(self):
                return self.curr[name]
            return inner

        def get_instance_field_names(self):
            return self.curr.keys()

        def get_instance_field_by_name(self, name):
            return self.curr[name]

        def get_name_ref(name, ref_to, classes):
            def inner(self):
                return (classes[ref_to](self.__instelem[ref_to][ref],
                                        self.__instelem) for
                        ref in iterempty(self.curr[name]))
            return inner

        def get_backref(name, ref_to, key, other_key, classes):
            composite_key = (name, other_key)
            memo = {}

            def key_by_backref(pair):
                return pair[1][key]

            def inner(self):
                if composite_key in memo:
                    groups = memo[composite_key]
                else:
                    by_backref = sorted(
                        self.__instelem[name].items(), key=key_by_backref)
                    keys = []
                    groups = []
                    for ident, group in itertools.groupby(
                            by_backref,
                            key=key_by_backref):
                        keys.append(ident)
                        groups.append([value[0] for value in group])
                    groups = dict(zip(keys, groups))
                    memo[composite_key] = groups

                w = (classes[name](self.__instelem[name][ref],
                                   self.__instelem)
                     for ref in groups[self.id()])
                return w
            return inner

        result['__init__'] = __init__

        for key, value in fields.items():
            if 'REF_TO' in value:
                other_element = value['REF_TO']
                if (other_element not in classes and
                        other_element not in self.__progress):
                    try:
                        self.__create_element(
                            self.__applelem[other_element], classes, backrefs)
                    except KeyError:
                        warnings.warn(
                            'Missing APPELEM:{}'.format(other_element))
                        continue
                func = get_name_ref(key, other_element, classes)
            else:
                func = get_name(key)

            result[key] = func

            if 'BASEATTR' in value:
                baseattr = value['BASEATTR']
                result[baseattr] = func
                if baseattr in current_backrefs:
                    other_key = current_backrefs[baseattr]
                    lookup = backrefs.setdefault(other_element, {})
                    lookup['backref_{}'.format(other_key)] = get_backref(
                        name, other_element, key, other_key, classes)

        for func in [get_instance_field_names, get_instance_field_by_name]:
            result[func.__name__] = func

        element_class = type(name, (object,), result)

        classes[name] = element_class

    def __get_element_iterator(self, basename):
        for name in self.__translate[basename]:
            for instance in self.__instelem[name].values():
                yield self.__classes[name](instance, self.__instelem)

    def __get_translations(self):
        pair_list = [(parent, child)
                     for child, parent, fields in
                     self.__applelem.values()]
        result = {}
        for key, value in pair_list:
            acc = result.setdefault(key, [])
            acc.append(value)
        return result
