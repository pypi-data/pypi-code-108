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
import os
import sys
import fnmatch
import inspect
from collections import defaultdict, OrderedDict

import importlib
import hashlib

from . prim import containing_dirs
from .. platform import state, exceptions
from .. api import component


FILE_ENVS = {}
COMPONENTS = defaultdict(lambda: defaultdict(list))


def hashstrings(strings):
    m = hashlib.md5()
    for string in strings:
        m.update(string)
    return m.hexdigest()


def import_file(filename, add_hash=True):
    for ext in importlib.machinery.EXTENSION_SUFFIXES:
        if filename.endswith(ext):
            add_hash = False
            break

    modname = os.path.basename(filename).split('.', 1)[0].encode(
        'ascii', errors='replace').decode('ascii')
    if add_hash:
        pathhash = hashstrings([filename.encode('utf8')])
        name = f'{modname}_{pathhash}'
    else:
        name = modname
    mod = sys.modules.get(name)

    if mod is None:
        spec = importlib.util.spec_from_file_location(name, filename)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules[name] = mod
    assert mod is not None
    return mod


def import_text(text):
    pathhash = hashstrings([text.encode('utf8')])
    name = f'import_text_module_{pathhash}'
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    exec(text, mod.__dict__)
    return mod


class IComponent(object):
    """
    Base class for discoverable components.
    Specific interface for a particular kind of components should be determined
    by creating a subclass of IComponent.
    """
    pass


def get_support_dirs(dirs=None):
    """
    Return list of support directories to scan for components.
    The method relies on state.node_state().settings having following fields:
        'support_dirs'
        'library_dirs'
    These are normally setup by worker_subprocess.worker.
    """
    if not dirs:
        library = [
            path
            for path in state.node_state().settings.get('library_dirs') or []]

        commons = [os.path.join(path, 'Common')
                   for path in library]
        dirs = library + commons
    return containing_dirs(dirs)


def get_file_env(filename, no_raise=False):
    """
    Return the environment resulting from executing the file in an empty
    environment.
    """
    if filename in FILE_ENVS:
        return FILE_ENVS[filename]

    env = OrderedDict()
    env['__file__'] = filename

    try:
        env.update(inspect.getmembers(import_file(filename)))
        FILE_ENVS[filename] = env
    except Exception as e:
        if no_raise:
            import traceback
            print('Error compiling {}'.format(filename), file=sys.stderr)
            traceback.print_exc()
        else:
            raise exceptions.SyDataError(
                "Could not read source file.",
                details=str(e))
    return env


def get_text_env(text, no_raise=False):
    """
    Return the environment resulting from executing the text in an empty
    environment.
    """
    env = OrderedDict()

    try:
        env.update(inspect.getmembers(import_text(text)))
    except Exception as e:
        raise
        if no_raise:
            import traceback
            print('Error compiling text', file=sys.stderr)
            traceback.print_exc()
        else:
            raise exceptions.SyDataError(
                "Could not read text.",
                details=str(e))
    return env


def get_subclasses_env(env, baseclass):
    """Return the class instances in env."""
    res = {}

    for key, value in env.items():
        if inspect.isclass(value) and issubclass(value, baseclass):
            # TODO(erik): Hack, pass filename in a less nasty way.
            # Importing instead of evaluating would result in a better
            # behavior with __file__ already set on the MODULE.
            try:
                value.__file__ = env['__file__']
            except (KeyError, TypeError):
                pass
            res[key] = value
    return res


def _scan_components(pattern, kind, dirs=None):
    """
    Scan python path for available components matching pattern and kind.
    Pattern is a glob pattern matched against the filename and kind is the base
    class for a group of components.
    """
    import sympathy.platform.library as library_platform
    matches = []
    for path in get_support_dirs(dirs):
        for root, dirs, files in os.walk(path):
            matches.extend([os.path.abspath(os.path.join(root, f))
                            for f in fnmatch.filter(files, pattern)])
    for library in library_platform.available_libraries():
        matches.extend(library_platform.library_plugins(library))

    return [value
            for match in matches
            for value in get_subclasses_env(
                get_file_env(match, no_raise=True), kind).values()]


def get_all_components(filename):
    res = {}
    for cls in get_subclasses_env(
            get_file_env(filename, no_raise=True),
            component.NodePlugin).values():

        if cls.is_plugin():
            res[cls.plugin_base()] = cls
    return res


def get_components(pattern, kind, dirs=None):
    """
    Get list of components for the given kind.
    If no components are found, a scan is performed.
    """
    result = COMPONENTS[str(kind)]
    if result:
        return result
    else:
        result = _scan_components(pattern, kind, dirs)
        COMPONENTS[str(kind)] = result
    return result
