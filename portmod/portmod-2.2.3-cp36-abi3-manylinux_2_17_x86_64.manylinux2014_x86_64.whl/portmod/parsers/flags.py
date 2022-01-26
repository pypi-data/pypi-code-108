# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module for interacting with use flag configuration files

These are files containing lines of the form:
    category/package-name flag -otherflag

Atoms in these files should always be qualified, but may be as general
or as specific as the specification allows, optionally using operators to match
specific versions or ranges of versions.
"""

import os
import re
from logging import info
from typing import Iterable, Optional, Set

from portmod.functools import system_cache
from portmodlib.atom import Atom, atom_sat
from portmodlib.l10n import l10n
from portmodlib.parsers.list import read_list


def get_flags(file: str, atom: Optional[Atom] = None) -> Set[str]:
    """
    Reads flags from a given file.

    args:
        file: Path of the file to be parsed
        atom: If non-None, file is assumed to be newline delimited
            with an atom followed by a list of flags on each line.
            If None, file is assumed to be a newline delimited list of flags
    returns:
        The set of flags contained in the file and matching the atom
    """
    flags: Set[str] = set()
    if os.path.exists(file):
        for line in read_list(file):
            # Remove comments
            line = re.sub("#.*", "", line)
            if not line:
                continue

            if atom:
                elem = line.split()
                line_atom = Atom(elem[0])
                if atom_sat(atom, line_atom):
                    flags = collapse_flags(flags, elem[1:])
            else:
                flags = collapse_flags(flags, [line])
        return flags
    return set()


def collapse_flags(old: Iterable[str], new: Iterable[str]) -> Set[str]:
    """
    Collases an ordered list of flags into an unordered set of flags

    The resulting set will contain only the last variant of a flag (enabled or
    disabled) present in the lists.
    """
    newset = set(old)
    for flag in new:
        if not flag.startswith("-"):
            newset.discard(f"-{flag}")
        elif flag.startswith("-"):
            newset.discard(flag.lstrip("-"))
        newset.add(flag)
    return newset


def add_flag(file: str, atom: Atom, flag: str):
    """
    Adds flag to the flag file

    args:
        file: Path of the file to be modified
        atom: Atom that the flag applies to. This function will only modify an existing
              atom/flag list if the atom exactly matches this atom, otherwise a new
              list will be added
        flag: Flag to be added, including the `-` prefix if the flag is to be
              disabled explicitly
    """
    if os.path.exists(file):
        flagfile = __read_flags(file)
    else:
        flagfile = []

    found = False
    for (index, line) in enumerate(flagfile):
        line = re.sub("#.*", "", line).strip()
        if not line:
            continue

        tokens = line.split()
        if tokens[0] == atom:
            if flag not in tokens:
                info(l10n("flag-add", flag=flag, atom=atom, file=file))
                flagfile[index] = "{} {}".format(line, flag)
            found = True
    if not found:
        info(l10n("flag-add", flag=flag, atom=atom, file=file))
        flagfile.append("{} {}".format(atom, flag))

    __write_flags(file, flagfile)


def remove_flag(file: str, atom: Atom, flag: str):
    """
    Removes flag from the flag file

    args:
        file: Path of the file to modify
        atom: Atom to match against. The flag will be disabled for all atoms in the
              file which satisfy this atom
        flag: Flag to remove from the file. The flag must match exactly, this will not
              also remove the disabled variant of a flag.
    """
    flagfile = __read_flags(file)

    for (index, line) in enumerate(flagfile):
        line = re.sub("#.*", "", line).strip()
        if not line:
            continue

        tokens = line.split()
        if atom_sat(Atom(tokens[0]), atom) and flag in tokens:
            info(l10n("flag-remove", flag=flag, atom=atom, file=file))
            tokens = list(filter(lambda a: a != flag, tokens))

            if len(tokens) > 1:
                flagfile[index] = " ".join(tokens)
            else:
                del flagfile[index]

    __write_flags(file, flagfile)


@system_cache
def __read_flags(file):
    if os.path.exists(file):
        with open(file, mode="r") as flagfile:
            return flagfile.read().splitlines()
    return []


def __write_flags(file, new_flagfile):
    with open(file, mode="w") as flagfile:
        for line in new_flagfile:
            print(line, file=flagfile)
    __read_flags.cache_clear()
