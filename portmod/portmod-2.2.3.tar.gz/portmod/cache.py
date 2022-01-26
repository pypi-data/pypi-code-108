# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""Module for handling the pybuild cache"""

import json
import os
from logging import debug
from typing import Dict

from portmodlib.atom import FQAtom
from portmodlib.fs import get_hash
from portmodlib.pybuild import FullPybuild
from portmodlib.util import pybuild_dumper

from .config import get_config
from .globals import env, get_version
from .pybuild import InstalledPybuild, Pybuild, to_cache
from .repo.loader import __safe_load_file, get_atom_from_path


class PreviouslyEncounteredException(Exception):
    """Exception that has previously occurred and should be ignored"""

    def __init__(self, previous: Exception):
        super().__init__()
        self.previous = previous


# We store a cache of mods so that they are only loaded once
# when doing dependency resolution.
# Stores key-value pairs of the form (filename, Mod Object)
class Cache:
    _mods: Dict[str, Pybuild] = {}
    _failed: Dict[str, Exception] = {}

    def __init__(self):
        self._mods = {}

    def clear(self):
        self._mods = {}
        self._failed = {}

    def clear_path(self, path: str):
        if path in self._mods:
            del self._mods[path]
        if path in self._failed:
            del self._failed[path]


cache = Cache()


def clear_cache_for_path(path: str):
    """
    Clears the mod cache for the given path

    Should be called if a file is updated and may be accessed again before the program exits
    """
    global cache
    cache.clear_path(path)


def cache_valid(path: str) -> bool:
    """
    Determines if the cache file at the given path is valid

    Returns true if and only if the cache file at the given path exists,
    the version of portmod is the same as the version stored in the cache file
    and that all file hashes in the cache file are valid
    """
    if not os.path.exists(path):
        return False

    with open(path, "r", encoding="utf-8") as cache_file:
        try:
            mod = json.load(cache_file)
        except Exception:
            return False

    if mod.get("__portmod_version__") != get_version():
        return False

    if not mod.get("__hashes__", []):
        return False

    for file, file_hash in mod.get("__hashes__"):
        if not os.path.exists(file) or get_hash(file) != file_hash:
            return False

    return True


def create_cache_str(mod: FullPybuild, cache: bool = True) -> str:
    # Only include members declared in the Pybuild class.
    # Internal members should be ignored
    dictionary = to_cache(mod)

    if cache:
        dictionary["__portmod_version__"] = get_version()

    for key in get_config()["CACHE_FIELDS"]:
        if hasattr(mod, key):
            dictionary[key] = getattr(mod, key)

    hashes = [(mod.FILE, get_hash(mod.FILE))]
    if cache:
        for super_cl in mod.__class__.mro():
            # Note: All superclasses will be either in the common directory,
            # portmod builtin superclasses, or builtin objects

            # Note: __file__ is defined specifically by our loader, it is not usually
            # a member of a class object
            if hasattr(super_cl, "__file__"):
                filepath = super_cl.__file__  # type: ignore
                if (
                    os.path.basename(os.path.dirname(os.path.dirname(filepath)))
                    == "common"
                ):
                    hashes.append((filepath, get_hash(filepath)))

    dictionary["__hashes__"] = hashes
    return json.dumps(dictionary, default=pybuild_dumper, sort_keys=True)


def load_cache(path: str, installed: bool) -> Pybuild:
    # Don't try to load the pybuild if it previously failed this run
    if path in cache._failed:
        raise PreviouslyEncounteredException(cache._failed[path])

    atom = get_atom_from_path(path)
    repo_name = atom.R
    if installed:
        cache_file = os.path.join(env.prefix().PYBUILD_INSTALLED_CACHE, atom.C, atom.PF)
    else:
        cache_file = os.path.join(env.PYBUILD_CACHE_DIR, repo_name, atom.C, atom.PF)

    if not cache_valid(cache_file):
        from .loader import SandboxedError

        os.makedirs(os.path.dirname(cache_file), exist_ok=True)

        if not path.endswith(".pybuild"):
            raise Exception()
        try:
            cache_str = create_cache_str(__safe_load_file(path, installed=installed))
        except SandboxedError as e:
            cache._failed[path] = e
            raise e

        if not cache_str:
            err = Exception("Pybuild cache produced no output!")
            cache._failed[path] = err
            raise err

        try:
            with open(cache_file, "w", encoding="utf-8") as file:
                file.write(cache_str)
        except OSError:
            # If we fail to write the file, just load the package directly from the cache string
            # Sandboxed modules may not have write access to the package cache.
            debug(f"Failed to write cache file {cache_file}")
            dictionary = json.loads(cache_str)
            return _load_cache_dict(path, atom, dictionary, installed)

    with open(cache_file, "r", encoding="utf-8") as file:
        dictionary = json.load(file)
        return _load_cache_dict(path, atom, dictionary, installed)


def _load_cache_dict(file: str, atom: FQAtom, pkg: Dict, installed: bool) -> Pybuild:
    if installed:
        return InstalledPybuild(atom, cache=pkg, INSTALLED=installed, FILE=file)
    else:
        return Pybuild(atom, cache=pkg, INSTALLED=installed, FILE=file)


def __load_mod_from_dict_cache(file: str, *, installed=False) -> Pybuild:
    global cache
    dictionary = cache._mods

    if dictionary.get(file, False):
        return dictionary[file]
    else:
        mod = load_cache(file, installed)
        dictionary[file] = mod
        return mod
