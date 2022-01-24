# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Control project versions."""

import logging
import sys
from typing import Optional

from versioning import get_release_controller

_log = logging.getLogger(__name__)
_controller = get_release_controller()


def bump(
    commit: bool = False,
    release: bool = False,
    # tag: bool = False,
    # tag_name: Optional[str] = None,
    message: Optional[str] = None,
    # sign: bool = False,
    build: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """Manage project versions.

    Parameters
    ----------
    commit: bool
        Commit release changes to project.
    message: str
        Notes included with the commit.
    release: bool
        Make this version a new release.
    build: str
        Build version from other systems the may help coordinate build
        artifacts.
    dry_run: bool
        Run the command without making changes.

    """
    # tag: bool
    #     Tag this version.
    # tag_name: str
    #     The tag name to use for this tag.
    #     default: version
    # sign: bool
    #     Sign commit with PKI signature.
    version = _controller.bump_version(
        commit=commit,
        release=release,
        # tag=tag,
        # tag_name=tag_name,
        message=message,
        # sign_tag=sign,
        build=build,
        dry_run=dry_run,
    )
    print(str(version), file=sys.stdout)


def view(release: bool = False, filepaths: bool = False) -> None:
    """Get the current version or settings of a project.

    Parameters
    ----------
    release: bool
        View the current release type
    filepaths: bool
        List the version filepaths

    """
    if release:
        print(_controller.release, file=sys.stdout)
    if filepaths:
        for x in _controller.config.templates:
            print(x['filepath'], file=sys.stdout)
    if not release and not filepaths:
        print(_controller.config.version, file=sys.stdout)
