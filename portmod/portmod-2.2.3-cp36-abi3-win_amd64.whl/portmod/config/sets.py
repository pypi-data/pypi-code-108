# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""Module for parsing and modifying sets such as @world"""

import os
from typing import Optional, Set

from portmod.config.profiles import get_system
from portmod.globals import env
from portmodlib.atom import Atom, atom_sat

BUILTIN_SETS = {
    "world",
    "selected",
    "system",
    "selected-packages",
    "selected-sets",
    "rebuild",
    "installed",
}


def is_selected(atom: Atom) -> bool:
    """
    Returns true if and only if a package matching the given Atom is selected

    Selected packages are either system packages, packages included in the world file,
    packages included in the world sets file, or local packages
    """
    selected = get_set("world")
    for selatom in selected:
        if atom_sat(atom, selatom):
            return True
    return False


def get_set(package_set: str, parent_dir: Optional[str] = None) -> Set[Atom]:
    """
    Returns the atoms contained in the given package set

    Builtin sets include:

    * ``world``: The combination of the system and the selected sets
    * ``selected``: All packages explicitly selected, \
                either directly or indirectly through a set
    * ``system``: Packages required by the system profile
    * ``selected-packages``: Packages explicitly selected by the user
    * ``selected-sets``: Sets explicitly selected by the user
    * ``local-packages``: Packages installed locally by the user
    * ``rebuild``: Packages which have been selected for rebuilding \
               due to changes in the system
    * ``installed``: All installed packages

    args:
        package_set: The name of the set (note that this should not include the @
                     symbol used to reference sets on the command line
        parent_dir: The directory which stores the set file. If not specified
                    will be determined automatically. Non-builtin sets
                    are stored in ``env.prefix().SET_DIR``

    returns:
        The atoms contained in the given package set
    """
    if package_set == "world":
        return get_set("system") | get_set("selected")
    if package_set == "selected":
        return (
            get_set("selected-packages")
            | get_set("selected-sets")
            | get_set("local-packages")
        )
    if package_set == "system":
        return get_system()
    if package_set == "installed":
        from portmod.loader import load_all_installed

        return {pkg.ATOM for pkg in load_all_installed()}

    if parent_dir is None:
        parent_dir = env.prefix().SET_DIR

    if package_set == "local-packages":
        local_dir = env.prefix().LOCAL_MODS
        if os.path.exists(local_dir):
            return set(
                map(
                    lambda name: Atom(f"local/{name}"),
                    os.listdir(local_dir),
                )
            )
        return set()

    set_file = _get_set_path(package_set, parent_dir)
    if os.path.exists(set_file):
        with open(set_file, "r") as file:
            return {Atom(s) for s in file.read().splitlines()}
    return set()


def _get_set_path(package_set: str, parent_dir: Optional[str] = None) -> str:
    if parent_dir is None:
        parent_dir = env.prefix().SET_DIR

    if package_set == "installed":
        raise RuntimeError("The @installed set cannot be modified by this function!")
    if package_set == "selected-packages":
        return os.path.join(env.prefix().VAR_SET_DIR, "world")
    if package_set == "selected-sets":
        return os.path.join(env.prefix().VAR_SET_DIR, "world_sets")
    if package_set in ("rebuild"):
        return os.path.join(env.prefix().VAR_SET_DIR, package_set)
    return os.path.join(parent_dir, package_set)


def add_set(package_set: str, atom: Atom, parent_dir: Optional[str] = None):
    """
    Adds an atom to a set

    args:
        package_set: Name of the set to modify
        atom: Package atom to add to the set
        parent_dir: The directory where the set file is located.
                    If not specified, defaults to the prefix's set directory
                    (a subdirectory of the config directory).
    """
    set_file = _get_set_path(package_set, parent_dir)

    os.makedirs(os.path.dirname(set_file), exist_ok=True)
    if os.path.exists(set_file):
        with open(set_file, "r+") as file:
            for line in file:
                if atom in line:
                    break
            else:
                print(atom, file=file)
    else:
        with open(set_file, "a+") as file:
            print(atom, file=file)


def remove_set(package_set: str, atom: Atom, parent_dir: Optional[str] = None):
    """
    Removes an atom from a set

    args:
        package_set: Name of the set to modify
        atom: Package atom to remove from the set. Must match the expected atom exactly.
        parent_dir: The directory where the set file is located.
                    If not specified, defaults to the prefix's set directory
                    (a subdirectory of the config directory).
    """
    set_file = _get_set_path(package_set, parent_dir)
    if os.path.exists(set_file):
        with open(set_file, "r+") as file:
            new_f = file.readlines()
            file.seek(0)
            for line in new_f:
                if atom not in line:
                    file.write(line)
            file.truncate()
