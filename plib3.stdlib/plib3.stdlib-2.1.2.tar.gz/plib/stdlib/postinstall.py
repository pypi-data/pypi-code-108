#!/usr/bin/env python3
"""
Module POSTINSTALL -- Post-install script utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains utilities for obtaining information
about installed Python modules and packages and running
scripts that were installed with them.
"""

import sys
import os
import importlib
import runpy
import sysconfig

from plib.stdlib.builtins import first


def get_install_scheme(import_name):
    """Find the installation scheme for module or package ``import_name``.
    
    This allows appropriate directories to be determined for post-install scripts
    that write or symlink additional files.
    """
    
    mod = importlib.import_module(import_name)
    dirpath = os.path.dirname(mod.__file__)
    if hasattr(mod, '__path__'):
        # Back out of the package directories
        for _ in range(len(import_name.split('.'))):
            dirpath = os.path.dirname(dirpath)
    dirpath = os.path.normcase(dirpath)
    paths = [
        (scheme, os.path.normcase(sysconfig.get_path(key, scheme)))
        for key in ('purelib', 'platlib')
        for scheme in sysconfig.get_scheme_names()
    ]
    result = first(
        scheme for scheme, path in paths
        if (path == dirpath) and scheme.startswith(os.name)
    )
    if (result is None) and (os.name == 'posix'):
        # Allows posix-specific heuristics for cases where Python sysconfig info is borked
        # (e.g., Ubuntu)
        basepath = "/usr/local" if 'local' in dirpath else "/usr"
        result = (basepath,)
    return result


def get_bin_dir(import_name):
    """Return the corresponding ``bin`` directory for module or package ``import_name``.
    """
    scheme = get_install_scheme(import_name)
    if isinstance(scheme, tuple):
        dirpath = scheme[0]
        return os.path.join(dirpath, 'bin')
    return sysconfig.get_path('scripts', scheme)


def get_share_dir(modname, import_name=None):
    """Return the corresponding ``share`` directory for module or package ``modname``.
    
    The ``import_name`` parameter allows for modules or packages which are
    imported under a different name than the name they are given in your
    ``setup.py`` file.
    """
    scheme = get_install_scheme(import_name or modname)
    if isinstance(scheme, tuple):
        dirpath = scheme[0]
        return os.path.join(dirpath, 'share', modname)
    return os.path.join(
        sysconfig.get_path('data', scheme),
        'share',
        modname
    )


def _get_share_script_dir(package_name, import_name=None, share_root=None):
    script_dir = get_share_dir(package_name, import_name)
    if share_root:
        script_dir = os.path.join(script_dir, share_root)
    return script_dir


def list_share_scripts(package_name, import_name=None, share_root=None):
    """Return list of share script directories for ``package_name``.
    
    The ``share_root`` parameter can be used to designate a subdirectory of
    the shared directory for ``package_name`` in which to look for share
    script directories.
    """
    
    names = []
    share_dir = _get_share_script_dir(package_name, import_name, share_root=share_root)
    for name in os.listdir(share_dir):
        fullname = os.path.join(share_dir, name)
        if os.path.isdir(fullname):
            for filename in os.listdir(fullname):
                if filename.endswith(".py"):
                    names.append((name, filename))
    return names


def run_share_script(dirname, package_name, import_name=None, share_root=None, script_basename=None):
    """Run script located in ``share`` directory ``dirname``.
    
    A common use case for this is running example programs distributed with a library
    (like those distributed with this library). If the programs are in a subdirectory
    of ``share/<dirname>`` (e.g., "examples" for example programs), pass the name of
    the subdirectory in ``share_root``.
    
    The ``package_name`` and ``import_name`` parameters are used to find the correct
    ``share`` directory by looking up the install scheme for the package.
    
    This function will normally run the first Python script it finds in the chosen
    directory; to tell it to run a specific script, pass the base name of the
    script (i.e., without any directory name, but with the ``.py`` extension if it
    has it) in ``script_basename``. (Note that this option can point to a script
    that does not have the ``.py`` extension.)
    """
    
    script_dir = _get_share_script_dir(package_name, import_name, share_root=share_root)
    script_dir = os.path.join(script_dir, dirname)
    script_basename = script_basename or first(f for f in os.listdir(script_dir) if f.endswith('.py'))
    if not script_basename:
        raise RuntimeError("Script not found for {} in {}".format(dirname, script_dir))
    script_path = os.path.join(script_dir, script_basename)
    runpy.run_path(script_path, run_name='__main__')


def _make_entry_point(name, dirname, package_name, import_name=None, share_root=None, script_basename=None):
    def _f():
        run_share_script(dirname, package_name, import_name, share_root=share_root, script_basename=script_basename)
    _f.__name__ = name
    return _f


def make_entry_points(modname, package_name, import_name=None, share_root=None):
    """Add entry point functions to ``mod`` for share scripts shipped with ``package_name``.
    """
    
    mod = sys.modules[modname]
    for dirname, script_basename in list_share_scripts(package_name, import_name, share_root=share_root):
        assert script_basename.endswith(".py")
        name = script_basename[:-3].replace("-", "_")
        setattr(mod, name, _make_entry_point(
            name, dirname, package_name, import_name, share_root=share_root, script_basename=script_basename)
        )


DEFAULT_INSTALL_SCHEME = (
    'osx_framework_user' if sys.platform == 'darwin' else
    'nt_user' if os.name == 'nt' else
    'posix_user'
)


def fix_scripts(install_scheme=DEFAULT_INSTALL_SCHEME):
    """Add the ``.py`` extension to scripts in the script directory for the given install scheme.
    
    Primarily for use on Windows, to fix the fact that scripts without a ``.py`` extension won't
    look executable to Windows, but if we ship the distribution with the ``.py`` extension on
    all scripts, then you have to type the ``.py`` on non-Windows systems to run the script
    (whereas on Windows you can just type the base name, no extension). Would not be necessary
    if a Windows Python installation had some way to tell the brain dead OS that it knows how
    to execute scripts with shebang lines, but don't hold your breath.
    """
    
    script_dir = sysconfig.get_path('scripts', install_scheme)
    if not os.path.isdir(script_dir):
        raise RuntimeError("Scripts directory not found for install scheme {}".format(install_scheme))
    for filename in os.listdir(script_dir):
        filename = os.path.join(script_dir, filename)
        if os.path.isfile(filename) and not filename.endswith(".py"):
            with open(filename, 'rb') as f:
                starting_bytes = f.read(2)
            if starting_bytes == b"#!":
                os.rename(filename, "{}.py".format(filename))
