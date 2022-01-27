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
import inspect
import itertools
import tempfile
import os
import shutil
import sys
import traceback
import glob
from collections import OrderedDict

import sympathy.app.wizards.wizard_helper_functions as whf
from sympathy.app import migrations
from sympathy.utils.prim import localuri
import sympathy.platform.library
from sympathy.platform.library import is_combine_library_id
from sympathy.platform.parameter_helper import ParameterRoot
from sympathy.platform.parameter_helper_visitors import ReorderVisitor
from sympathy.platform import node as synode
from sympathy.platform import version_support as vs
from sympathy.platform.exceptions import sywarn
from sympathy.platform import workflow_converter
from sympathy.utils.context import trim_doc, is_original
from sympathy.utils import tag
from sympathy.utils import port
from sympathy.utils import library_info
from sympathy.utils import components

fs_encoding = sys.getfilesystemencoding()

pid = os.getpid()
hashings = 'md5', 'mtime'
hashing = hashings[0]


def new_style_library_package(library_root):
    """
    Return package pointed to by the library_root.
    """
    package_name = os.path.basename(library_root)
    if package_name and len(package_name):
        return __import__(package_name)
    raise ImportError(
        'No library package found in: "{}".'.format(library_root) +
        '\nThe library can not be used.')


def old_style_library_package(library_root):
    """
    Return the Common package pointed to by the library.ini file.
    """
    package_name = library_info.instance()[
        library_root].package_name()
    if package_name and len(package_name):
        return __import__(package_name)
    raise ImportError(
        'No common package found in library: "{}".'.format(library_root) +
        '\nThe library has been imported, but it is recommended to ' +
        'create this package in the library structure.' +
        '\nUse the Library Wizard to see an example of this.')


def check_file_for_classes(node):
    """
    Search a module and locate classes that are subclassed from node.Node.
    Returns list of located clases.
    """
    classes = []
    mod_name = os.path.basename(os.path.splitext(node)[0])
    node_path = vs.str_(os.path.dirname(node), vs.fs_encoding)
    if node_path not in sys.path:
        sys.path.append(node_path)

    mod_ = components.import_file(node)
    members = OrderedDict(inspect.getmembers(mod_))

    for name, instance in [mod for mod in members.items()
                           if not mod[0].startswith('_')]:
        if inspect.isclass(instance) and issubclass(instance,
                                                    synode.BasicNode):
            classes.append((mod_name, name, instance))
    return classes


NAME = 'name'
NODEID = 'nodeid'


def plugin_data_base(plugin_cls):
    mod = sys.modules[plugin_cls.__module__]
    return {
        'full': f'{plugin_cls.__module__}.{plugin_cls.__name__}',
        'class': plugin_cls.__name__,
        'file': localuri(mod.__file__),
        'name': plugin_cls.plugin_base_name()}


def plugin_data_impl(plugin_cls):
    mod = sys.modules[plugin_cls.__module__]
    return {
        'class': plugin_cls.__name__,
        'file': localuri(mod.__file__),
        'name': plugin_cls.plugin_impl_name()}


