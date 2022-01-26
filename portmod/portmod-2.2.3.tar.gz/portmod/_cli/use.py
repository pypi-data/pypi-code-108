# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import logging
import sys
import traceback
from logging import error
from typing import Optional

from portmod.config.use import InvalidFlag, add_use, remove_use
from portmod.lock import exclusive_lock
from portmodlib.atom import Atom
from portmodlib.l10n import l10n


def add_use_parser(subparsers, parents):
    """
    Main function for the omwuse executable
    """

    parser = subparsers.add_parser("use", help=l10n("use-help"), parents=parents)
    parser.add_argument("-E", metavar=l10n("flag-placeholder"), help=l10n("use-enable"))
    parser.add_argument(
        "-D", metavar=l10n("flag-placeholder"), help=l10n("use-disable")
    )
    parser.add_argument("-R", metavar=l10n("flag-placeholder"), help=l10n("use-remove"))
    parser.add_argument(
        "-p", metavar=l10n("atom-placeholder"), help=l10n("use-package")
    )

    @exclusive_lock()
    def use_main(args):
        if not args.E and not args.D and not args.R and not args.p:
            parser.print_help()
            sys.exit(2)
        try:
            atom: Optional[Atom]
            if args.p is not None:
                atom = Atom(args.p)
            else:
                atom = None

            if args.E or args.D:
                if args.E:
                    add_use(args.E, atom)
                elif args.D:
                    add_use(args.D, atom, disable=True)

            if args.R:
                remove_use(args.R, atom)
        except InvalidFlag as e:
            if logging.root.level <= logging.DEBUG:
                traceback.print_exc()
            error(f"{e}")
        except Exception as e:
            traceback.print_exc()
            error(f"{e}")

    parser.set_defaults(func=use_main)
