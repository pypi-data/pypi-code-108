# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3


import os
from logging import info

from portmod.config import get_config, set_config_value
from portmod.config.profiles import profile_exists, set_profile
from portmod.globals import env
from portmod.prefix import add_prefix
from portmod.prompt import prompt_bool, prompt_num, prompt_num_multi
from portmod.repo import get_repo
from portmod.repo.metadata import get_archs
from portmod.repos import add_repo
from portmod.sync import sync
from portmodlib.colour import bright
from portmodlib.l10n import l10n

from .select import add_prefix_repo, get_profile, list_profiles, list_repos


def init(args):
    """Initializes a prefix"""
    add_prefix(args.prefix, args.arch, args.directory)

    if env.INTERACTIVE:
        # If prefix previously existed and the configuration was preserved from when it
        # was removed, configuration could exist already.
        # If so, display configuration and prompt user to keep it or go through the
        # normal selection process
        if profile_exists():
            print(l10n("existing-configuration", prefix=args.prefix))
            enabled = " ".join(get_config()["REPOS"])
            print()
            print(f'    REPOS = "{enabled}"')
            print(f'    profile = "{get_profile()}"')
            print()
            if prompt_bool(l10n("existing-configuration-prompt")):
                return

            # Ensure that existing repositories get cleared so that only the new ones
            # will be included
            set_config_value("REPOS", "")

        info("")
        info(l10n("init-preamble"))
        info("")

        repos = list_repos(args.arch)
        if len(repos) == 1:
            info("")
            info(bright(l10n("init-single-repo", arch=args.arch, repo=repos[0].name)))
            info("")
            selected = [0]
        else:
            selected = prompt_num_multi(l10n("init-repositories-prompt"), len(repos))

        for index in selected:
            info(f"portmod {args.prefix} select repo add {repos[index].name}")
            add_prefix_repo(repos[index].name)
            add_repo(repos[index])

        # Re-initialize prefix with the new repositories
        env.set_prefix(args.prefix)

        if selected:
            info("portmod sync " + " ".join([repos[x].name for x in selected]))
            sync([get_repo(repos[x].name) for x in selected])

        print()
        profiles = list_profiles(args.arch)
        index = prompt_num(l10n("init-profile-prompt"), len(profiles))
        info(f"portmod {args.prefix} select profile set {index}")
        set_profile(profiles[index])

        info("")
        info(l10n("init-subcommands"))
        info(f"    portmod {args.prefix} select profile")
        info(f"    portmod {args.prefix} select repo")
    else:
        if not profile_exists():
            info(l10n("init-non-interactive-postamble"))
            info(f"    portmod {args.prefix} select profile")
            info(f"    portmod {args.prefix} select repo")


def add_init_parser(subparsers, parents):
    parser = subparsers.add_parser("init", help=l10n("init-help"), parents=parents)
    parser.add_argument(
        "prefix", metavar=l10n("prefix-placeholder"), help=l10n("init-prefix-help")
    )
    try:
        meta_repo = get_repo("meta")
        if not os.path.exists(meta_repo.location) and not env.TESTING:
            sync([meta_repo])
            if not env.REPOS:
                env.REPOS = [meta_repo]
        parser.add_argument(
            "arch",
            help=l10n("init-arch-help"),
            choices={arch for repo in env.REPOS for arch in get_archs(repo.location)},
        )
    except Exception:
        parser.add_argument("arch", help=l10n("init-arch-help"))

    parser.add_argument(
        "directory",
        metavar=l10n("directory-placeholder"),
        help=l10n(
            "init-directory-help",
            local=env.DATA_DIR.replace(os.path.expanduser("~"), "~"),
        ),
        nargs="?",
    )
    parser.set_defaults(func=init)
