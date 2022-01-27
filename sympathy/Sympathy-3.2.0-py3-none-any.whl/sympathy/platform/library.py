# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
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
import typing as _t
import fnmatch
import pkg_resources
import sympathy.utils.library_info
from . import plugins


def scan_files(root, filename_pattern='*'):
    res = []
    for dirpath, dirnames, filenames in os.walk(root, True):
        res.extend([os.path.join(dirpath, fn) for fn in fnmatch.filter(
            filenames, filename_pattern)])
    return res


# Serialization:

def to_dict(library):
    res = {}
    res['identifier'] = library.identifier()
    res['name'] = library.name()
    res['description'] = library.description()
    res['path'] = os.path.abspath(
        os.path.dirname(library.__file__))

    for key, default_func in [
            ('maintainer', default_maintainer),
            ('copyright', default_copyright),
            ('version', default_version),
            ('icon', default_icon),
            ('nodes', default_nodes),
            ('flows', default_flows),
            ('plugins', default_plugins),
            ('migrations', default_migrations),
            ('tags', default_tags),
            ('types', default_types),
            ('examples_path', default_examples_path),
            ('required_features', default_required_features),
            ('repository_url', default_repository_url),
            ('documentation_url', default_documentation_url),
            ('home_url', default_home_url),
    ]:
        try:
            func = getattr(library, key)
        except AttributeError:
            res[key] = default_func(library)
        else:
            res[key] = func()

    return res


# Default functions:

def default_maintainer(library):
    return ''


def default_copyright(library):
    return ''


def default_version(library):
    return ''


def default_icon(library):
    return ''


def default_nodes(library):
    return scan_files(
        os.path.dirname(library.__file__), 'node_*.py')


def default_flows(library):
    return scan_files(
        os.path.dirname(library.__file__), 'flow_*.syx')


def default_plugins(library):
    return scan_files(
        os.path.dirname(library.__file__), 'plugin_*.py')


def default_migrations(library):
    return scan_files(
        os.path.dirname(library.__file__), 'migrations_*.py')


def default_tags(library):
    return []


def default_types(library):
    return []


def default_required_features(library):
    return []


def default_examples_path(library):
    return os.path.join(os.path.dirname(library.__file__), 'examples')


def default_repository_url(library):
    return ''


def default_documentation_url(library):
    return ''


def default_home_url(library):
    return ''


# Library plugins:

_libraries = plugins.Plugin('sympathy.library.plugins', _t.Any)


def available_libraries(load=True):
    if load:
        return _libraries.plugins().values()
    else:
        return _libraries.entry_points().values()


def unavailable_libraries():
    return _libraries.errors().items()


def unsatisfied_libraries():
    return _libraries.require_errors().keys()


# Utilities:

def is_old_style(library_root):
    library_ini_path = os.path.join(library_root, 'library.ini')
    common_path = os.path.join(library_root, 'Common')
    library_path = os.path.join(library_root, 'Library')
    return os.path.exists(library_ini_path) or (
        os.path.exists(common_path) and os.path.exists(library_path))


def is_combine_library_id(identifier):
    return identifier.startswith('com.sympathyfordata.') or identifier in [
        'org.sysess.sympathy',
        'migrationstestlib',
    ]


def package_python_path(library_root):
    if is_old_style(library_root):
        return os.path.join(library_root, 'Common')
    else:
        return os.path.dirname(library_root)


def library_path(library_root):
    if is_old_style(library_root):
        library_name = sympathy.utils.library_info.library_name(
            library_root)
        if library_name:
            return os.path.join(library_root, 'Library', library_name)
        else:
            return os.path.join(library_root, 'Library')
    else:
        return library_root


def package_name(library_root):
    if is_old_style(library_root):
        return sympathy.utils.library_info.library_name(library_root)
    else:
        return os.path.basename(library_root)


# Accessors

def library_plugins(library):
    res = []
    try:
        res = library.plugins()
    except AttributeError:
        if library.__file__:
            res = default_plugins(library)
    return res
