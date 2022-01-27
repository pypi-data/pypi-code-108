# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017-2018 Combine Control Systems AB
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
from collections import OrderedDict
import inspect
import sys
import os
import sympathy.api
from sympathy.api import node as synode
from sympathy.api import datasource as dsrc
from sympathy.api import importers
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, settings
from sympathy.api import exceptions
import sylib.url


def hasarg(func, arg):
    return arg in inspect.signature(func).parameters


FAILURE_STRATEGIES = OrderedDict(
    [('Exception', 0), ('Create Empty Entry', 1)])

LIST_FAILURE_STRATEGIES = OrderedDict(
    [('Exception', 0), ('Create Empty Entry', 1), ('Skip File', 2)])


def _set_supported_cardinalities(importer, multi):
    options = [importer.one_to_one]
    if multi:
        options = [importer.one_to_many, importer.one_to_one]
    importer.set_supported_cardinalities(options)


class SuperNode(object):
    tags = Tags(Tag.Input.Import)
    plugins = (importers.IDataImporter, )
    _url_doc = """
    *URL datasource*

    If input datasource is a URL resource, the node will download it to a
    temporary file before importing it.

    If the URL resource contains credential variables, these will be entered
    as part of the URL.

    See :ref:`Credentials Preferences<preferences_credentials>` for more info.
    """

    @staticmethod
    def parameters_base():
        parameters = synode.parameters()
        parameters.set_string(
            'active_importer', label='Importer', value='Auto',
            description=('Select data format importer'))
        custom_importer_group = parameters.create_group(
            'custom_importer_data')
        custom_importer_group.create_group('Auto')
        return parameters

    def _available_plugins(self, name=None):
        return importers.available_plugins(self.plugins[0])

    def _create_temp_file_datasource(self, datasource):
        env = dict(datasource['env'])

        if datasource.decode_type() == datasource.modes.url:
            try:
                output_filename = sylib.url.download_url_with_credentials(
                    self,
                    datasource.connection(), env,
                    tempfile_kwargs=dict(prefix='import_http_',
                                         dir=settings()['session_folder']))
                datasource = dsrc.File.from_filename(output_filename)
            except sylib.url.RequestError as e:
                raise exceptions.SyDataError(f'Download failed due to {e}')
        return datasource

    def _remove_temp_file_datasource(self, url_temp_filename):
        if url_temp_filename:
            try:
                os.remove(url_temp_filename)
            except (OSError, IOError):
                pass

    def _output_item_filename_hook(self, output_item, filename):
        pass

    def _import_data(self, item_factory, importer_cls, datasource,
                     parameters, manage_input, progress, multi=False):

        def import_native(importer, manage_input):
            """
            Special case where the file is native sydata of the right type and
            should be copied into the platform.
            """
            # Native importers are only dummy plugins and do not support
            # datasource even when configured through auto.
            importer.check_datasource_type(datasource, datasource.modes.file)
            filename = datasource.decode_path()

            try:
                # Got plugin adaf importer.
                import_links = importer.import_links
            except AttributeError:
                import_links = False

            factory = item_factory(importer.cardinality())
            try:
                ds_infile = factory(
                    filename=filename, mode='r', import_links=import_links)
            except Exception:
                if factory:
                    is_type = getattr(
                        factory, 'is_type', lambda filename, scheme: False)
                    try:
                        match = is_type(filename, 'hdf5')
                    except Exception:
                        match = False

                    if not match:
                        raise importer.invalid_file(filename)
                    raise
            if manage_input is not None:
                manage_input(filename, ds_infile)
            return ds_infile

        def import_external(importer, parameters, progress, manage_input):
            output_data = item_factory(importer.cardinality())()
            # Manage input is only used by import_native and could probably
            # be removed for import_external.
            if hasarg(importer.import_data, 'manage_input'):
                importer.import_data(
                    output_data, parameters, progress=progress,
                    manage_input=manage_input)
            else:
                importer.import_data(
                    output_data, parameters, progress=progress)
            return output_data

        importer = importer_cls.from_datasource(datasource, parameters)
        importer.set_node(self)
        importer.check_datasource(datasource)
        _set_supported_cardinalities(importer, multi)

        if importer.is_type():
            return (import_native(importer, manage_input),
                    importer.cardinality())
        return (import_external(importer, parameters, progress, manage_input),
                importer.cardinality())


