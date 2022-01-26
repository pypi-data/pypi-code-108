# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
from collections import defaultdict
from typing import Dict, List, Optional, Set

from portmod.config.profiles import profile_exists, profile_parents
from portmod.functools import prefix_aware_cache
from portmod.globals import env
from portmod.repo import get_repo
from portmod.repo.metadata import get_masters
from portmodlib.atom import QualifiedAtom, atom_sat
from portmodlib.parsers.list import CommentedLine, read_list


@prefix_aware_cache
def get_masked(repo: Optional[str] = None) -> Dict[str, Dict[QualifiedAtom, List[str]]]:
    """
    Returns details about masked packages

    args:
        repo: Name of the repository in question, to be used outside the context of a prefix

    returns:
        A mapping of package Category-Package-Name strings to their comment and atom
        (noting that the atom can contain version specifiers, and the mapping is
        provided to facilitate efficient checks).
    """
    masked: Dict[str, Dict[QualifiedAtom, List[str]]] = defaultdict(dict)

    paths: List[str] = []

    if env.PREFIX_NAME:
        paths.extend(
            os.path.join(repo.location, "profiles") for repo in env.prefix().REPOS
        )
        paths.append(env.prefix().CONFIG_DIR)

        if profile_exists():
            paths.extend(profile_parents())
    elif repo:
        paths.append(get_repo(repo).location)
        for master in get_masters(repo):
            paths.append(master.location)

    for path in paths:
        if os.path.exists(os.path.join(path, "package.mask")):
            for line in read_list(os.path.join(path, "package.mask")):
                atom = QualifiedAtom(line)
                if isinstance(line, CommentedLine):
                    masked[atom.CPN][atom] = line.comment
                else:
                    masked[atom.CPN][atom] = []
    return masked


@prefix_aware_cache
def get_unmasked() -> Dict[str, Set[QualifiedAtom]]:
    """
    Returns a dictionary mapping Category-Package-Name strings to
    the precice atom which is unmasked
    """
    unmasked: Dict[str, Set[QualifiedAtom]] = defaultdict(set)

    path = env.prefix().CONFIG_DIR
    if os.path.exists(os.path.join(path, "package.unmask")):
        for line in read_list(os.path.join(path, "package.unmask")):
            atom = QualifiedAtom(line)
            unmasked[atom.CPN].add(atom)
    return unmasked


@prefix_aware_cache
def is_masked(atom: QualifiedAtom, repo: Optional[str] = None):
    if atom.CPN in get_masked(repo) and any(
        atom_sat(atom, masked) for masked in get_masked(repo)[atom.CPN]
    ):
        if atom.CPN not in get_unmasked() or not any(
            atom_sat(atom, unmasked) for unmasked in get_unmasked()[atom.CPN]
        ):
            return True

    return False
