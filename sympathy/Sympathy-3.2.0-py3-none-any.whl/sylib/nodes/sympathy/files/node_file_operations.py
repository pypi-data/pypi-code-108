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
import shutil
import re
import os
import os.path

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api import datasource as dsrc
from sympathy.api.nodeconfig import (Port, Ports, Tag, Tags)
from sympathy.api.exceptions import SyDataError
from sympathy.platform import exceptions
import sylib.url


def check_files(datasources, no_error):
    res = []
    for datasource in datasources:
        try:
            res.append(datasource._require_file())
        except Exception:
            if not no_error:
                raise
    return res


def copy_file(
        filename, new_filename=None, directory=None, regex=False, pattern=None,
        replace=None, no_error=False):
    if regex:
        new_filename = re.sub(pattern, replace, filename)
    elif directory:
        new_filename = os.path.join(
            directory, os.path.basename(filename))

    if (not new_filename or
            os.path.abspath(new_filename) == os.path.abspath(filename)):
        in_filename, ext = os.path.splitext(filename)
        new_filename = in_filename + ' - Copy' + ext

    new_filename = os.path.abspath(new_filename)
    path = os.path.dirname(new_filename)
    try:
        try:
            os.makedirs(path)
        except (OSError, IOError):
            pass
        try:
            shutil.copyfile(filename, new_filename)
        except FileNotFoundError:
            raise SyDataError(f'File not found: {filename}.')
    except Exception:
        if no_error:
            return None
        raise
    return new_filename


def delete_file(filename, delete_folder=False, no_error=False):
    directory = os.path.dirname(filename) if delete_folder else None
    try:
        try:
            os.remove(filename)
        except FileNotFoundError:
            raise SyDataError(f'File not found: {filename}.')
    except Exception:
        if no_error:
            filename = None
        else:
            raise
    if directory:
        try:
            os.removedirs(directory)
        except Exception:
            pass
    return filename


def rename_file(
        filename, new_filename=None, directory=None, regex=False,
        pattern=None, replace=None, no_error=False):
    if not new_filename:
        new_filename = filename
    new_filename = os.path.join(
        os.path.dirname(filename), os.path.basename(new_filename))
    if regex:
        new_filename = re.sub(pattern, replace, filename)
    try:
        os.rename(filename, new_filename)
    except (OSError, IOError, SyDataError):
        if not no_error:
            raise
        return None
    return new_filename


def move_file(filename, new_filename, no_error=False):
    path = os.path.dirname(new_filename)
    try:
        os.makedirs(path)
    except (OSError, IOError):
        pass
    try:
        try:
            shutil.move(filename, new_filename)
        except FileNotFoundError:
            raise SyDataError(f'File not found: {filename}.')
    except Exception:
        if no_error:
            return None
        raise
    return new_filename


def regex_only_parameters(parameters):
    parameters.set_string(
        'pattern', label='Search',
        description=(
            'Specify the regular expression that will be used for matching'))
    parameters.set_string(
        'replace', label='Replace',
        description=('The string to replace the match found with the regular '
                     'expression'))
    return parameters


def regex_parameters(parameters, is_dir=False):
    parameters.set_boolean(
        'use_regex', label='Regex',
        description='Turn on/off naming using a regular expression')
    parameters = regex_only_parameters(parameters)
    return parameters


def exception_parameter(parameters):
    parameters.set_boolean(
        'error', label='Do not raise exceptions',
        description='If a file operation fails, do not raise an exception')
    return parameters


def delete_folder_parameter(parameters):
    parameters.set_boolean(
        'delete_folder', label='Delete enclosing folder if empty',
        description=(
            'If a file that is removed is the last in that folder, '
            'the folder is removed. If this operation fails, '
            'no exception is raised.'))
    return parameters


def filename_columns(parameters):
    parameters.set_list(
        'current', label='Current filenames',
        description='The column with the current file names',
        value=[0], editor=synode.Util.combo_editor(edit=True, filter=True))
    parameters.set_list(
        'new', label='New filenames',
        description='The column with the new filenames',
        value=[0], editor=synode.Util.combo_editor(edit=True, filter=True))
    return parameters


def dir_param(parameters):
    parameters.set_string(
        'filename', label='Directory',
        editor=synode.Util.directory_editor(),
        description=('Manually enter a directory'))
    return parameters


def file_param(parameters):
    parameters.set_string(
        'filename', label='Filename',
        editor=synode.Util.savename_editor(['Any files (*)']),
        description=('Manually enter a filename, if not using a regular '
                     'expression'))
    return parameters


