# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017-2018, Combine Control Systems AB
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
import tempfile
import itertools
from sympathy.api import exporters
from sympathy.api import datasource as dsrc
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exceptions


def base_params():
    parameters = synode.parameters()
    parameters.set_string(
        'active_exporter', label='Exporter',
        description=('Select data format exporter. Each data format has its '
                     'own exporter with its own special configuration, see '
                     'exporter information. The selection of exporter do also '
                     'suggest filename extension.'))
    parameters.create_group('custom_exporter_data')
    parameters.set_string(
        'directory', value='.', label='Output directory',
        description='Select the directory where to export the files.',
        editor=synode.Util.directory_editor().value())
    parameters.set_string(
        'filename', label='Filename',
        description='Filename without extension.')
    return parameters


class ExportMultiple(object):
    """Compress/decompress files that are pointed to by the Datasources"""

    tags = Tags(Tag.Output.Export)
    plugins = (exporters.IDataExporter, )
    parameters = base_params()
    outputs = Ports([Port.Datasources(
        'Datasources of exported files', name='port0', scheme='text')])

    def _available_plugins(self, name=None):
        return exporters.available_plugins(self.plugins[0])

    def verify_parameters(self, node_context):
        parameters = node_context.parameters
        parameters_ok = "" != parameters.value_or_empty('active_exporter')
        return parameters_ok

    def exec_parameter_view(self, node_context):
        parameters = node_context.parameters
        input_list = node_context.input.first
        filename_port_list = node_context.input.group(
            self._exporter_ext_filenames_portname())
        fq_filenames = None
        if filename_port_list:
            try:
                fq_filenames = [
                    ds.decode_path() for ds in filename_port_list[0]]
            except exceptions.NoDataError:
                pass

        return exporters.configuration_widget(
            self._available_plugins(),
            parameters, input_list, fq_filenames, node=self)

    def _exporter_ext_filename(self, custom_parameters, fq_filename):
        return fq_filename

    def _exporter_input_item_filename_hook(self, item, fq_filename):
        pass

    def _exporter_ext_filenames_portname(self):
        return 'port1'

    def execute(self, node_context):

        def case_sensitive():
            """
            Trying to figure out weather or not the filesystem is case
            sensitive.
            This is done by opening the temporary filename in lowercase or
            capital
            letters checking if the file can be opened.
            """
            with tempfile.NamedTemporaryFile(
                    prefix='case_', suffix='.cst') as tf:
                return not (os.path.exists(tf.name.lower()) and
                            os.path.exists(tf.name.upper()))

        def unique_actual_filenames(filenames):
            result = []
            lookup = set()
            failed = []

            if case_sensitive():
                lookup.update(filenames)
                for filename in filenames:
                    if filename in lookup:
                        result.append(filename)
                        lookup.remove(filename)
                    else:
                        failed.append(filename)
            else:
                lookup.update([filename.lower() for filename in filenames])
                for filename in filenames:
                    if filename.lower() in lookup:
                        result.append(filename)
                        lookup.remove(filename.lower())
                    failed.append(filename)
            return result

        def export_to_file(type_file, fq_filename, created_dirs):
            fq_dirname = os.path.dirname(fq_filename)
            if fq_dirname not in created_dirs and not os.path.isdir(
                    fq_dirname):
                os.makedirs(fq_dirname)
                created_dirs.add(fq_dirname)

            try:
                return exporter.export_data(type_file, fq_filename,
                                            progress=self.set_progress)
            except (IOError, OSError):
                raise exceptions.SyNodeError(
                    'Unable to create file. Please check that you '
                    'have permission to write to the selected folder.')

        def export_to_dir(type_file, fq_dirname):
            if not os.path.isdir(fq_dirname):
                os.makedirs(fq_dirname)

            try:
                return exporter.export_data(type_file, fq_dirname,
                                            progress=self.set_progress)
            except (IOError, OSError):
                raise exceptions.SyNodeError(
                    'Unable to create file. Please check that you '
                    'have permission to write to the selected folder.')

        def get_fq_filenames(input_list, filename, directory):
            if filename_port_list:
                fq_filenames = [
                    self._exporter_ext_filename(
                        custom_parameters,
                        ds.decode_path()) for ds in filename_port_list[0]]
            else:
                fq_filenames = exporter.create_filenames(input_list, filename)

                if exporter.cardinality() == exporter.one_to_one:
                    fq_filenames = list(itertools.islice(
                        iter(fq_filenames),
                        len(input_list)))

            if exporter.cardinality() == exporter.one_to_one:
                if len(fq_filenames) != len(input_list):
                    raise exceptions.SyNodeError(
                        '"When exporting one-to-one, filenames" and '
                        'datasource list must be the same length.')

            elif exporter.cardinality() == exporter.one_to_many:
                pass
            elif exporter.cardinality() == exporter.many_to_one:
                if len(fq_filenames) != 1:
                    raise exceptions.SyNodeError(
                        '"When exporting many-to_one, filenames" and '
                        'datasource list must be the same length.')
            else:
                assert False, 'Unknown cardinality'
            return [os.path.join(directory, fq_filename)
                    for fq_filename in fq_filenames]

        parameters = node_context.parameters
        exporter_type = parameters['active_exporter'].value
        exporter_cls = self._available_plugins().get(exporter_type)

        if exporter_cls is None:
            raise exceptions.SyConfigurationError(
                "Selected exporter plugin ({}) could not be found.".format(
                    exporter_type))

        custom_parameters = synode.parameters(
            node_context.parameters[
                'custom_exporter_data'][exporter_type])
        exporter = exporter_cls(custom_parameters)
        exporter.set_node(self)

        directory = None
        if exporter.file_based():
            directory = parameters.value_or_empty('directory')
            if not os.path.isdir(directory):
                os.makedirs(directory)

        input_list = node_context.input.first
        datasource_list = node_context.output.first
        number_of_objects = len(input_list)

        filename = parameters.value_or_empty('filename')
        directory = parameters.value_or_empty('directory')
        created_dirs = set()
        filename_port_list = node_context.input.group(
            self._exporter_ext_filenames_portname())

        if exporter.file_based():
            fq_filenames = get_fq_filenames(input_list, filename, directory)

            if exporter.cardinality() == exporter.one_to_one:
                for object_no, (fq_filename, input_item) in enumerate(
                        zip(fq_filenames, input_list)):
                    export_to_file(input_item, fq_filename, created_dirs)
                    self._exporter_input_item_filename_hook(
                        input_item, fq_filename)
                    self.set_progress(
                        100.0 * (1 + object_no) / number_of_objects)

            elif exporter.cardinality() == exporter.many_to_one:
                fq_filename = fq_filenames[0]
                export_to_file(input_list, fq_filename, created_dirs)
                for object_no, (fq_filename, input_item) in enumerate(
                        zip(fq_filenames, input_list)):
                    self._exporter_input_item_filename_hook(
                        input_item, fq_filename)

                self.set_progress(100.0)

            elif exporter.cardinality() == exporter.one_to_many:
                dirnames = [directory for _ in input_list]

                for object_no, (dirname, input_file) in enumerate(
                        zip(dirnames, input_list)):
                    export_to_dir(input_file, dirname)
                    self.set_progress(
                        100.0 * (1 + object_no) / number_of_objects)
            else:
                assert False, 'Unknown cardinality'

            for filename in unique_actual_filenames(fq_filenames):
                # Output datasource is independent of input.
                datasource_file = dsrc.File()
                datasource_file.encode_path(os.path.abspath(filename))
                datasource_list.append(datasource_file)
        else:
            if exporter.cardinality() == exporter.one_to_one:
                for object_no, input_file in enumerate(input_list):
                    exporter.export_data(input_file, None)
                    self.set_progress(
                        100.0 * (1 + object_no) / number_of_objects)

            elif exporter.cardinality() == exporter.many_to_one:
                exporter.export_data(input_list, None)

            elif exporter.cardinality() == exporter.one_to_many:
                raise NotImplementedError(
                    'One-to-many is only implemented for file based plugins.')
            else:
                assert False, 'Unknown cardinality'

        self.set_progress(100)
