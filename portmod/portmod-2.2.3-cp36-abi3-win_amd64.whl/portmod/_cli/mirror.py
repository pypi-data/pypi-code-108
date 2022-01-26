# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
import traceback
from logging import error

from portmod.download import download_mod, mirrorable
from portmod.loader import load_all
from portmodlib.l10n import l10n


def add_mirror_parser(subparsers, parents):
    parser = subparsers.add_parser("mirror", help=l10n("mirror-help"), parents=parents)
    parser.add_argument(
        "mirror", metavar=l10n("directory-placeholder"), help=l10n("mirror-dir-help")
    )

    def mirror_main(args):
        if args.mirror:
            os.makedirs(args.mirror, exist_ok=True)
            for mod in load_all():
                if mirrorable(mod):
                    try:
                        for source in download_mod(mod, set(), matchall=True):
                            path = os.path.join(args.mirror, source.name)
                            if not os.path.exists(path):
                                print(l10n("copying-file", src=source.path, dest=path))
                                shutil.copy(source.path, path)
                    except Exception as e:
                        traceback.print_exc()
                        error(f"{e}")
        else:
            parser.print_help()

    parser.set_defaults(func=mirror_main)
