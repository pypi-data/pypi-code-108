# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyDataError, sywarn

from sympathy.utils import filebase
import sympathy


def filename_str(filename_syd):
    return filename_syd._require_file()


def check_type(const, data):
    dtype = data.container_type
    ctype = const.container_type

    if dtype != ctype:
        raise SyDataError(
            'Type of select file: {} does not match type constraint: {}.'
            .format(dtype, ctype))


scheme = 'hdf5'


class DebugExport(synode.Node):
    """
    This is not a regular export node. The exported file will not be readable
    in any other Sympathy version than the one in which they were exported. If
    you want to export data to sydata files and be able to use the files
    between Sympathy versions you should use :ref:`Export Tables`, :ref:`Export
    ADAFs` etc.

    On the other hand this node is able to export any data type into a sydata
    file, which can be useful for debugging purposes.
    """

    name = 'Debug Export'
    description = (
        'Export internal data structure. '
        'It will only be readable in this Sympathy version.')
    icon = 'debug_export.svg'
    nodeid = 'org.sysess.sympathy.debug.export'
    author = 'Erik der Hagopian'
    version = '1.0'
    tags = Tags(Tag.Development.Debug)
    related = ['org.sysess.sympathy.debug.import']

    inputs = Ports([
        Port.Custom('<a>', 'Data', name='data'),
        Port.Datasource('Filename', name='filename')])

    outputs = Ports([
        Port.Datasource('Filename', name='filename', n=(0, 1, 0))])

    def execute(self, node_context):
        sywarn(self.description)
        data = node_context.input['data']
        fn = filename_str(node_context.input['filename'])

        try:
            with filebase.to_file(
                    fn, scheme, data.container_type, external=True) as f:
                f.source(data)
        except Exception as e:
            raise SyDataError(f'Error exporting file, {e}.')

        fns = node_context.output.group('filename')
        if fns:
            fns[0].encode_path(fn)


class DebugImport(synode.Node):
    """
    This is not a regular import node. The files to be imported must be created
    by :ref:`org.sysess.sympathy.debug.export` on the same Sympathy version. If
    you just want to read normal exported sydata files you should use
    :ref:`Table`, :ref:`ADAF` etc.

    On the other hand this node is able to import any data type from a sydata
    file, which can be useful for debugging purposes.
    """

    name = 'Debug Import'
    description = (
        'Import internal data structure created by Debug Export. '
        'Can only read files exported in this Sympathy version.')
    icon = 'debug_import.svg'
    nodeid = 'org.sysess.sympathy.debug.import'
    author = 'Erik der Hagopian'
    version = '1.0'
    tags = Tags(Tag.Development.Debug)
    related = ['org.sysess.sympathy.debug.export']

    inputs = Ports([
        Port.Datasource('Filename', name='filename'),
        Port.Custom('<a>', 'Type constraint', name='type', n=(1, 1, 1))])

    outputs = Ports([
        Port.Custom('<a>', 'Data', name='data')])

    def execute(self, node_context):
        sywarn(self.description)
        data = node_context.output['data']
        const = node_context.input['type']
        fn = filename_str(node_context.input['filename'])

        if not os.path.isfile(fn):
            raise SyDataError('File: {} does not exist.'.format(fn))

        fileinfo = filebase.fileinfo(fn, scheme)

        if not fileinfo.platform_version() == sympathy.__version__:
            raise SyDataError(
                'File: {} was not created with the current Sympathy'
                ' version.'.format(fn))

        with filebase.from_file(fn, scheme=scheme, external=False) as f:
            check_type(f, const)

        with filebase.from_file(
                fn, scheme, data.container_type,
                external=False) as f:
            if f.container_type != const.container_type:
                check_type(const)
            data.source(f)
