# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""Interface for installing and removing packages"""

import argparse
import os
import sys
import traceback
from logging import error, info
from shutil import move, rmtree

from portmod._deps import DepError, PackageDoesNotExist
from portmod.download import get_filename
from portmod.globals import env
from portmod.loader import AmbiguousAtom, load_all
from portmod.lock import exclusive_lock
from portmod.merge import configure, deselect, global_updates
from portmod.news import display_unread_message
from portmodlib.atom import InvalidAtom
from portmodlib.fs import onerror
from portmodlib.l10n import l10n

from . import atom_metavar


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def filter_mods(mods):
    atoms = []
    os.makedirs(env.DOWNLOAD_DIR, exist_ok=True)

    for mod in mods:
        if os.path.isfile(mod):
            for atom in load_all():
                for source in atom.get_sources(matchall=True):
                    if source.check_file(mod):
                        move(mod, get_filename(source.name))
                        atoms.append(atom.ATOM)
        else:
            atoms.append(mod)

    return atoms


def add_merge_parser(subparsers, parents):
    parser = subparsers.add_parser(
        "merge", help=l10n("merge-help"), parents=parents, conflict_handler="resolve"
    )
    parser.add_argument(
        "packages",
        metavar=atom_metavar(archive=True, sets=True),
        help=l10n("package-help"),
        nargs="*",
    )
    parser.add_argument(
        "--ignore-default-opts",
        help=l10n("ignore-default-opts-help"),
        action="store_true",
    )
    parser.add_argument(
        "-c", "--depclean", help=l10n("depclean-help"), action="store_true"
    )
    parser.add_argument(
        "-x", "--auto-depclean", help=l10n("auto-depclean-help"), action="store_true"
    )
    parser.add_argument(
        "-C", "--unmerge", help=l10n("unmerge-help"), action="store_true"
    )
    parser.add_argument(
        "-1", "--oneshot", help=l10n("oneshot-help"), action="store_true"
    )
    parser.add_argument("-O", "--nodeps", help=l10n("nodeps-help"), action="store_true")
    parser.add_argument("-u", "--update", help=l10n("update-help"), action="store_true")
    parser.add_argument(
        "-n", "--noreplace", help=l10n("noreplace-help"), action="store_true"
    )
    parser.add_argument("-N", "--newuse", help=l10n("newuse-help"), action="store_true")
    parser.add_argument(
        "-e", "--emptytree", help=l10n("emptytree-help"), action="store_true"
    )
    parser.add_argument("-D", "--deep", help=l10n("deep-help"), action="store_true")
    parser.add_argument(
        "-w",
        "--select",
        type=str2bool,
        nargs="?",
        const=True,
        default=None,
        metavar=l10n("yes-or-no"),
        help=l10n("merge-select-help"),
    )
    parser.add_argument(
        "--deselect",
        type=str2bool,
        nargs="?",
        const=True,
        default=None,
        metavar=l10n("yes-or-no"),
        help=l10n("merge-deselect-help"),
    )
    parser.add_argument("--sort-vfs", help=l10n("sort-vfs-help"), action="store_true")
    parser.add_argument("--debug", help=l10n("merge-debug-help"), action="store_true")

    parser.set_defaults(func=merge_main)


@exclusive_lock()
def merge_main(args):
    atoms = filter_mods(args.packages)
    env.DEBUG = args.debug

    if args.nodeps and args.depclean:
        error(l10n("nodeps-depclean"))
        sys.exit(1)

    if atoms or args.depclean:
        # If deselect is supplied (is not None), only deselect if not removing.
        # If removing, remove normally, but deselect depending on supplied value.
        if args.deselect and not (args.unmerge or args.depclean):
            deselect(atoms, no_confirm=args.no_confirm)
        else:
            try:
                configure(
                    atoms,
                    delete=args.unmerge,
                    depclean=args.depclean,
                    no_confirm=args.no_confirm,
                    oneshot=args.oneshot,
                    verbose=args.verbose,
                    update=args.update or args.newuse or args.noreplace,
                    nodeps=args.nodeps,
                    deselect=args.deselect,
                    select=args.select,
                    auto_depclean=args.auto_depclean,
                    deep=args.deep,
                    emptytree=args.emptytree,
                )

                # Note: When execeptions occur, TMP_DIR should be preserved
                if not env.DEBUG and os.path.exists(env.TMP_DIR):
                    rmtree(env.TMP_DIR, onerror=onerror)
                    info(">>> " + l10n("cleaned-up", dir=env.TMP_DIR))
            except (InvalidAtom, PackageDoesNotExist, AmbiguousAtom, DepError) as e:
                if args.debug:
                    traceback.print_exc()
                error(f"{e}")
                sys.exit(1)

    if args.sort_vfs:
        global_updates()

    display_unread_message()