def get_properties(node, class_name, instance):
    """
    Return dictionary of select properties extracted from class instance.
    """
    def to_dict(params):
        try:
            return params._parameter_dict
        except AttributeError:
            return params

    top_level = (
        'author',
        'class',
        'copyright',
        'description',
        'file',
        'icon',
        NAME,
        NODEID,
        'type',
        'version')

    required_fields = (
        NAME,
        NODEID)

    translation_dict = {'nodeid': 'id', 'name': 'label'}

    members = dict(inspect.getmembers(instance))
    has_required = True
    properties = {}
    original = True

    # Mark classes that don't need to be validated.

    if 'verify_parameters' in members:
        original &= is_original(
            instance.verify_parameters)
    if 'verify_parameters_basic' in members:
        original &= is_original(
            instance.verify_parameters_basic)
    if 'verify_parameters_managed' in members:
        original &= is_original(
            instance.verify_parameters_managed)

    properties['validate'] = not original

    try:
        properties['parameters'] = {}
        parameters = members['parameters']
        properties['parameters']['data'] = to_dict(parameters)
        properties['parameters']['type'] = 'json'
        parameter_root = ParameterRoot(parameters)
        reorder_visitor = ReorderVisitor()
        parameter_root.accept(reorder_visitor)
    except Exception:
        pass

    if 'tags' in members:
        try:
            properties['tags'] = members['tags'].to_dict()
        except Exception:
            pass

    if 'plugins' in members:
        properties['plugins'] = [
            plugin_data_base(plugin_cls)
            for plugin_cls in members['plugins']]

    if 'related' in members:
        properties['related'] = members['related']

    nodedir = os.path.dirname(node)
    for f in top_level:
        properties[f] = ''

    if not (members.get(NODEID) and members.get(NAME)):
        # Assuming that the node is a base class.
        return

    for origin, target in translation_dict.items():
        properties[target] = members[origin]

    for field in top_level:
        if field in members:
            properties[field] = members[field]
            if not isinstance(members[field], str):
                sywarn('[{}] field {} is not a string'.format(node, field))
        elif field in required_fields:
            sywarn('*** {0} is missing from {1}'.format(field, class_name))
            has_required = False

    field = '__doc__'
    doc = members.get(field)
    if doc:
        doc = trim_doc(doc)
    properties[field] = doc

    field = 'deprecated'
    deprecated = members.get(field)
    properties[field] = deprecated

    if not has_required:
        # When making a node be sure to include all require fields.
        return

    try:
        properties['ports'] = port.port_structures_to_dict(
            members.get('inputs'),
            members.get('outputs'))
    except Exception as e:
        sywarn(f"*** {class_name}: {e}")
        return

    # Check if we have a resource directory where icons could reside.
    icon = members.get('icon')
    if icon:
        icon_path = workflow_converter.icon_dirs_path(
            icon, [os.path.join(nodedir, '_resources'), nodedir])
        if icon_path:
            properties['icon'] = localuri(icon_path)
        else:
            sywarn("Couldn't find icon for node {}".format(properties[NAME]))

    properties['type'] = 'python2'
    properties['file'] = localuri(node)
    properties['class'] = class_name
    return properties


def get_node_data_list(py_file):
    """
    Return a dictionary with the properties from each class in py_file.
    """
    return [(class_name, get_properties(py_file, class_name, instance))
            for (name, class_name, instance)
            in check_file_for_classes(py_file)]


def get_flow_data_list(syx_flow):
    """
    Get data from flow file.

    Parameters
    ----------
    syx_flow : str
        Flow filename

    Returns
    -------
    [(str, dict)]
        List containing one dictionary of flow properties or empty list.
    """

    properties = workflow_converter.get_flow_data(syx_flow)
    flow_name = os.path.basename(syx_flow)

    if properties and properties.get('id'):
        return [(flow_name, properties)]
    return []


def create_json_filename(name, dest):
    """
    Create a new json file with given properties at dest.
    Return the path to the new file.
    """
    return '{0}.json'.format(os.path.join(dest, name))


def create_json_file(name, props, dest):
    """
    Create a new json file with given properties at dest.
    Return the path to the new file.
    """
    js_node = create_json_filename(name, dest)

    with open(js_node, 'wb') as js_file:
        js_file.write(vs.encode(vs.json_dumps(
            props, indent=4, sort_keys=True,), 'utf8'))
    return js_node


def get_cache_path(cache, py_file):
    """
    Return the folder where json files for nodes that are defined in py_file
    will be stored.
    """
    res = None
    epy_file = py_file.encode('utf8')
    if hashing == 'md5':
        with open(py_file, 'rb') as f:
            res = os.path.join(
                cache, components.hashstrings([epy_file, f.read()]))
    elif hashing == 'mtime':
        mtime = str(os.path.getmtime(py_file))
        res = os.path.join(cache, components.hashstrings([epy_file, mtime]))
    else:
        assert False, 'Only md5 and mtime are supported.'

    return res


def get_cached_paths(cache, py_file):
    try:
        path = get_cache_path(cache, py_file)
        return [os.path.join(path, name) for name in os.listdir(path)]
    except Exception:
        return None


def create_tags(tagslist):
    tagslist = [tags() for tags in tagslist]
    if tagslist:
        return tag.LibraryTags.merge(tagslist).to_dict()
    return tag.NullLibraryTags().to_dict()


def create_types(typealiases):
    return {
        typealias.container_type.name():
        {'name': typealias.container_type.name(),
         'type': repr(typealias.container_type.get()),
         'icon': typealias.icon(),
         'util': '{}:{}'.format(typealias.__module__,
                                typealias.__name__)}
        for typealias in typealiases}


