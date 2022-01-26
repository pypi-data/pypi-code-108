# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module for directly loading pybuild files.
These functions should not be called directly.
See portmod.loader for functions to load pybuilds safely using a sandbox.
"""

import glob
import os
from copy import deepcopy
from logging import warning
from types import SimpleNamespace
from typing import Callable, Dict, Generator, Optional, cast

from portmod.config.mask import is_masked
from portmod.functools import install_cache, prefix_aware_cache, system_cache
from portmod.globals import env
from portmod.lock import vdb_lock
from portmod.parsers.manifest import Manifest
from portmod.repo import Repo, get_repo, get_repo_name
from portmod.repo.metadata import get_categories, get_masters
from portmod.util import get_max_version
from portmod.vdb import VDB
from portmodlib._loader import (
    SAFE_GLOBALS,
    __load_file_common,
    __load_installed_common,
    restricted_load,
)
from portmodlib.atom import Atom, FQAtom, QualifiedAtom, VAtom, atom_sat
from portmodlib.l10n import l10n
from portmodlib.pybuild import File, FullPybuild, InstallDir

from .updates import get_moved


def commit_moved():
    """
    Moves installed packages which have been moved

    Should be run prior to entering the sandbox,
    as otherwise moved packages will not be visible
    """
    for repo in env.prefix().REPOS:
        moved = get_moved(repo)
        for source, dest in moved.items():
            atom = QualifiedAtom(source)

            path = os.path.join(env.prefix().INSTALLED_DB, atom.C, atom.PN)
            if os.path.exists(path):
                destatom = QualifiedAtom(dest)
                destpath = os.path.join(
                    env.prefix().INSTALLED_DB, destatom.C, destatom.PN
                )
                for filepath in glob.glob(os.path.join(path, "*.pybuild")):
                    oldatom = get_atom_from_path(filepath)
                    if oldatom.R != repo.name:
                        with VDB(l10n("moved-package", src=source, dst=dest)) as vdb:
                            newfile = f"{destatom.PN}-{oldatom.PVR}.pybuild"
                            vdb.git.mv(filepath, os.path.join(path, newfile))
                            vdb.git.mv(path, destpath)
                            break


def find_installed_path(atom: Atom) -> Optional[str]:
    repo_path = env.prefix().INSTALLED_DB

    # Handle renames:
    # Check all possible renames for this atom (all repos), and they are only valid if
    # the package comes from the repo matching the rename entry
    for repo in env.REPOS:
        moved = get_moved(repo)
        if atom.CPN in moved:
            moved_atom = QualifiedAtom(moved[atom.CPN])
            path = os.path.join(repo_path, moved_atom.C, moved_atom.PN)
            if os.path.exists(path):
                with open(os.path.join(path, "REPO"), "r") as file:
                    if repo.name == file.read().strip():
                        atom = moved_atom
                        break

    if atom.C:
        path = os.path.join(repo_path, atom.C, atom.PN)
        if os.path.exists(path):
            results = glob.glob(os.path.join(path, "*.pybuild"))
            assert len(results) == 1
            return results[0]
    else:
        for dirname in glob.glob(os.path.join(repo_path, "*")):
            path = os.path.join(repo_path, dirname, atom.PN)
            if os.path.exists(path):
                results = glob.glob(os.path.join(path, "*.pybuild"))
                assert len(results) == 1
                return results[0]
    return None


# Make sure this is only run once since _iterate_pybuilds is called many times
@system_cache
def check_repo_exists(name: str, location: str):
    if not os.path.exists(location):
        warning(
            l10n(
                "repo-does-not-exist-warning",
                name=name,
                path=location,
                command="portmod sync",
            )
        )


def _iterate_pybuilds(
    atom: Optional[Atom] = None,
    repo_name: Optional[str] = None,
    only_repo_root: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Iterates over pybuilds.

    If no repository is given, checks all available.
    If a repository name is given, checks that repository and its masters

    if only_repo_root is specified, only checks the repository at the given location
    """
    path = None
    repos = []
    if env.PREFIX_NAME:
        repos = env.prefix().REPOS
    else:
        repos = env.REPOS

    if repo_name is not None:
        repo = get_repo(repo_name)
        repos = [repo]
        for master in get_masters(repo.location):
            yield from _iterate_pybuilds(atom, master.name)
    elif only_repo_root:
        repos = [Repo(location=only_repo_root, name=get_repo_name(only_repo_root))]

    def valid_atom(desired_atom: Atom, other: Atom):
        if isinstance(desired_atom, FQAtom):
            return desired_atom == other
        else:
            return atom_sat(other, desired_atom)

    def try_move_atom(moved: Dict[str, str], atom: QualifiedAtom, repo):
        true_atom = atom
        if atom.CPN in moved:
            true_atom = QualifiedAtom(moved[atom.CPN])
            if atom.PVR:
                true_atom = QualifiedAtom(f"{true_atom}-{atom.PVR}")
        return true_atom

    for repo in repos:
        check_repo_exists(repo.name, repo.location)
        if atom:
            moved = get_moved(repo)
            if atom.C:
                true_atom = try_move_atom(moved, cast(QualifiedAtom, atom), repo)
                path = os.path.join(repo.location, true_atom.C, true_atom.PN)
                if path is not None:
                    for file in glob.iglob(os.path.join(path, "*.pybuild")):
                        if valid_atom(true_atom, get_atom_from_path(file)):
                            yield file
            else:
                for category in get_categories(repo.location):
                    true_atom = try_move_atom(moved, atom.with_category(category), repo)
                    path = os.path.join(repo.location, category, true_atom.PN)

                    if path is not None:
                        for file in glob.iglob(os.path.join(path, "*.pybuild")):
                            if valid_atom(true_atom, get_atom_from_path(file)):
                                yield file
        else:
            for file in glob.iglob(os.path.join(repo.location, "*", "*", "*.pybuild")):
                yield file


