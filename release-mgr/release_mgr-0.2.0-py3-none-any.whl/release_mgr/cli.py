#!/usr/bin/env python3

import os
import sys
from copy import deepcopy

import click

from release_mgr.git import get_commit_for_tag, get_repo, git
from release_mgr.github import create_release
from release_mgr.release import release_notes_for_version
from release_mgr.version import Version
from release_mgr.version_files import update_version_files


@click.command()
@click.option(
    "--version",
    "-v",
    type=str,
    default="",
    help="Specify the version to go to",
)
@click.option(
    "--pre-release",
    "-l",
    is_flag=True,
    help="Indicates this is a pre-release",
)
@click.option(
    "--draft",
    "-d",
    is_flag=True,
    help="Indicates this is a draft release",
)
@click.option(
    "--repo",
    "-r",
    type=str,
    default=None,
    help="The repository to create the release on in :owner/:repo format, "
    "will attempt to parse from git remotes if not given",
)
@click.option(
    "--title",
    "-t",
    is_flag=True,
    help="If given use the release name as the markdown title, otherwise title "
    "is omitted for Github style formatting",
)
@click.option(
    "--minor",
    "-m",
    is_flag=True,
    help="Bump minor version",
)
@click.option(
    "--major",
    "-j",
    is_flag=True,
    help="Bump major version",
)
@click.option(
    "--patch",
    "-p",
    is_flag=True,
    help="Bump patch version",
)
@click.option(
    "--skip-version-files",
    "-s",
    is_flag=True,
    help="Don't try to update version metadata files (package.json, setup.py etc.)",
)
@click.option(
    "--skip-upload",
    is_flag=True,
    help="Don't try to create a release on github and don't push the commits",
)
def main(
    version,
    major,
    patch,
    minor,
    skip_version_files,
    pre_release,
    draft,
    repo,
    title,
    skip_upload,
):
    """
    A simple tool for managing software releases on GitHub.
    """
    if not any((patch, minor, major, version)):
        print("Must provide one of --version, --major, --minor, or --patch.")
        sys.exit(1)

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("$GITHUB_TOKEN must be set.")
        sys.exit(1)

    last_version_commit, last_version = Version.latest_version()
    if version:
        version = Version.from_str(version)
    else:
        version = deepcopy(last_version)
        if patch:
            version.increment_patch()
        if minor:
            version.increment_minor()
        if major:
            version.increment_major()

    version_commit = get_commit_for_tag("HEAD")
    release_notes = release_notes_for_version(
        version,
        version_commit,
        last_version_commit,
    )

    if title:
        release_notes = f"# {version}\n\n{release_notes}"

    repo = repo or get_repo()

    print("Creating release", version, version_commit)
    print("Previous version", last_version, last_version_commit)
    print("Pre-release?", pre_release)
    print("Draft release?", draft)
    print("Repository", repo)
    print("============= Release Notes ============")
    print(release_notes)

    ans = input("Does this look correct? (y/N) ")
    if not ans.startswith("y"):
        return

    if not skip_version_files:
        update_version_files(version)

    git("tag", str(version))
    if not skip_upload:
        git("push", "--tags")

    try:
        if not skip_upload:
            create_release(
                token=token,
                repo=repo,
                tag_name=str(version),
                name=str(version),
                body=release_notes,
                draft=draft,
                prerelease=pre_release,
            )
    except Exception as exc:
        print("Failed to create release!")
        print(exc)


if __name__ == "__main__":
    main()