def create_library_data_directory(temp, js_nodes, py_nodes, syx_flows):
    """
    Create the nodes for a library directory. Can run in parallel for
    whatever gains that may bring.

    However for the current library the gain is small and therefore this
    is not run in parallel.

    Return list of js_node paths.
    """

    # Create json files from python node files.
    cache = os.path.join(temp, 'json')
    path_nodes = {}

    try:
        os.makedirs(cache)
    except (IOError, OSError):
        # Assume already existing.
        pass

    def create_js_cache(flodes, props_fun):
        for flode in flodes:
            # Attempt to get cached files.
            cached = get_cached_paths(cache, flode)
            if cached is not None:
                path_nodes.setdefault(flode, []).extend(cached)
            else:
                tempdir = None
                try:
                    tempdir = tempfile.mkdtemp(
                        prefix=str(os.getpid()), dir=cache)
                    js_dir = get_cache_path(cache, flode)
                    # Nothing cached, create files.
                    items = []
                    for name, props in props_fun(flode):
                        if props is not None:
                            create_json_file(name, props, tempdir)
                            items.append(create_json_filename(name, js_dir))
                    path_nodes.setdefault(flode, []).extend(items)
                    try:
                        os.rename(tempdir, js_dir)
                    except OSError:
                        # The directory seems to already exist. This means that
                        # another Sympathy instance created it just now, so we
                        # don't need to do anything here.
                        pass
                except Exception:
                    sywarn('Node error, failed to generate: {}'.format(flode))

                    # traceback.format_exc() gives a traceback encoded with
                    # fsencoding so we need to decode it.
                    sywarn(vs.decode(traceback.format_exc(), fs_encoding))
                    try:
                        shutil.rmtree(tempdir)
                    except Exception:
                        pass

    create_js_cache(py_nodes, get_node_data_list)
    create_js_cache(syx_flows, get_flow_data_list)
    return path_nodes


