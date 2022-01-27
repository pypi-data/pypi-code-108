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
import re
import os.path
import struct
import array
import datetime

import numpy as np

from sympathy.api import importers
from sympathy.api.exceptions import SyDataError


TYPES = {
        'Double': 'd',
        'Float': 'f',
        'LongLong': 'q',
        'ULongLong': 'Q',
        'Long': 'l',
        'ULong': 'L',
        'Int': 'i',
        'UInt': 'I',
        'Short': 'h',
        'UShort': 'H',
        'Char': 'b',
        'UChar': 'B'
        }


def erg_info(filename):
    """
    Return a tuple of two dictionaries.
    The first containing a structure where the 'File' and 'Quantity' structures
    have been separated into two keys. The remaning keys are as found in the
    file.
    The second containing the keys directly from the file and their value.
    """
    items = []
    props = {}

    with open(filename) as f:
        for line in f:
            try:
                key, value = line.strip().split('=', 1)
            except ValueError:
                pass
            else:
                key = key.strip()
                value = value.strip()
                items.append((key, value))

                swf = key.startswith('File.')
                swq = key.startswith('Quantity.')

                if swf or swq:

                    if swf:
                        parts = key.split('.')
                    if swq:
                        parts = key.split('.')
                        parts = (parts[:1] + ['.'.join(parts[1:-1])] +
                                 parts[-1:])
                    if parts:
                        prev = props

                        for part in parts[:-1]:
                            prev = prev.setdefault(part, {})

                        prev[parts[-1]] = value
                else:
                    props[key] = value
        return (props, dict(items))


def erg_parse_header(f):
    header_format = '8sBBH4x'
    header = f.read(struct.calcsize(header_format))
    id_string, erg_version, endianness, record_length = struct.unpack(header_format, header)
    if id_string != b"CM-ERG\0\0":
        raise SyDataError('Not a valid type 2 ERG file.')
    if erg_version != 1:
        raise SyDataError('Version {} of type 2 ERG file format is not supported.'.format(erg_version))
    if endianness != 0:
        raise SyDataError('Big endian support is not implemented.')
    return record_length


def erg_read_data(f, rec_len, props):
    column_names = []
    column_types = []
    record_format = ''

    i = 1
    while True:
        if str(i) not in props['File']['At']:
            break
        colname = props['File']['At'][str(i)]['Name']
        coltype = props['File']['At'][str(i)]['Type']
        bytes_match = re.match(r'(\d+) Bytes', coltype)
        if bytes_match:
            record_format += bytes_match.group(1) + 'x'
        else:
            column_names.append(colname)
            column_types.append(TYPES[coltype])
            record_format += TYPES[coltype]
        i += 1

    s = struct.Struct(record_format)
    if rec_len != s.size:
        raise SyDataError('Found {} records with total length {}, but record '
                          'length is reported to be {}.'.format(
                              len(column_names), s.size, rec_len))

    columns = [array.array(t) for t in column_types]
    while True:
        t = f.read(rec_len)
        if len(t) < rec_len:
            break
        record = s.unpack_from(t)
        for a, v in zip(columns, record):
            a.append(v)
    return columns, column_names


def get_factor_and_offset(name, props):
    try:
        k = props['Quantity'][name]['Factor']
    except KeyError:
        k = 1
    try:
        b = props['Quantity'][name]['Offset']
    except KeyError:
        b = 0
    return k, b


def get_unit(name, props):
    try:
        return props['Quantity'][name]['Unit']
    except KeyError:
        return ''


class DataImportERG(importers.ADAFDataImporterBase):
    IMPORTER_NAME = "CM-ERG"

    def valid_for_file(self):
        if self._fq_infilename is None or not os.path.isfile(
                self._fq_infilename):
            return False

        with open(self._fq_infilename, 'rb') as f:
            try:
                erg_parse_header(f)
            except:
                return False
            else:
                return True

    def import_data(self, out_datafile, parameters=None, progress=None):
        erg_filename = self._fq_infilename
        info_filename = erg_filename + '.info'
        if not os.path.exists(info_filename):
            info_filename = os.path.splitext(erg_filename)[0] + '.info'
            if not os.path.exists(info_filename):
                raise SyDataError("Can't find infofile.")

        props, items = erg_info(info_filename)

        if props['File']['Format'] == 'FORTRAN_Binary_Data':
            raise SyDataError('Only type 2 erg files are supported. Not type 1.')
        elif props['File']['Format'] != 'erg':
            raise SyDataError('Invalid erg infofile.')

        if props['File']['ByteOrder'] != 'LittleEndian':
            raise SyDataError('Big endian support is not implemented.')

        time = datetime.datetime.fromtimestamp(int(props['File']['DateInSeconds']))

        with open(erg_filename, 'rb') as f:
            rec_len = erg_parse_header(f)
            columns, column_names = erg_read_data(f, rec_len, props)

        out_datafile.meta.create_column('Datetime', np.array([time]), {})
        system = out_datafile.sys.create('CM-ERG')
        raster = system.create('raster')
        unit = get_unit(column_names[0], props)
        raster.create_basis(np.array(columns[0]), dict(unit=unit))
        for name, signal in zip(column_names[1:], columns[1:]):
            unit = get_unit(name, props)
            k, b = get_factor_and_offset(name, props)
            signal = np.array(signal) * k + b
            raster.create_signal(name, signal, dict(unit=unit))
