# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
from logging import info, warning

from portmod.config.sets import get_set
from portmod.globals import env
from portmod.loader import load_installed_pkg
from portmod.package import remove_pkg
from portmod.prefix import remove_prefix
from portmod.prompt import display_num_list, prompt_bool, prompt_num_multi
from portmodlib.fs import get_tree_size
from portmodlib.l10n import l10n


def destroy(args):
    assert env.PREFIX_NAME
    to_remove = []

    if args.remove_config and os.path.lexists(env.prefix().CONFIG_DIR):
        to_remove.append(env.prefix().CONFIG_DIR)

    if env.INTERACTIVE:
        if to_remove:
            print(l10n("destroy-directories"))
            display_num_list(
                to_remove,
                [l10n("size", size=get_tree_size(d) / 1024 ** 2) for d in to_remove],
            )
            try:
                skip = prompt_num_multi(
                    l10n("destroy-exclude-prompt"),
                    len(to_remove),
                    cancel=True,
                )
            except EOFError:
                return

            for index in skip:
                del to_remove[index]
        else:
            print(l10n("no-directories-to-remove"))

        if not args.preserve_root:
            print(l10n("destroy-preserve-original", path=env.prefix().ROOT))

        print()
        if not prompt_bool(l10n("destroy-prompt", prefix=env.PREFIX_NAME)):
            return

    for directory in to_remove:
        print(l10n("removing-directory", path=directory))
        shutil.rmtree(directory)

    if not args.preserve_root:
        # Remove files installed by portmod
        # This only occurs for prefixes which were installed into an existing directory
        for atom in get_set("installed"):
            pkg = load_installed_pkg(atom)
            if pkg:
                remove_pkg(pkg)
            else:
                # This should not occur
                warning(f"Unable to load installed package {atom} during destruction")
        info(l10n("removing-directory", path=os.path.join(env.prefix().ROOT, "var")))
        shutil.rmtree(os.path.join(env.prefix().ROOT, "var"))

    remove_prefix(env.PREFIX_NAME)


def add_destroy_parser(subparsers, parents):
    parser = subparsers.add_parser(
        "destroy", help=l10n("destroy-help"), parents=parents
    )
    parser.add_argument(
        "--preserve-root",
        help=l10n("destroy-preserve-root-help"),
        action="store_true",
    )
    parser.add_argument(
        "--remove-config",
        help=l10n("destroy-remove-config-help"),
        action="store_true",
    )
    parser.set_defaults(func=destroy)