@system_cache
def _import_common(
    name: str,
    installed: bool,
    load_function: Callable,
    repo: Optional[str] = None,
) -> SimpleNamespace:
    """
    args:
        name: The import name as an absolute import path
        installed: Whether or not the package calling this is an installed package
        load_function: The function taking a file path and a keyword argument installed,
            indicating the installed status of the file to be loaded, to be used to load
            the common module

    returns:
        The Module as a SimpleNamespace
    """
    if len(name.split(".")) > 2:
        raise Exception(f"Invalid package {name}")
    _, module_name = name.split(".")
    base_atom = Atom(f"common/{module_name}")
    if installed:
        path = find_installed_path(base_atom)

    if installed and path:
        result = load_function(path, installed=True, repo=None)
    else:
        versions = {}
        for file in _iterate_pybuilds(base_atom, repo_name=repo):
            basename, _ = os.path.splitext(os.path.basename(file))
            atom = VAtom("common/" + basename)
            if not is_masked(atom, repo):
                versions[atom.PVR] = file

        max_version = get_max_version(versions.keys())
        if not max_version:
            raise Exception(f"Could not find package {name}")

        result = load_function(versions[max_version], installed=False, repo=repo)

    return SimpleNamespace(
        **{key: value for key, value in result.items() if not key.startswith("_")}
    )


def __safe_load_file(path: str, *, installed=False) -> FullPybuild:
    """
    Loads a pybuild file

    :param path: Path of the pybuild file
    """
    repo = get_repo_name(path) if not installed else None
    module = __safe_load_module(path, installed, repo)
    pkg = __load_file_common(path, module, installed)

    pkg.ATOM = get_atom_from_path(path)
    pkg.REPO = pkg.ATOM.R
    if installed:
        with vdb_lock():
            __load_installed_common(pkg, path)
            parent = os.path.dirname(path)
            pkg.INSTALLED_REBUILD_FILES = None
            path = os.path.join(parent, "REBUILD_FILES")
            if os.path.exists(path):
                try:
                    pkg.INSTALLED_REBUILD_FILES = Manifest(path)
                except ValueError:
                    warning(f"Failed to load {path}")
    return cast(FullPybuild, pkg)


@prefix_aware_cache
def pkg_exists(atom: Atom, *, repo_name: Optional[str] = None) -> bool:
    """Returns true if a package with the given atom can be found in the given repository"""
    return next(_iterate_pybuilds(atom, repo_name), None) is not None


