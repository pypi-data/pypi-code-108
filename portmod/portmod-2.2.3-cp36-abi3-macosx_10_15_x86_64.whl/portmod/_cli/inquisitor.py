# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Quality assurance for the mod repo
"""

import argparse
import glob
import os
import re
import sys
import traceback
from logging import debug, error
from typing import Callable

from portmod.globals import env
from portmod.loader import SandboxedError, load_file
from portmod.news import validate_news
from portmod.repo import Repo, get_repo_name, get_repo_root
from portmod.repo.loader import get_atom_from_path
from portmod.repo.metadata import (
    get_categories,
    get_use_flag_atom_aliases,
    license_exists,
)
from portmodlib.atom import Atom, InvalidAtom, UnqualifiedAtom
from portmodlib.l10n import l10n
from portmodlib.log import add_logging_arguments, init_logger
from portmodlib.parsers.list import read_list
from portmodlib.portmod import (
    parse_category_metadata,
    parse_groups,
    parse_yaml_dict,
    parse_yaml_dict_dict,
)

from .pybuild import pybuild_manifest, pybuild_validate


def scan_package_dir(path: str, err: Callable[[str], None]):
    cpn = os.path.join(os.path.basename(os.path.dirname(path)), os.path.basename(path))
    if Atom(os.path.basename(cpn)).PV is not None:
        err(f"Package name {cpn} must not end in a version")

    for file in glob.glob(os.path.join(path, "*.pybuild")):
        debug(f"Scanning {file}")
        dir_name = os.path.basename(path)
        file_name = Atom(os.path.splitext(os.path.basename(file))[0]).PN
        if dir_name != file_name:
            err(
                f"The package name in filename {file} should match its parent directory's name!"
            )

        try:
            pybuild_validate(file)
        except SandboxedError as e:
            err(f"{e}")
        except Exception as e:
            traceback.print_exc()
            err(f"{e}")


def scan_category_metadata(path: str, err: Callable[[str], None]):
    # Note: Package metadata is already validated as part of pybuild_validate
    try:
        parse_category_metadata(path)
    except Exception as e:
        traceback.print_exc()
        err("{}".format(e))


def scan_category(path: str, err: Callable[[str], None]):
    for directory in glob.glob(os.path.join(path, "*")):
        if os.path.isdir(directory) and any(
            file.lower().endswith(".pybuild") for file in os.listdir(directory)
        ):
            scan_package_dir(directory, err)
    metadata_path = os.path.join(path, "metadata.yaml")
    if os.path.exists(metadata_path):
        scan_category_metadata(metadata_path, err)


def scan_arch_list(repo_root: str, err: Callable[[str], None]):
    # Check profiles/arch.list
    path = os.path.join(repo_root, "profiles", "arch.list")
    if os.path.exists(path):
        archs = read_list(path)
        for arch in archs:
            if " " in arch:
                err(
                    f'arch.list: in entry "{arch}". '
                    "Architectures cannot contain spaces"
                )


def scan_categories(repo_root: str, err: Callable[[str], None]):
    # Check profiles/categories
    path = os.path.join(repo_root, "profiles", "categories")
    if os.path.exists(path):
        lines = read_list(path)
        for category in lines:
            if " " in category:
                err(
                    f'categories.list: in category "{category}". '
                    "Categories cannot contain spaces"
                )


def scan_groups(repo_root: str, err: Callable[[str], None]):
    # Check metadata/groups.yaml
    path = os.path.join(repo_root, "metadata", "groups.yaml")
    if os.path.exists(path):
        parse_groups(path)


def scan_license_groups(repo_root: str, err: Callable[[str], None]):
    # Check metadata/license_groups.yaml
    # All licenses should exist in licenses/LICENSE_NAME
    path = os.path.join(repo_root, "profiles", "license_groups.yaml")
    if os.path.exists(path):
        license_groups = parse_yaml_dict(path)
        for key, value in license_groups.items():
            if value is not None:
                for license in value.split():
                    if not license_exists(repo_root, license) and not (
                        license.startswith("@")
                    ):
                        err(
                            f'license_groups.yaml: License "{license}" in group {key} '
                            "does not exist in licenses directory"
                        )


def scan_repo_name(repo_root: str, err: Callable[[str], None]):
    # Check profiles/repo_name
    path = os.path.join(repo_root, "profiles", "repo_name")
    if os.path.exists(path):
        lines = read_list(path)
        if len(lines) == 0:
            err("repo_name: profiles/repo_name cannot be empty")
        elif len(lines) > 1:
            err(
                "repo_name: Extra lines detected. "
                "File must contain just the repo name."
            )
        elif " " in lines[0]:
            err("repo_name: Repo name must not contain spaces.")


def scan_use(repo_root: str, err: Callable[[str], None]):
    # Check profiles/use.yaml
    path = os.path.join(repo_root, "profiles", "use.yaml")
    if os.path.exists(path):
        flags = parse_yaml_dict(path)
        for desc in flags.values():
            if not isinstance(desc, str):
                err(f'use.yaml: Description "{desc}" is not a string')


def scan_profiles(repo_root: str, err: Callable[[str], None]):
    # Check profiles/profiles.yaml
    path = os.path.join(repo_root, "profiles", "profiles.yaml")
    archs_path = os.path.join(repo_root, "profiles", "arch.list")
    if os.path.exists(archs_path):
        archs = read_list(archs_path)
    if os.path.exists(path):
        keywords = parse_yaml_dict_dict(path)
        for keyword, profiles in keywords.items():
            if keyword not in archs:
                err(
                    f"profiles.yaml: keyword {keyword} " "was not declared in arch.list"
                )
            for profile in profiles:
                if not isinstance(profile, str):
                    err('profiles.yaml: Profile "{profile}" is not a string')
                path = os.path.join(repo_root, "profiles", profile)
                if not os.path.exists(path):
                    err(f"profiles.yaml: Profile {path} does not exist")


def scan_use_expand(filename: str, err: Callable[[str], None]):
    entries = parse_yaml_dict(filename)
    for entry in dict(entries):
        if not re.match("[A-Za-z0-9][A-Za-z0-9+_-]*", entry):
            err(f"USE_EXPAND flag {entry} in {filename} contains invalid characters")


def scan_root(repo_root: str, err: Callable[[str], None]):
    # Run pybuild validate on every pybuild in repo
    for category in get_categories(repo_root):
        scan_category(os.path.join(repo_root, category), err)

    # Check files in metadata and profiles.
    # These may not exist, as they might be inherited from another repo instead
    scan_arch_list(repo_root, err)
    scan_categories(repo_root, err)
    scan_groups(repo_root, err)
    scan_license_groups(repo_root, err)
    scan_repo_name(repo_root, err)
    scan_use(repo_root, err)
    scan_profiles(repo_root, err)
    for filename in glob.glob(os.path.join(repo_root, "profiles", "desc", "*.yaml")):
        scan_use_expand(filename, err)
    # Check news
    validate_news(repo_root, err)
    scan_use_alias(repo_root, err)


def scan_use_alias(repo_root: str, err: Callable[[str], None]):
    # Check profiles/use.alias.yaml
    try:
        aliases = get_use_flag_atom_aliases(repo_root)
    except (RuntimeError, UnqualifiedAtom, InvalidAtom) as _e:
        err(str(_e))
    for flag, alias in aliases.items():
        # Check that alias is a valid package in the repository
        packages = glob.glob(
            os.path.join(repo_root, alias.C, alias.PN, alias.PN + "-*.pybuild")
        )
        if not packages:
            err(
                f"Use flag alias package {alias} for flag {flag} "
                f"does not exist in this repository"
            )

        # If alias has a use flag requirement, it must be a valid use flag for at least
        # one version of that package
        if alias.USE:
            if not any(
                alias.USE <= set(load_file(package).IUSE_EFFECTIVE)
                for package in packages
            ):
                err(
                    "No package has the required use flag dependencies "
                    f"for use flag {flag}'s alias {alias}"
                )


def scan_file(filename: str, repo_root: str, err: Callable[[str], None]):
    _, ext = os.path.splitext(filename)
    relative = os.path.normpath(os.path.relpath(filename, start=repo_root))
    if ext.lower() == ".pybuild":
        scan_package_dir(os.path.dirname(filename), err)
    else:
        news_dir = os.path.join("metadata", "news")
        if relative == os.path.join("profiles", "arch.list"):
            scan_arch_list(repo_root, err)
        elif relative == os.path.join("profiles", "categories"):
            scan_categories(repo_root, err)
        elif relative == os.path.join("metadata", "groups.yaml"):
            scan_groups(repo_root, err)
        elif relative == os.path.join("profiles", "license_groups.yaml"):
            scan_license_groups(repo_root, err)
        elif relative == os.path.join("profiles", "repo_name"):
            scan_repo_name(repo_root, err)
        elif relative == os.path.join("profiles", "use.yaml"):
            scan_use(repo_root, err)
        elif relative == os.path.join("profiles", "use.alias.yaml"):
            scan_use_alias(repo_root, err)
        elif os.path.dirname(relative) == os.path.join(
            "profiles", "desc"
        ) and relative.endswith(".yaml"):
            scan_use_expand(filename, err)
        elif os.path.commonprefix([relative, news_dir]) == news_dir:
            validate_news(repo_root, err)
        elif os.path.basename(filename) == "metadata.yaml":
            path, _ = os.path.split(relative)
            if os.path.split(path)[0] is None:
                scan_category_metadata(filename, err)
            else:
                scan_package_dir(os.path.dirname(filename), err)


def scan_commit(commit, err):
    import git

    _git = git.Git()

    files = _git.show(commit, name_only=True, oneline=True).splitlines()[1:]
    message = _git.log(commit, format="%B", n=1)
    header_line = message.splitlines()[0]
    packages_modified = [file for file in files if file.endswith(".pybuild")]
    if len(packages_modified) == 1:
        atom = get_atom_from_path(packages_modified[0]).CPN
        if not message.startswith(atom + ":"):
            err(f'Commit "{header_line}" should start with "{atom}: <short desc>"')


def commit_message(args, repo_root: str, err: Callable[[str], None]):
    import git

    gitrepo = git.Repo.init(repo_root)

    initial_message = None
    message = ""
    if args.initial_message:
        with open(args.initial_message) as file:
            initial_message = file.read()

    changes = gitrepo.head.commit.diff(git.Diffable.Index)

    pybuild_diffs = [diff for diff in changes if diff.b_path.endswith(".pybuild")]

    def check_initial_message(message, initial_message):
        return (
            initial_message
            and initial_message.strip() != message
            and not initial_message.startswith("fixup!")
        )

    if len(pybuild_diffs) == 1:
        diff = pybuild_diffs[0]

        if diff.a_path.endswith(".pybuild"):
            if diff.a_path:
                old = get_atom_from_path(diff.a_path)
            if diff.b_path:
                new = get_atom_from_path(diff.b_path)

            if diff.deleted_file:
                message = f"{old.CPN}: Removed version {old.PV}"
                if check_initial_message(message, initial_message):
                    message += f"\n\n{initial_message}"
            elif diff.new_file:
                message = f"{new.CPN}: Added version {new.PV}"
                if check_initial_message(message, initial_message):
                    message += f"\n\n{initial_message}"
            elif diff.renamed_file and old.PV != new.PV:
                message = f"{new.CPN}: Updated to version {new.PV}"
                if check_initial_message(message, initial_message):
                    message += f"\n\n{initial_message}"
            else:
                # Either a change to the package without bump, or just a revision bump.
                # We can't autogenerate a meaningful message
                if initial_message:
                    if initial_message.startswith(
                        new.CPN + ":"
                    ) or initial_message.startswith("fixup!"):
                        message = initial_message
                    else:
                        message = f"{new.CPN}: {initial_message}"
                else:
                    message = f"{new.CPN}: "

        if args.initial_message:
            with open(args.initial_message, "w") as file:
                file.write(message)
        else:
            print(message)


def scan(args, repo_root: str, err: Callable[[str], None]):
    if args.diff:
        import git

        for file in git.Git().diff(args.diff, name_only=True).splitlines():
            scan_file(os.path.join(repo_root, file), repo_root, err)

        for commit in git.Git().log("HEAD", "^" + args.diff, pretty="%H").splitlines():
            scan_commit(commit, err)

    else:
        for root in args.paths or [os.getcwd()]:
            if os.path.exists(os.path.join(root, "profiles", "repo_name")):
                scan_root(root, err)
            elif os.path.isdir(root):
                if glob.glob(os.path.join(root, "*", "*.pybuild")):
                    scan_category(root, err)
                elif glob.glob(os.path.join(root, "*.pybuild")):
                    scan_package_dir(root, err)
                else:
                    # Try to scan all files in directory tree
                    for path_root, _, filenames in os.walk(root):
                        for filename in filenames:
                            scan_file(os.path.join(path_root, filename), repo_root, err)
            elif os.path.isfile(root):
                scan_file(os.path.abspath(root), repo_root, err)


def manifest(args, _repo_root: str, err: Callable[[str], None]):
    def try_manifest(file: str):
        try:
            pybuild_manifest(file)
        except Exception as e:
            traceback.print_exc()
            err(f"{e}")

    for root in args.paths or [os.getcwd()]:
        if os.path.isdir(root):
            # Run pybuild manifest on every pybuild in repo
            for file in glob.iglob(
                os.path.join(root, "**", "*.pybuild"), recursive=True
            ):
                try_manifest(file)
        else:
            _, ext = os.path.splitext(root)
            if ext.lower() == ".pybuild":
                try_manifest(root)
            else:
                err(f"{root} is not a pybuild file!")


def main():
    """
    Main function for the inquisitor executable
    """

    common = argparse.ArgumentParser(add_help=False)
    add_logging_arguments(common)
    common.add_argument("--debug", help=l10n("merge-debug-help"), action="store_true")

    parser = argparse.ArgumentParser(
        description="Quality assurance program for the package repository",
        parents=[common],
    )
    subparsers = parser.add_subparsers()
    manifest_parser = subparsers.add_parser(
        "manifest", help="Produces Manifest files", parents=[common]
    )
    scan_parser = subparsers.add_parser(
        "scan", help="QA Checks package repositories", parents=[common]
    )
    commit_msg_parser = subparsers.add_parser(
        "commit-msg",
        help="Produces a commit message using the working directory. "
        "Designed to be used as a git commit-msg hook",
        parents=[common],
    )
    commit_msg_parser.add_argument(
        "initial_message",
        help="Path to a file containing a user-supplied message to start from",
        nargs="?",
    )
    commit_msg_parser.add_argument(
        "--paths",
        help="Location of the repository to process. "
        "If omitted, the current working directory will be used",
        nargs="?",
    )
    scan_parser.add_argument(
        "--diff",
        nargs="?",
        help="Scan files changed since the given git target (branch, commit, etc.)",
    )
    manifest_parser.add_argument(
        "paths",
        metavar="PATH",
        help="scope to process. If not provided defaults to the current working directory",
        nargs="*",
    )
    scan_parser.add_argument(
        "paths",
        metavar="PATH",
        help="scope to process. If not provided defaults to the current working directory",
        nargs="*",
    )

    scan_parser.set_defaults(func=scan)
    manifest_parser.set_defaults(func=manifest)
    commit_msg_parser.set_defaults(func=commit_message)

    args = parser.parse_args()
    init_logger(args)

    if hasattr(args, "paths") and args.paths:
        repo_root = get_repo_root(args.paths[0])
    else:
        repo_root = get_repo_root(os.getcwd())

    has_errored = False
    env.ALLOW_LOAD_ERROR = False

    def err(string: str):
        nonlocal has_errored
        error(string)
        has_errored = True

    if repo_root is None:
        err(
            "Cannot find repository for the current directory. "
            "Please run from within the repository you wish to inspect"
        )
        sys.exit(1)

    # Register repo in case it's not already in repos.cfg
    real_root = os.path.realpath(repo_root)
    if not any([real_root == os.path.realpath(repo.location) for repo in env.REPOS]):
        sys.path.insert(0, os.path.join(repo_root))
        env.REPOS.insert(0, Repo(get_repo_name(repo_root), repo_root))

    if args.debug:
        env.DEBUG = True

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)

    args.func(args, repo_root, err)

    if has_errored:
        sys.exit(1)
