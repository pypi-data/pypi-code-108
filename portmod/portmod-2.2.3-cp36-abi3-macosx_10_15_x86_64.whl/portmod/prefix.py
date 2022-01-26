# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import configparser
import csv
import getpass
import os
import re
from logging import info, warning
from stat import S_IWRITE
from typing import Mapping, NamedTuple, Optional

from portmod.functools import system_cache
from portmodlib.fs import is_parent
from portmodlib.l10n import l10n

from .globals import env
from .repo.metadata import get_archs
from .repos import get_local_repos


class InvalidPrefix(RuntimeError):
    def __init__(self, prefix):
        self.prefix = prefix

    def __str__(self):
        return l10n("invalid-prefix", prefix=self.prefix)


class PrefixExistsError(RuntimeError):
    def __init__(self, prefix):
        self.prefix = prefix

    def __str__(self):
        return l10n("prefix-exists", prefix=self.prefix)


class Prefix(NamedTuple):
    arch: str
    path: Optional[str]


@system_cache
def get_prefixes() -> Mapping[str, Prefix]:
    """Returns a mapping of prefixes to their architectures"""
    prefixes = {}
    if os.path.exists(env.PREFIX_FILE):
        with open(env.PREFIX_FILE, "r", newline="") as file:
            # Ignore empty lines and comments
            lines = filter(
                bool, map(lambda x: re.sub("#.*", "", x).strip(), file.readlines())
            )
            csvdata = csv.reader(
                lines, delimiter=" ", dialect="unix", quoting=csv.QUOTE_MINIMAL
            )
            for row in csvdata:
                prefix = row[0]
                arch = row[1]
                directory = None
                if len(row) > 2:
                    directory = row[2]

                prefixes[prefix] = Prefix(arch, directory)

    return prefixes


def remove_prefix(prefix: str):
    """
    Removes a prefix the prefix file

    Does not modify the prefix's data
    """
    stat = os.stat(env.PREFIX_FILE)
    os.chmod(env.PREFIX_FILE, stat.st_mode | S_IWRITE, follow_symlinks=True)

    info(l10n("removing-prefix", prefix=prefix))
    with open(env.PREFIX_FILE) as file:
        lines = file.readlines()
        origlines = list(lines)
        for index, line in enumerate(lines):
            file_prefix, _, _ = line.partition(" ")
            if prefix == file_prefix:
                del lines[index]

    with open(env.PREFIX_FILE, "w") as file:
        if lines != origlines:
            file.writelines(lines)

    stat = os.stat(env.PREFIX_FILE)
    os.chmod(env.PREFIX_FILE, stat.st_mode - S_IWRITE, follow_symlinks=True)

    get_prefixes.cache_clear()


def add_prefix(prefix: str, arch: str, directory: Optional[str] = None):
    """
    Adds a new prefix

    args:
        prefix: Name of the prefix
        arch: Architecture of the prefix
        directory: Optional initial directory to store the prefix inside
                   If not included it will be stored with other portmod files
                   (~/.local/share/portmod on Linux)
                   Any files which are already in the directory will be backed up
                   if overwritten, and restored when the prefix is destroyed
    """

    invalid_prefixes = {"news", "sync", "mirror"}

    if prefix in invalid_prefixes:
        raise InvalidPrefix(prefix)

    if prefix in get_prefixes():
        raise PrefixExistsError(prefix)

    arch_options = set()
    for repo in get_local_repos().values():
        arch_options |= get_archs(repo.location)

    if arch not in arch_options:
        warning(l10n("unknown-arch", arch=arch))

    if directory:
        if not os.access(directory, os.W_OK):
            raise PermissionError(l10n("directory-not-writable", path=directory))

        existing_prefixes = get_prefixes()
        for name, existing_prefix in existing_prefixes.items():
            # directory cannot overlap with other prefixes
            existing_path = existing_prefix.path or os.path.join(env.DATA_DIR, name)
            if is_parent(directory, existing_path) or is_parent(
                existing_path, directory
            ):
                raise FileExistsError(
                    l10n(
                        "prefix-overlap",
                        newpath=directory,
                        oldpath=existing_path,
                        prefix=name,
                    )
                )

    # Add new prefix to the prefix file
    if os.path.exists(env.PREFIX_FILE):
        stat = os.stat(env.PREFIX_FILE)
        os.chmod(env.PREFIX_FILE, stat.st_mode | S_IWRITE, follow_symlinks=True)

    os.makedirs(os.path.dirname(env.PREFIX_FILE), exist_ok=True)

    with open(env.PREFIX_FILE, "a", newline="") as file:
        writer = csv.writer(
            file, delimiter=" ", dialect="unix", quoting=csv.QUOTE_MINIMAL
        )
        if directory is None:
            writer.writerow([prefix, arch])
        else:
            writer.writerow([prefix, arch, os.path.abspath(directory)])

    stat = os.stat(env.PREFIX_FILE)
    os.chmod(env.PREFIX_FILE, stat.st_mode - S_IWRITE, follow_symlinks=True)

    get_prefixes.cache_clear()

    env.set_prefix(prefix)

    # If the database already existed, it will not be recreated
    if os.path.exists(env.prefix().INSTALLED_DB):
        print(l10n("database-exists", path=env.prefix().INSTALLED_DB))
    else:
        import git

        # Initialize as git repo
        os.makedirs(env.prefix().INSTALLED_DB)

        gitrepo = git.Repo.init(env.prefix().INSTALLED_DB)
        # This repository is for local purposes only.
        # We don't want to worry about prompts for the user's gpg key password
        localconfig = gitrepo.config_writer()
        localconfig.set_value("commit", "gpgsign", False)
        USER = getpass.getuser()

        try:
            # May throw TypeError if GitPython<3.0.5
            globalconfig = git.config.GitConfigParser()
            globalconfig.get_value("user", "name")
            globalconfig.get_value("user", "email")
        except (TypeError, configparser.NoOptionError, configparser.NoSectionError):
            # Set the user name and email if they aren't in a global config
            localconfig.set_value("user", "name", f"{USER}")
            localconfig.set_value("user", "email", f"{USER}@example.com")

        localconfig.release()

    get_prefixes.cache_clear()
    info(l10n("initialized-prefix", prefix=prefix))