def __safe_load_module(path: str, installed: bool, repo: Optional[str]):
    try:
        atom: Optional[FQAtom] = get_atom_from_path(path)
    except Exception:
        atom = None

    def get_info():
        assert atom
        return {
            "CATEGORY": atom.C,
            "P": atom.P,
            "PF": atom.PF,
            "PN": atom.PN,
            "PV": atom.PV,
            "PR": atom.PR,
            "PVR": atom.PVR,
            "__name__": "pybuild.info",
        }

    def get_pybuild():
        # File/InstallDir/Pybuild1 objects are instead passed as functions
        # to prevent modification of class attributes.
        # the instances are safe as long as underscored attributes are inaccessible

        def file_func(*args, **kwargs):
            return File(*args, **kwargs)

        def install_dir_func(*args, **kwargs):
            return InstallDir(*args, **kwargs)

        # create simplified version of Pybuild to use for inheritance.
        # It has default values for all the pyubild fields.
        # We don't use FullPybuild directly to prevent its fields being modified
        # This class is generated within a function, and thus will not be the same
        # for any two packages.
        class Pybuild1(FullPybuild):
            """Generated Pybuild1 for use in non-sandboxed loader"""

        return {
            "File": file_func,
            "InstallDir": install_dir_func,
            "Pybuild1": Pybuild1,
            "DOWNLOAD_DIR": env.DOWNLOAD_DIR,
            "version_gt": None,
            "find_file": None,
            "use_reduce": None,
            "check_required_use": None,
            "patch_dir": None,
            "get_masters": None,
            "apply_patch": None,
            "__name__": "pybuild",
        }

    def get_typing():
        import typing

        result = {}

        for attr, value in typing.__dict__.items():
            if not attr.startswith("_") and not isinstance(value, type(typing)):
                result[attr] = deepcopy(value)

        return result

    def _import(name, _globs, _loc, _fromlist, _level):
        if name.startswith("common."):
            return deepcopy(_import_common(name, installed, __safe_load_module, repo))
        if name == "pybuild":
            return SimpleNamespace(**get_pybuild())
        if name == "pybuild.info":
            return SimpleNamespace(**get_info())
        if name == "typing":
            return SimpleNamespace(**get_typing())
        if _fromlist:
            return SimpleNamespace(**{item: None for item in _fromlist})
        else:

            class NoAttr:
                def __getattr__(self, attr):
                    # Necessary so that the object can be copied
                    # Note that RestrictedPython prevents use of such attributes through ast parsing
                    if attr.startswith("_"):
                        return super().__getattr__(attr)  # type: ignore  # pylint: disable=no-member
                    raise RuntimeError(
                        f"Cannot use {name}.{attr}: Complex code in the global scope is not allowed!"
                    )

            return NoAttr()

    filename, _ = os.path.splitext(os.path.basename(path))

    with open(path, "r", encoding="utf-8") as file:
        code = file.read()
        tmp_globals = deepcopy(SAFE_GLOBALS)
        tmp_globals["__builtins__"]["__import__"] = _import
        tmp_globals["__name__"] = filename
        restricted_load(code, path, tmp_globals)
        for _global in tmp_globals.values():
            # Note: we can't use hasattr here, as we want to set the attribute for this classmethod
            if isinstance(_global, type) and "__file__" not in _global.__dict__:
                try:
                    setattr(_global, "__file__", path)
                except:  # noqa
                    ...

    return tmp_globals


def _iterate_installed() -> Generator[str, None, None]:
    repo = env.prefix().INSTALLED_DB

    for path in glob.glob(os.path.join(repo, "*", "*", "*.pybuild")):
        yield path


@install_cache
def get_atom_from_path(path: str) -> FQAtom:
    repopath, filename = os.path.split(os.path.abspath(os.path.normpath(path)))
    atom, _ = os.path.splitext(filename)
    repopath, _ = os.path.split(repopath)
    repopath, C = os.path.split(repopath)
    try:
        repo_name = get_repo_name(repopath)
    except FileNotFoundError as e:
        path = os.path.join(os.path.dirname(path), "REPO")
        if os.path.exists(path):
            with open(path, "r") as file:
                repo_name = file.read().strip() + "::installed"
        else:
            raise e
    return FQAtom(f"{C}/{atom}::{repo_name}")
