# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
Library of the nodes
"""
import json
import os
import copy

from packaging.version import Version
from Qt import QtCore

from sympathy.platform.parameter_helper import ParameterRoot
from sympathy.utils.prim import open_url, uri_to_path, localuri, samefile
from sympathy.utils.tag import LibraryTags
from sympathy.utils import components, log
from sympathy.platform import port as port_platform
from sympathy.platform import types
import sympathy.app.datatypes as datatypes
import sympathy.app.settings as settings
from sympathy.platform import migrations
from sympathy.platform.library import is_combine_library_id
import sympathy.app.user_statistics as user_statistics
import sympathy.platform.feature
from . import library_manager
from . import util


node_id = 0
core_logger = log.get_logger('core')


def _sort_dict(parameter_dict):
    def key_fn(item):
        """
        Place scalar values first, in alphabetical order. Place lists after
        that. Place dictionaries with 'order' keys after that based on
        'order'. Lastly, place dictionaries without an 'order' key.
        """
        if isinstance(item[1], (str, bytes, int, float, bool, type(None))):
            return (0, item[0])
        elif isinstance(item[1], list):
            return (1, item[0])
        elif isinstance(item[1], dict):
            try:
                return (2, item[1]['order'])
            except (KeyError, TypeError):
                return (3, item[0])
        else:
            return (4, item[0])

    if isinstance(parameter_dict, dict):
        items = [(k, _sort_dict(v)) for k, v in parameter_dict.items()]
        return dict(sorted(items, key=key_fn))
    else:
        return parameter_dict


def ensure_parsed(version):
    if isinstance(version, Version):
        return version
    return Version(version)


def sort_migrations(migration_classes):
    """Return sorted migrations and latest version as a tuple."""
    migration_classes = sorted(
        migration_classes,
        key=lambda cls: cls.from_version)

    # Ignore NodeMigrations since their to_version applies to a different node.
    basic_migration_classes = [
        cls for cls in migration_classes
        if not issubclass(cls, migrations.NodeMigration)]

    if not len(basic_migration_classes):
        latest_version = None
    else:
        latest_version = basic_migration_classes[-1].to_version

    return migration_classes, latest_version


class PortDefinition(object):
    def __init__(self, name, description, datatype, scheme, index,
                 requires_input_data=False, preview=False):
        super(PortDefinition, self).__init__()
        self._name = name
        self._description = description
        if isinstance(datatype, datatypes.DataType):
            self._datatype = datatype
        else:
            self._datatype = datatypes.DataType.from_str(datatype)

        self.generics = types.generics(self._datatype.datatype)

        self._scheme = scheme
        self._index = index
        self._requires_input_data = requires_input_data
        self._preview = preview

    @classmethod
    def from_definition(cls, definition):
        name = definition.get('name', '')
        description = definition['description']
        type_ = definition.get('type') or definition['datatype']
        datatype = datatypes.DataType.from_str(type_)
        scheme = definition.get('scheme', 'hdf5')
        index = definition.get('index', None)
        requires_input_data = definition.get('requiresdata', True)
        preview = definition.get('preview', False)
        return cls(name, description, datatype, scheme, index,
                   requires_input_data, preview)

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def datatype(self):
        return self._datatype

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def requires_input_data(self):
        return self._requires_input_data

    @property
    def preview(self):
        return self._preview

    @property
    def file_list(self):
        return self._file_list

    @file_list.setter
    def file_list(self, value):
        self._file_list = value

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        self._scheme = value

    def __str__(self):
        return 'PortDefinition: {}/{} {}'.format(
            self._name, self._description, self._index)


class AnyTypePortDefinition(PortDefinition):
    def __init__(self):
        super().__init__(
            'Port', 'Port', datatypes.Any, 'hdf5', -1, False)


class ParameterModel:
    def __init__(self):
        super().__init__()
        self._data = {}
        self._type = 'json'

    @classmethod
    def from_dict(cls, dictionary):
        instance = cls()
        instance.build_from_dict(dictionary)
        return instance

    @classmethod
    def from_json(cls, json_data):
        instance = cls()
        instance.build_from_json(json_data)
        return instance

    def to_dict(self):
        return self._data

    def to_ordered_dict(self):
        return _sort_dict(self.to_dict())

    def json(self):
        return json.dumps(self.to_dict())

    def build_from_json(self, parameters):
        self.build_from_dict(json.loads(parameters))

    def build_from_dict(self, parameters):
        if parameters is None:
            return
        if 'data' in parameters:
            self._data = parameters['data']
            self._type = parameters['type']

    def is_empty(self, ignore_group=False):
        if ignore_group:
            res = len(self._data) <= 1
        else:
            res = len(self._data) == 0
        return res

    def data_dict(self):
        """
        Return only the data dictionary.
        This method should return the part of the model with the actual
        parameters.
        """
        return self._data

    def equal_to(self, other_parameter_model):
        """
        Compares this parameter model to another parameter model and returns
        true if all "value" and "list" keys are equal.
        :param other_parameter_model: Parameter model to compare.
        :return: True if equal.
        """
        # Copy to prevent issues from any modifications resulting from building
        # parameter model.
        self_parameters = ParameterRoot(
            copy.deepcopy(self.data_dict()))
        other_parameters = ParameterRoot(
            copy.deepcopy(other_parameter_model.data_dict()))
        got_eq = self_parameters.equal_to(other_parameters, as_stored=True)
        return got_eq

    def to_parameter_model(self):
        """Return a ParameterModel."""
        return self

    def to_parameter_root(self):
        return ParameterRoot(copy.deepcopy(self.data_dict()))


class OverridesModel(ParameterModel):
    """
    Special parameter model for overrides which also keeps track of the
    overrides version.
    """
    def __init__(self):
        super().__init__()
        self._version = None
        self._nodeid = None

    def get_nodeid(self):
        return self._nodeid

    def set_nodeid(self, nodeid):
        self._nodeid = nodeid

    def get_version(self):
        return self._version

    def set_version(self, version: Version):
        assert isinstance(version, Version)
        self._version = version

    def build_from_dict(self, parameters):
        super().build_from_dict(parameters)
        if 'version' in parameters:
            self.set_version(Version(parameters['version']))
        if 'nodeid' in parameters:
            self._nodeid = parameters['nodeid']

    def to_dict(self):
        return {
            'data': self._data,
            'type': self._type,
            'version': str(self._version),
            'nodeid': self._nodeid}

    def to_parameter_model(self):
        """
        Return a new ParameterModel with the a copy of data in this model.
        """
        return ParameterModel.from_dict(copy.deepcopy(self.to_dict()))


class LibraryNode(object):

    def __init__(self, parent_library):
        self._name = None
        self._library_id = None
        self._hierarchical_name = None
        self._author = None
        self._description = None
        self._copyright = None
        self._maintainer = None
        self._version = None
        self._tags = None
        self._library = None
        self._has_svg_icon = None
        self._has_docs = None
        self._html_docs = None
        self._html_base_uri = None
        self._svg_icon_data = None
        self._node_identifier = None
        self._icon = None
        self._parameter_model = None
        self._parent = None
        self._source_uri = None
        self._class_name = None
        self._inputs = None
        self._outputs = None
        self._path = None
        self._parent = None
        self._type = None
        self._deprecated = None
        self._needs_validate = True
        self._ok = True
        self._port_definition = {}

    def reload(self):
        pass

    @property
    def name(self):
        return self._name

    @property
    def installed(self):
        return self._name

    @property
    def hierarchical_name(self):
        return self._hierarchical_name

    @property
    def author(self):
        return self._author

    @property
    def maintainer(self):
        return self._maintainer

    @property
    def description(self):
        return self._description or ''

    @property
    def copyright(self):
        return self._copyright

    @property
    def deprecated(self):
        return self._deprecated

    @property
    def version(self):
        return self._version

    @property
    def tags(self):
        return self._tags

    @property
    def library(self):
        return self._library

    @property
    def library_id(self):
        return self._library_id

    @property
    def has_svg_icon(self):
        return self._has_svg_icon

    @property
    def has_docs(self):
        return self._has_docs

    @property
    def html_docs(self):
        return self._html_docs

    @property
    def html_base_uri(self):
        return self._html_base_uri

    @property
    def svg_icon_data(self):
        return self._svg_icon_data

    @property
    def node_identifier(self):
        return self._node_identifier

    @property
    def icon(self):
        return self._icon

    @property
    def parameter_model(self):
        return self._parameter_model

    @parameter_model.setter
    def parameter_model(self, value):
        self._parameter_model = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def source_uri(self):
        return self._source_uri

    @property
    def class_name(self):
        return self._class_name

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def type(self):
        return self._type

    @property
    def ok(self):
        return self._ok

    @property
    def path(self):
        return self._path

    @property
    def needs_validate(self):
        return self._needs_validate

    @property
    def port_definition(self):
        return self._port_definition

    @property
    def migrations(self):
        return self._migrations

    @property
    def is_platform_node(self):
        return is_platform_node(self)

    # Complete mock-up at this point
    @classmethod
    def from_uri(cls, uri, library):
        node = cls(library)
        node._uri = uri
        definition = ''
        node._set_definition(definition)
        return node

    @classmethod
    def from_definition(cls, parent_library_identifier, definition):
        node = cls(parent_library_identifier)
        node._name = definition['label']
        node._type = definition['type']

        missing_str = 'Unknown'

        node._author = definition.get('author', missing_str)
        node._description = definition.get('description', missing_str)
        node._copyright = definition.get('copyright', missing_str)
        node._maintainer = definition.get('maintainer', missing_str)
        node._version = definition.get('version', '')
        node._tags = definition.get('tags', None)
        node._deprecated = definition.get('deprecated')
        node._needs_validate = definition.get('validate', True)

        # If node definition doesn't include library keyword (probably
        # means that the node definitions was read from a 1.0 workflow)
        # and the node is not found in any known library set it
        # library to an empty string.
        node._library = definition.get('library', '')

        # TODO: parent_library_identifier should probably be preferred when
        # provided, library_identifier is currently not available in all node
        # definitions: flow nodes, missing nodes. Either that or
        # library_identifier should be ensured to exist in definition.
        parent_library_identifier = parent_library_identifier or ''
        node._library_id = definition.get(
            'library_identifier', parent_library_identifier)

        try:
            node._source_uri = definition['file']
        except KeyError:
            node._source_uri = ''
            core_logger.warning('Node "%s" not found in libraries.',
                                node._name)
            node._needs_validate = False
            node._ok = False
        node._icon = definition.get('icon', None)

        if not node._icon:
            node._icon = localuri(util.icon_path('missing.svg'))

        try:
            with open_url(node._icon, 'rb') as f:
                svg_data = f.read()
            node._has_svg_icon = True
            node._svg_icon_data = QtCore.QByteArray(svg_data)
        except Exception as e:
            print('Could not open icon file {} ({})'.format(node._icon,
                  node._source_uri))
            print(e)

        node._html_base_uri = definition.get('docs', '')
        node._node_identifier = definition['id']
        node._parameter_model = ParameterModel.from_dict(
            definition['parameters'])
        node._class_name = definition.get('class', None)

        migration_classes = []
        for migr_def in definition.get('migrations', []):
            env = components.get_file_env(
                uri_to_path(migr_def['file']), no_raise=True)
            migr_class = env[migr_def['class']]
            migr_class.from_version = ensure_parsed(migr_class.from_version)
            migr_class.to_version = ensure_parsed(migr_class.to_version)
            migration_classes.append(migr_class)
        node._migrations, node_version = sort_migrations(migration_classes)
        if node_version is None:
            if is_combine_library_id(node.library_id):
                node_version = migrations.updated_version
            else:
                node_version = migrations.epoch_version
        node._version = node_version

        node._path = [
            part for part in os.path.dirname(
                uri_to_path(node._source_uri)[
                    len(node._library):]).split(os.path.sep)
            if len(part) > 0]
        node._inputs = []
        ports = definition.get('ports', {})
        node._port_definition = ports

        inputs = ports.get('inputs', [])
        outputs = ports.get('outputs', [])
        inputs, outputs = port_platform.instantiate(inputs, outputs, {})

        node._inputs = []
        for idx, port in enumerate(inputs):
            node._inputs.append(
                PortDefinition.from_definition(port))

        node._outputs = []
        for idx, port in enumerate(outputs):
            node._outputs.append(
                PortDefinition.from_definition(port))

        return node


class Library(object):

    def __init__(self, name=None):
        super(Library, self).__init__()
        self.clear()
        self._uri = None
        self._name = name or 'Unknown'
        self._description = None
        self._version = None
        self._libraries = []
        self._parent = None
        self._installed = None
        self._identifier = None
        self._required_features = []
        self._nodes = []
        self._examples_path = None
        self._home_url = None
        self._repository_url = None
        self._documentation_url = None
        self._style = None

    def add_library(self, library):
        self._libraries.append(library)
        library.parent = self

    def add_node(self, node):
        self._nodes.append(node)
        node.parent = self

    def is_valid(self):
        return True

    def hierarchical_name(self):
        pass

    @property
    def name(self):
        return self._name

    @property
    def uri(self):
        return self._uri

    @property
    def libraries(self):
        return self._libraries

    @property
    def nodes(self):
        return self._nodes

    @property
    def tags(self):
        return self._tags

    @property
    def examples_path(self):
        return self._examples_path

    @property
    def repository_url(self):
        return self._repository_url

    @property
    def documentation_url(self):
        return self._documentation_url

    @property
    def home_url(self):
        return self._home_url

    @property
    def installed(self):
        return self._installed

    @property
    def identifier(self):
        return self._identifier

    @property
    def required_features(self):
        return self._required_features

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def style(self):
        return self._style

    @classmethod
    def from_uri(cls, uri, parent=None):
        library = cls()
        library._uri = uri
        return library

    @classmethod
    def from_dict(cls, dictionary, parent=None):
        library = cls()
        library._uri = 'Unknown'

        library._installed = dictionary['installed']
        library._identifier = dictionary['identifier']
        library._required_features = dictionary['required_features']
        library._name = dictionary['name']
        library._uri = dictionary['root']
        library._examples_path = dictionary['examples_path']
        library._repository_url = dictionary['repository_url']
        library._documentation_url = dictionary['documentation_url']
        library._home_url = dictionary['home_url']
        library._style = dictionary['style']

        for definition in dictionary['nodes']:
            try:
                node = LibraryNode.from_definition(
                    library.identifier, definition)
                library._nodes.append(node)
            except Exception:
                core_logger.warning('Node "%s" could not be added to library.',
                                    (definition or {}).get('id'))

        return library

    def clear(self):
        self._libraries = []
        self._nodes = []
        self._name = ''
        self._parent = None
        self._uri = ''
        self._examples_path = None
        self._identifier = ''
        self._installed = None


class RootLibrary(Library):
    def __init__(self):
        super(RootLibrary, self).__init__()
        self._tags = None

    def set_tags(self, tags):
        self._tags = tags

    def clear(self):
        super(RootLibrary, self).clear()
        self._tags = None


class LibraryManager(QtCore.QObject):
    library_added = QtCore.Signal()
    library_output = QtCore.Signal(util.DisplayMessage)
    library_aliases = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super(LibraryManager, self).__init__(parent)
        self._root_library = RootLibrary()
        self._node_registry = {}
        self._root_library._name = 'Root'
        self._library_manager = None
        self._library_data = None
        self._library_ids = {}

    def reload_library(self):
        """Reload libraries using the library manager"""
        settings_instance = settings.instance()
        install_folder = settings_instance['install_folder']
        self._library_manager = library_manager.LibraryManager(
            install_folder,
            settings_instance['storage_folder'],
            util.python_paths(),
            util.library_paths(),
            settings_instance.sessions_folder,
            settings_instance['session_folder'])

        tags, lib, aliases = self.get_library_data()
        for msg in util.result_messages(
                'Library Creator',
                self._library_manager.library_creator_result()):
            self.library_output.emit(msg)
        self.set_library_data(tags, lib, aliases)

    def set_library_data(self, tags, libs, aliases):
        library_ids = dict(self._library_ids)
        old_library_id_set = set(self._library_ids)
        self.clear()
        self._library_data = (tags, libs, aliases)

        if tags:
            tags = LibraryTags.from_dict(tags)
        else:
            tags = None

        for k, v in aliases.items():
            datatypes.register_datatype(k, v['icon'])

        for lib in libs:
            library = Library.from_dict(lib)
            if sympathy.platform.feature.satisfies(library.required_features):
                self._root_library.add_library(library)
                self._register_library(library)
                self._library_ids[library.identifier] = (
                    library.uri, library.name, library.installed)

        new_library_id_set = set(self._library_ids)
        global_paths = util.global_library_paths()

        def is_global_path(path):
            try:
                for global_path in global_paths:
                    if samefile(path, global_path):
                        return True
            except Exception:
                pass
            return False

        for library_id in sorted(old_library_id_set - new_library_id_set):
            path, name, installed = library_ids[library_id]
            user_statistics.user_unloaded_library(
                library_id, path, name, installed or is_global_path(path))

        for library_id in sorted(new_library_id_set - old_library_id_set):
            path, name, installed = self._library_ids[library_id]
            user_statistics.user_loaded_library(
                library_id, path, name, installed or is_global_path(path))

        # TODO(erik): tags and types should only be provided from
        # active libraries.
        self._root_library.set_tags(tags)

        self.library_added.emit()
        self.library_aliases.emit(aliases)

    def get_library_data(self, update=True):
        if not update and self._library_data:
            return self._library_data

        tags = self._library_manager.library_tags()
        lib = self._library_manager.libraries()
        aliases = self._library_manager.typealiases()
        return tags, lib, aliases

    def reload_documentation(self, library=None, output_folder=None,
                             excluded_exts=None):
        if output_folder is None:
            if library is not None:
                output_folder = os.path.join(library, 'Docs')
            else:
                output_folder = self._get_default_documentation_path()
        self._library_manager.create_library_doc(
            self._root_library, output_folder, library_dir=library,
            excluded_exts=excluded_exts)

    def get_documentation_builder(self, output_folder=None):
        output_folder = output_folder or self._get_default_documentation_path()
        return self._library_manager.get_documentation_builder(
            self._root_library, output_folder)

    def _get_default_documentation_path(self):
        return os.path.join(
            self._library_manager.application_directory, 'Docs')

    def add_library(self, library_uri):
        library = Library.from_uri(library_uri)
        self._register_library(library)
        self._root_library.add_library(library)

    def set_tags(self, tags):
        self._tags = tags

    def clear(self):
        self._library_ids.clear()
        self._node_registry.clear()
        self._root_library.clear()
        self._root_library._name = 'Root'
        self._root_library._tags = None

    def is_in_library(self, node_identifier, libraries=None):
        node = self._node_registry.get(node_identifier)
        if node is not None:
            if node.installed:
                return True
            else:
                return libraries is None or (
                    os.path.normcase(os.path.abspath(
                        os.path.dirname(uri_to_path(node.library))))
                    in libraries)
        return False

    def library_node_from_definition(self, node_identifier, definition):
        try:
            # TODO: Using None for parent_library_identifier, allowing it
            # to be set could be useful when creating flow library nodes.
            # First argument is not used and could be removed.
            return LibraryNode.from_definition(None, definition)
        except Exception:
            core_logger.warning('Node "%s" could not be added to library.',
                                node_identifier)

    def library_node(self, node_identifier):
        return self._node_registry[node_identifier]

    def register_node(self, node_identifier, node):
        if node_identifier not in self._node_registry:
            self._node_registry[node_identifier] = node

    def unregister_node(self, node_identifier):
        if node_identifier in self._node_registry:
            del self._node_registry[node_identifier]

    def root(self):
        return self._root_library

    def typealiases(self):
        return self._library_manager.typealiases()

    def _register_library(self, library):
        for node in library.nodes:
            self.register_node(node.node_identifier, node)

        for library_ in library.libraries:
            self._register_library(library_)


def is_platform_node(node):
    if node and node.library_id:
        return is_combine_library_id(node.library_id)
    return False