class ImportSingle(SuperNode):
    inputs = Ports([Port.Datasource('Datasource')])

    parameters = SuperNode.parameters_base()
    parameters.set_list(
        'fail_strategy', label='Action on import failure',
        list=list(FAILURE_STRATEGIES.keys()), value=[0],
        description='Decide how failure to import a file should be handled.',
        editor=synode.Util.combo_editor())

    def exec_parameter_view(self, node_context):
        datasource = dsrc.File()
        try:
            input_data = node_context.input.first
            if input_data.is_valid():
                datasource = input_data
        except exceptions.NoDataError:
            # This is if no input is connected.
            pass
        return importers.configuration_widget(
            self._available_plugins(),
            node_context.parameters, datasource,
            cardinalities=[importers.IDataImporter.one_to_one],
            node=self)

    def execute(self, node_context):

        def item_factory(cardinality):
            if cardinality == importer_cls.one_to_one:
                return type(node_context.output.first)
            assert False, (
                'Single importer plugin must support one to one relation '
                'between input and output.')

        params = synode.parameters(node_context.parameters)
        importer_type = params['active_importer'].value
        if 'fail_strategy' in params:
            fail_strategy = params['fail_strategy'].value[0]
        else:
            fail_strategy = 0

        url_temp_filename = None
        try:
            importer_cls = self._available_plugins().get(importer_type)
            datasource = node_context.input.first

            if datasource.decode_type() == datasource.modes.url:
                datasource = self._create_temp_file_datasource(datasource)
                url_temp_filename = datasource['path']

            importer_cls = self._available_plugins().get(importer_type)
            ds_dict = datasource.decode()

            if importer_cls is None:
                raise exceptions.SyConfigurationError(
                    "Selected importer plugin ({}) could not be found.".format(
                        importer_type))

            with self._import_data(
                    item_factory,
                    importer_cls, datasource,
                    params["custom_importer_data"][importer_type],
                    None,
                    progress=self.set_progress, multi=False)[0] as output:

                if ds_dict['type'] == 'FILE':
                    self._output_item_filename_hook(output, ds_dict['path'])

                node_context.output.first.source(output)
        except Exception:
            if fail_strategy == FAILURE_STRATEGIES['Create Empty Entry']:
                pass
            else:
                raise
        finally:
            self._remove_temp_file_datasource(url_temp_filename)

        self.set_progress(100)


class ImportMulti(SuperNode):
    inputs = Ports([
        Port.Datasources('Datasources', name='input')])

    parameters = SuperNode.parameters_base()
    parameters.set_list(
        'fail_strategy', label='Action on import failure',
        list=list(LIST_FAILURE_STRATEGIES.keys()), value=[0],
        description='Decide how failure to import a file should be handled.',
        editor=synode.Util.combo_editor())

    def exec_parameter_view(self, node_context):
        datasource = dsrc.File()
        try:
            try:
                datasource = node_context.input.first[0]
            except IndexError:
                datasource = dsrc.File()
        except exceptions.NoDataError:
            # This is if no input is connected.
            pass

        return importers.configuration_widget(
            self._available_plugins(),
            node_context.parameters, datasource,
            cardinalities=[importers.IDataImporter.one_to_many,
                           importers.IDataImporter.one_to_one],
            node=self)

    def execute(self, node_context):

        def item_factory(cardinality):

            if cardinality == importer_cls.one_to_one:
                return type(output_list.create())
            elif cardinality == importer_cls.one_to_many:
                return (lambda *args, **kwargs:
                        sympathy.api.from_type(output_list.container_type))
            else:
                assert False, (
                    'List importer plugin must support one to one or '
                    'one to many relation between input and output.')

        params = node_context.parameters
        importer_type = params['active_importer'].value
        if 'fail_strategy' in params:
            fail_strategy = params['fail_strategy'].value[0]
        else:
            fail_strategy = 0

        input_list = node_context.input.first
        len_input_list = len(input_list)
        output_list = node_context.output.first

        for i, datasource in enumerate(input_list):
            url_temp_filename = None
            try:
                if datasource.decode_type() == datasource.modes.url:
                    datasource = self._create_temp_file_datasource(datasource)
                    url_temp_filename = datasource['path']

                importer_cls = self._available_plugins().get(importer_type)
                ds_dict = datasource.decode()
                if importer_cls is None:
                    raise exceptions.SyDataError(
                        "No importer could automatically be found for "
                        "this file.")

                output_item, cardinality = self._import_data(
                    item_factory,
                    importer_cls,
                    datasource,
                    params['custom_importer_data'][importer_type],
                    node_context.manage_input,
                    lambda x: self.set_progress(
                        (100 * i + x) / len_input_list), multi=True)

                if cardinality == importer_cls.one_to_one:
                    output_items = [output_item]
                elif cardinality == importer_cls.one_to_many:
                    output_items = output_item
                else:
                    raise NotImplementedError()

                if ds_dict['type'] == 'FILE':
                    for output_item in output_items:
                        self._output_item_filename_hook(
                            output_item, ds_dict['path'])
                for output_item in output_items:
                    output_list.append(output_item)
            except Exception:
                if fail_strategy == LIST_FAILURE_STRATEGIES['Exception']:
                    raise exceptions.SyListIndexError(i, sys.exc_info())
                elif fail_strategy == LIST_FAILURE_STRATEGIES[
                        'Create Empty Entry']:
                    print('Creating empty output file (index {}).'.format(i))
                    output_item = output_list.create()
                    output_list.append(output_item)
                else:
                    print('Skipping file (index {}).'.format(i))

            finally:
                self._remove_temp_file_datasource(url_temp_filename)

            self.set_progress(100 * (1 + i) / len_input_list)
