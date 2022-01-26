# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import sys
from logging import error
from subprocess import CalledProcessError

from portmod.execute import sandbox_execute
from portmod.globals import env
from portmod.perms import Permissions
from portmodlib.l10n import l10n


def run(args):
    try:
        sandbox_execute(
            args.command,
            Permissions(
                global_read=True, rw_paths=[env.prefix().ROOT], tmp=env.TMP_DIR
            ),
        )
    except CalledProcessError as e:
        if args.debug:
            error(str(e))
        sys.exit(1)


def add_run_parser(subparsers, parents):
    parser = subparsers.add_parser("run", help=l10n("run-help"), parents=parents)
    parser.add_argument(
        "command",
        nargs="+",
        metavar=l10n("command-placeholder"),
        help=l10n("run-command-help"),
    )
    parser.set_defaults(func=run)