def regex_controllers():
    return (
        synode.controller(
            when=synode.field('use_regex', state='checked'),
            action=(
                synode.field('filename', state='disabled'),
                synode.field('pattern', state='enabled'),
                synode.field('replace', state='enabled'),
            ),
        ),
    )


def get_file_lists(node_context):
    parameters = node_context.parameters

    file_table = node_context.input['port2']
    columns = file_table.column_names()

    try:
        current_index = parameters['current'].value[0]
        new_index = parameters['new'].value[0]
        # Fix indices for old configurations
        if parameters['current'].list[0] == '':
            current_index -= 1
        if parameters['current'].list[0] == '':
            new_index -= 1

        current_filenames = file_table.get_column_to_array(
            columns[current_index])
        new_filenames = file_table.get_column_to_array(
            columns[new_index])
    except IndexError:
        return [], []
    if (current_filenames.dtype.kind not in ('U', 'S') or
       new_filenames.dtype.kind not in ('U', 'S')):
        raise SyDataError(
            'One or more of the input columns have the wrong type. '
            'They should be text.')
    return current_filenames, new_filenames


class CopyFile(synode.Node):
    """
    Copy a file from one directory to another. Missing directories will be
    created if possible.
    """

    name = 'Copy file'
    description = ('Copy files to another location. It is possible to name '
                   'the copies using a regular expression.')
    author = 'Alexander Busck & Andreas Tågerud'
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.copyfile'
    icon = 'copy.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([Port.Datasource(
        'Datasource of file to be copied', name='port1', scheme='text')])
    outputs = Ports([Port.Datasource(
        'Datasource of copied file', name='port1', scheme='text')])

    parameters = synode.parameters()
    parameters = file_param(parameters)
    parameters = regex_parameters(parameters)
    parameters = exception_parameter(parameters)
    controllers = regex_controllers()

    def execute(self, node_context):
        parameters = node_context.parameters
        ds_in = node_context.input['port1']
        no_error = parameters['error'].value

        for filename in check_files([ds_in], no_error):
            new_filename = copy_file(
                filename, parameters['filename'].value, None,
                parameters['use_regex'].value, parameters['pattern'].value,
                parameters['replace'].value, no_error)

            if new_filename:
                node_context.output['port1'].encode_path(new_filename)


class CopyFiles(synode.Node):
    """
    Copy multiple files from one directory to another.
    Missing directories will be created if possible.
    """

    name = 'Copy files'
    description = ('Copy files to another location. It is possible to name '
                   'the copies using a regular expression.')
    author = 'Andreas Tågerud'
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.copyfiles'
    icon = 'copy.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([Port.Datasources('Files to be copied', name='port1')])
    outputs = Ports([Port.Datasources('Copied files', name='port1')])

    parameters = synode.parameters()
    parameters = dir_param(parameters)
    parameters = regex_parameters(parameters)
    parameters = exception_parameter(parameters)
    controllers = regex_controllers()

    def execute(self, node_context):
        parameters = node_context.parameters
        no_error = parameters['error'].value

        for filename in check_files(node_context.input['port1'], no_error):
            new_filename = copy_file(
                filename, None, parameters['filename'].value,
                parameters['use_regex'].value, parameters['pattern'].value,
                parameters['replace'].value, no_error)
            if new_filename:
                ds = dsrc.File()
                ds.encode_path(new_filename)
                node_context.output['port1'].append(ds)


class CopyFilesWithDatasources(synode.Node):
    """
    Copies the input file datasources, to the locations designated in the
    second datasources input, element by element. Missing directories will be
    created if possible.
    """

    name = 'Copy files with Datasources'
    description = 'Copy files to another location using a table with paths'
    author = 'Andreas Tågerud'
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.copyfileswithdsrc'
    icon = 'copy.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([
        Port.Datasources('Files to be copied', name='port1'),
        Port.Datasources('File destinations to copy to', name='port2')])
    outputs = Ports([Port.Datasources('Copied files', name='port1')])

    parameters = synode.parameters()
    parameters = exception_parameter(parameters)

    def execute(self, node_context):
        in_dss = node_context.input['port1']
        out_dss = node_context.input['port2']
        no_error = node_context.parameters['error'].value

        for in_filename, out_filename in zip(check_files(in_dss, no_error),
                                             check_files(out_dss, no_error)):
            new_filename = copy_file(
                in_filename, out_filename, no_error=no_error)
            if new_filename:
                out_file = dsrc.File()
                out_file.encode_path(new_filename)
                node_context.output['port1'].append(out_file)


