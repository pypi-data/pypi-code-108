# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Displays filesystem conflicts between mods
"""

from portmodlib.l10n import l10n
from portmodlib.portmod import file_conflicts
from portmodlib.vfs import get_vfs_dirs


def add_conflicts_parser(subparsers, parents):
    """
    Main executable for openmw-conflicts executable
    """
    conflicts_parser = subparsers.add_parser(
        "conflict-ui", help=l10n("conflict-ui-help"), parents=parents
    )

    def conflicts_main(args):
        mod_dirs = get_vfs_dirs()

        file_conflicts(mod_dirs, ["txt", "md"])

    conflicts_parser.set_defaults(func=conflicts_main)
