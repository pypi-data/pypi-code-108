# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module containing shared CLI code
"""

from portmodlib.l10n import l10n


def atom_metavar(
    *, atom: bool = True, archive: bool = False, sets: bool = False
) -> str:
    strings = []
    if atom:
        strings.append(l10n("atom-placeholder"))
    if archive:
        strings.append(l10n("archive-placeholder"))
    if sets:
        strings.append("@" + l10n("set-placeholder"))

    return " | ".join(strings)