class DeleteFile(synode.Node):
    """Deletes one file."""

    name = 'Delete file'
    description = 'Delete a file'
    author = 'Magnus Sandén & Andreas Tågerud'
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.deletefile'
    icon = 'delete.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([Port.Datasource('File to delete', name='port1')])
    outputs = Ports([Port.Datasource('Path to deleted file', name='port1')])

    parameters = synode.parameters()
    parameters = delete_folder_parameter(parameters)
    parameters = exception_parameter(parameters)

    def execute(self, node_context):
        if not node_context.input['port1'].decode_path():
            # Legacy support.
            return
        parameters = node_context.parameters
        no_error = parameters['error'].value
        for filename in check_files([node_context.input['port1']], no_error):
            del_file = delete_file(
                filename, parameters['delete_folder'].value,
                no_error=parameters['error'].value)
            if del_file:
                ds = dsrc.File()
                ds.encode_path(del_file)
                node_context.output['port1'].encode_path(del_file)


@node_helper.list_node_decorator(['port1'], ['port1'])
class DeleteFiles(DeleteFile):
    name = 'Delete files'
    nodeid = 'org.sysess.sympathy.files.deletefiles'


class MoveFile(synode.Node):
    """Move one file from one location to another."""

    name = 'Move File'
    author = 'Andreas Tågerud'
    version = '1.0'
    icon = 'move.svg'
    description = (
        'Moves a file to new location using a datasource with the location')
    nodeid = 'org.sysess.sympathy.files.movefile'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([
        Port.Datasource('File to be moved', name='port1'),
        Port.Datasource('New location', name='port2')])
    outputs = Ports([Port.Datasource('Moved file', name='port1')])

    parameters = synode.parameters()
    parameters = exception_parameter(parameters)

    def execute(self, node_context):
        if not node_context.input['port1'].decode_path():
            # Legacy support.
            return
        no_error = node_context.parameters['error'].value
        for in_filename, out_filename in zip(
                check_files([node_context.input['port1']], no_error),
                check_files([node_context.input['port2']], no_error)):
            new_filename = move_file(
                in_filename, out_filename, no_error=no_error)
            if new_filename:
                node_context.output['port1'].encode_path(new_filename)


@node_helper.list_node_decorator(['port1', 'port2'], ['port1'])
class MoveFiles(MoveFile):
    name = 'Move Files'
    nodeid = 'org.sysess.sympathy.files.movefiles'


class DownloadFile(synode.Node):
    """
    Download the data at URL to specified local file.


    If URL resource contains credential variables for login or token
    credentials these will be entered as part of the URL.

    See :ref:`Credentials Preferences<preferences_credentials>` for more info.
    """

    name = 'Download URL to file'
    description = 'Download file from a URL to specified filename.'
    author = 'Erik der Hagopian, '
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.downloadfile'
    icon = 'copy.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([Port.Datasource(
        'Datasource pointing to data to read', name='port1', scheme='text')])
    outputs = Ports([Port.Datasource(
        'Datasource of resulting file', name='port1', scheme='text')])

    parameters = synode.parameters()
    parameters = file_param(parameters)
    parameters.set_string(
        'if_exists', label='If file already exists', value='Overwrite',
        description=('What to do if the file already exists'),
        editor=synode.Util.combo_editor(
            options=['Skip file', 'Overwrite', 'Raise exception']))

    def execute(self, node_context):
        parameters = node_context.parameters
        input_datasource = node_context.input['port1']
        output_datasource = node_context.output['port1']
        filename = parameters['filename'].value
        if_exists = parameters['if_exists'].value

        if os.path.isfile(filename):
            if if_exists == 'Skip file':
                output_datasource.encode_path(filename)
                return
            elif if_exists == 'Raise exception':
                raise SyDataError(
                    'File {} already exists'.format(filename))

        if input_datasource.decode_type() == output_datasource.modes.url:
            if not filename:
                raise exceptions.filename_not_empty()
            try:
                output_filename = sylib.url.download_url_with_credentials(
                    self,
                    input_datasource.connection(), input_datasource['env'],
                    filename=filename)
            except sylib.url.RequestError as e:
                raise SyDataError(f'Download failed due to {e}')
            output_datasource.source(dsrc.File.from_filename(output_filename))
        else:
            raise SyDataError('Only URL datasources can be downloaded')
