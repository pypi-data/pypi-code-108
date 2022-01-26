# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
CLI to select various configuration options

Currently just profiles
"""

import os
from logging import info
from typing import List, Optional

from portmod.config import get_config, set_config_value
from portmod.config.profiles import get_profile_path, set_profile
from portmod.globals import env
from portmod.modules import add_parsers
from portmod.news import add_news_parsers
from portmod.prompt import display_num_list
from portmod.repo import RemoteRepo, has_repo
from portmod.repo.metadata import get_profiles
from portmod.repos import add_repo, get_remote_repos, get_repos
from portmod.sync import sync
from portmodlib.colour import bright, green, lblue
from portmodlib.l10n import l10n

from .error import InputException


def get_profile():
    linkpath = os.path.join(env.prefix().CONFIG_DIR, "profile")
    if os.path.exists(linkpath) and os.path.islink(linkpath):
        return os.readlink(linkpath).split("profiles")[-1].lstrip(os.path.sep)
    return None


def list_profiles(arch: str) -> List[str]:
    """
    Prints a list of profiles

    args:
        arch: The architecture to use to filter the profiles

    returns:
        The paths of each profile, in the order they were displayed
    """
    start = 0
    try:
        profile_path: Optional[str] = get_profile_path()
    except FileNotFoundError:
        profile_path = None
    for repo, profiles in get_profiles(arch, env.prefix().REPOS).items():
        print(bright(green(l10n("profile-available", repo=repo))))
        display_num_list(
            [profile for _, profile, _ in profiles],
            [stability for _, _, stability in profiles],
            {
                index + start
                for index, (path, _, _) in enumerate(profiles)
                if path == profile_path
            },
            start=start,
        )
        start += len(profiles)
    return [
        path
        for values in get_profiles(arch, env.prefix().REPOS).values()
        for path, _, _ in values
    ]


def list_repos(arch: str) -> List[RemoteRepo]:
    repos = get_remote_repos(arch).values()
    print(bright(green(l10n("repos-available"))))
    display_num_list(
        [bright(repo.name) + ": " + repo.description for repo in repos],
        [
            repo.quality + (" " + lblue(repo.sync_uri) if repo.sync_uri else "")
            for repo in repos
        ],
        {index for index, repo in enumerate(repos) if has_repo(repo.name)},
    )
    return list(repos)


def add_prefix_repo(repo: str):
    enabled_repos = get_config()["REPOS"]
    repo_name = get_repo_name(repo)

    if repo_name and repo_name not in enabled_repos:
        enabled_repos.add(repo_name)
        info(l10n("repo-adding", name=repo_name, conf=env.prefix().CONFIG))

    set_config_value("REPOS", " ".join(sorted(enabled_repos)))
    # Re-set prefix so that env.prefix().REPOS is updated
    env.set_prefix(env.PREFIX_NAME)


def get_repo_name(value: str) -> str:
    repos = list(get_remote_repos(env.prefix().ARCH).values())
    if value.isdigit():
        repo_name = repos[int(value)].name
    else:
        if any(repo.name == value for repo in repos):
            repo_name = value
        else:
            raise InputException(l10n("repo-does-not-exist", name=value))

    return repo_name


def add_profile_parsers(subparsers, parents):
    profile = subparsers.add_parser(
        "profile", help=l10n("profile-help"), parents=parents
    )
    profile_subparsers = profile.add_subparsers()
    profile_list = profile_subparsers.add_parser("list", help=l10n("profile-list-help"))
    profile_set = profile_subparsers.add_parser("set", help=l10n("profile-set-help"))
    profile_set.add_argument(
        "index", metavar=l10n("number-placeholder"), help=l10n("profile-number-help")
    )
    profile_show = profile_subparsers.add_parser("show", help=l10n("profile-show-help"))

    def list_func(_args):
        list_profiles(env.prefix().ARCH)

    def set_func(args):
        path, _, _ = [
            tup
            for value in get_profiles(env.prefix().ARCH, env.prefix().REPOS).values()
            for tup in value
        ][int(args.index)]
        set_profile(path)

    def show_func(_args):
        linkpath = os.path.join(env.prefix().CONFIG_DIR, "profile")
        print(bright(green(l10n("profile-current-symlink", path=linkpath))))
        print(
            "  "
            + bright(os.readlink(linkpath).split("profiles")[-1].lstrip(os.path.sep))
        )

    def profile_help(args):
        profile.print_help()

    profile.set_defaults(func=profile_help)
    profile_list.set_defaults(func=list_func)
    profile_set.set_defaults(func=set_func)
    profile_show.set_defaults(func=show_func)


def add_repo_parser(subparsers, parents):
    repo = subparsers.add_parser("repo", help=l10n("repo-help"), parents=parents)
    repo_subparsers = repo.add_subparsers()
    repo_list = repo_subparsers.add_parser("list", help=l10n("repo-list-help"))
    repo_add = repo_subparsers.add_parser("add", help=l10n("repo-add-help"))
    repo_add.add_argument(
        "repo", metavar=l10n("repo-placeholder"), help=l10n("repo-identifier-help")
    )
    repo_remove = repo_subparsers.add_parser("remove", help=l10n("repo-remove-help"))
    repo_remove.add_argument(
        "repo", metavar=l10n("repo-placeholder"), help=l10n("repo-identifier-help")
    )

    def list_func(_args):
        list_repos(env.prefix().ARCH)

    def add_func(args):
        add_prefix_repo(args.repo)
        repo = get_remote_repos(env.prefix().ARCH)[args.repo]
        result = add_repo(repo)
        if result:
            sync([result])
        env.REPOS = get_repos()

    def remove_func(args):
        enabled_repos = get_config()["REPOS"]
        repo_name = get_repo_name(args.repo)

        if repo_name and repo_name in enabled_repos:
            enabled_repos.remove(repo_name)
            info(l10n("repo-removing", name=repo_name, conf=env.prefix().CONFIG))

        set_config_value("REPOS", " ".join(sorted(enabled_repos)))

    def repo_help(args):
        repo.print_help()

    repo.set_defaults(func=repo_help)
    repo_list.set_defaults(func=list_func)
    repo_add.set_defaults(func=add_func)
    repo_remove.set_defaults(func=remove_func)


def add_select_parser(subparsers, parents):
    """
    Adds the select subparser to the given subparsers
    """
    parser = subparsers.add_parser("select", help=l10n("select-help"), parents=parents)
    _subparsers = parser.add_subparsers()
    add_profile_parsers(_subparsers, parents)
    add_news_parsers(_subparsers, parents)
    add_repo_parser(_subparsers, parents)
    add_parsers(_subparsers, parents)
    parser.set_defaults(func=lambda args: parser.print_help())