def create(source_dirs, temp, session):
    """Create library."""

    def create_missing_ini(library_root):
        info = whf.find_library_info(library_root)
        return whf.create_ini(library_root + '/' + whf.LIBRARY_INI, **info)

    def check_single_package(folder):
        pyfiles = os.path.join(folder, '*.py')
        pycfiles = os.path.join(folder, '*.pyc')
        initpy = os.path.join(folder, '*', '__init__.py*')
        initfiles = glob.glob(initpy)
        len_initfiles = len(initfiles)

        if glob.glob(pyfiles):
            sywarn('{} contains .py files'.format(folder))

        if glob.glob(pycfiles):
            sywarn('{} contains .pyc files'.format(folder))

        if len_initfiles == 2:
            pyfile, pycfile = sorted(initfiles)
            if not (len(pyfile) == len(pycfile) - 1 and
                    pyfile == pycfile[:-1]):
                sywarn('{} should contain only single package'.format(folder))
        elif len_initfiles > 2:
            sywarn('{} should contain only single package'.format(folder))

    libraries = []
    new_style_packages = []
    old_style = []

    for library in source_dirs:
        if os.path.exists(library):
            if sympathy.platform.library.is_old_style(library):
                old_style.append(library)
            else:
                try:
                    new_style_packages.append(
                        new_style_library_package(library))
                except Exception as e:
                    sywarn(
                        f'Failed to load library {library} due to {e}.')

    installed_libraries = list(sympathy.platform.library.available_libraries())
    for k, e in sympathy.platform.library.unavailable_libraries():
        sywarn(f'Failed to load library plugin {k} due to {e}.')

    for k in sympathy.platform.library.unsatisfied_libraries():
        sywarn(f'Library plugin {k} has unsatisfied requirements and may not '
               f'work properly.')

    for package in itertools.chain(
            installed_libraries, new_style_packages):
        issues = []
        try:
            library_dict = sympathy.platform.library.to_dict(package)
            ok = True
        except Exception as e:
            library_dict = {}
            ok = False
            issues.append(str(e))
        else:
            ident = library_dict['identifier']
            library = library_dict['path']
            local_tags = library_dict['tags']
            local_types = library_dict['types']

        try:
            # Serialization for tags and types.
            library_dict['tags'] = create_tags(local_tags)
            library_dict['types'] = create_types(local_types)
        except Exception as e:
            ok = False
            issues.append(str(e))

        if ok:
            library_dict['style'] = 'new'
            library_dict['package'] = package.__name__
            library_dict['js_nodes'] = create_library_data_directory(
                temp, [], library_dict['nodes'], library_dict['flows'])
            library_dict['root'] = os.path.dirname(os.path.abspath(
                package.__file__))
            library_dict['installed'] = package in installed_libraries
            libraries.append(library_dict)
        else:
            sywarn(
                'Attempted to load invalid library package: '
                '{package}:\n* {issues}'.format(
                    package=package,
                    issues='\n* '.join(issues)))

    for library in old_style:

        ok = False
        inipath = os.path.normpath(os.path.join(library, whf.LIBRARY_INI))
        library_info.create_library_info(inipath, library)
        local_types = []
        local_tags = []
        library_dict = {'style': 'old'}

        try:
            try:
                package = old_style_library_package(library)
                try:
                    local_types.extend(package.library_types())
                except AttributeError:
                    pass
                try:
                    local_tags.extend(package.library_tags())
                except AttributeError:
                    pass
            except ImportError:
                sywarn(
                    f'Failed to import library package for {library}.\n'
                    'This may be caused by missing or incompatible packages '
                    'in your python environment.'
                    '\n\n')
                traceback.print_exc()
            except KeyError:
                sywarn('library.ini missing General:common_path option')
        except (IOError, OSError):
            # message = (
            #     'library.ini was missing or cannot be read for library '
            #     f'"{library}".')
            pass
        except ValueError:
            ok = False
            sywarn('Library "' + library + '" could not be fully imported. '
                   u'Common_path should end with '
                   'slash followed by the package name.')
        else:
            ok = True
            try:
                library_dict['package'] = package.__name__ if package else ''
                general = library_info.instance()[library]['General']

                ident = general['identifier']
                library_dict['identifier'] = ident

                for key in ['maintainer', 'copyright', 'description', 'icon']:
                    library_dict[key] = general.get(key, '')

                library_dict['repository_url'] = general.get('repository', '')
                library_dict['documentation_url'] = general.get(
                    'documentation', '')
                library_dict['home_url'] = general.get('home', '')

                library_dict['name'] = general.get(
                    'name', os.path.basename(library))

            except Exception:
                ok = False
            else:
                if not ident:
                    sywarn(
                        'Ignoring library: "{}" which has no identifier.'
                        .format(library))
                    ok = False

        try:
            # Serialization for tags and types.
            library_dict['tags'] = create_tags(local_tags)
            library_dict['types'] = create_types(local_types)
        except Exception as e:
            ok = False
            issues.append(str(e))

        library_ = os.path.normpath(os.path.join(library, 'Library'))
        if not os.path.isdir(library_):
            sywarn('Error in library: "{}". '
                   'It does not contain required subdirectory called '
                   '"Library" containing nodes'.format(library))
        elif ok:
            library_dict['required_features'] = []
            library_dict['installed'] = False
            library_dict['identifier'] = ident
            library_dict['root'] = os.path.abspath(library)
            library_dict['nodes'] = sympathy.platform.library.scan_files(
                os.path.join(library, 'Library'), 'node_*.py')
            library_dict['flows'] = sympathy.platform.library.scan_files(
                os.path.join(library, 'Library'), 'flow_*.syx')
            library_dict['plugins'] = sympathy.platform.library.scan_files(
                library, 'plugin_*.py')
            library_dict['migrations'] = sympathy.platform.library.scan_files(
                library, 'migrations_*.py')
            library_dict['examples_path'] = os.path.join(library, 'Examples')
            library_dict['js_nodes'] = create_library_data_directory(
                temp, [], library_dict['nodes'], library_dict['flows'])
            libraries.append(library_dict)

    for library_dict in libraries:
        plugins = {}

        for filename in library_dict['plugins']:
            for k, v in components.get_all_components(filename).items():
                plugins.setdefault(k, []).append(plugin_data_impl(v))

        plugins = [(plugin_data_base(k), vs) for k, vs in plugins.items()]
        library_dict['plugins_info'] = plugins

        migrations_ = {}
        if is_combine_library_id(library_dict['identifier']):
            for filename in library_dict['migrations']:
                for migr_cls in migrations.migrations_from_file(filename):
                    try:
                        migration_data = migration_data_impl(migr_cls)
                        nodeid = migration_data['nodeid']
                    except (KeyError, AttributeError) as e:
                        sywarn(f'*** Unable to load migration {migr_cls}: {e}')
                    migrations_.setdefault(nodeid, []).append(migration_data)

        library_dict['migrations_info'] = migrations_
    return libraries


def migration_data_impl(migration_cls):
    mod = sys.modules[migration_cls.__module__]
    return {
        'class': migration_cls.__name__,
        'file': localuri(mod.__file__),
        'nodeid': migration_cls.nodeid,
        'from_version': str(migration_cls.from_version),
        'to_version': str(migration_cls.to_version),
    }


class LibraryCreator(object):
    name = 'Library Creator'

    def __init__(self, *args, **kwargs):
        return

    def _future__init__(self, *args, **kwargs):
        return self

    def create(self, library_dirs, temp_dir, session_dir):
        libraries = create(library_dirs, temp_dir, session_dir)
        if libraries is None:
            libraries = []
        return libraries

    def source_file(self):
        return localuri(__file__).replace('.pyc', '.py')
