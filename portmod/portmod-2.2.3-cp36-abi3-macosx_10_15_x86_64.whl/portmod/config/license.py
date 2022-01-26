# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Helper functions for interacting with package licenses
"""

from typing import List, Union

from portmod.config import get_config
from portmod.config.use import get_use
from portmod.functools import system_cache
from portmod.pybuild import Pybuild
from portmod.repo import get_repo
from portmod.repo.metadata import get_license_groups
from portmodlib.usestr import use_reduce


def _get_pkg_license_groups(pkg: Pybuild):
    if pkg.INSTALLED:
        return get_license_groups(get_repo(pkg.REPO).location)
    else:
        if not pkg.REPO_PATH:
            raise RuntimeError(
                "Checking license of a package with no repository! "
                "This should not happen!"
            )
        return get_license_groups(pkg.REPO_PATH)


def is_license_accepted(mod: Pybuild) -> bool:
    """
    Returns true if the mod's license(s) are accepted by the user's configuration

    For a license to be accepted, it must be both listed, either explicitly,
    part of a group, or with the * wildcard  and it must not be blacklisted
    by a license or license group prefixed by a '-'
    """
    license_groups = _get_pkg_license_groups(mod)

    ACCEPT_LICENSE = get_config()["ACCEPT_LICENSE"]

    def accepted(group: Union[str, List]) -> bool:
        if not group:
            return True

        if isinstance(group, str):
            allowed = False
            # Check if license is allowed by anything in ACCEPT_LICENSE
            for license in ACCEPT_LICENSE:
                if license.startswith("-") and (
                    license == group
                    or (license[1] == "@" and group in license_groups[license[2:]])
                ):
                    # not allowed if matched by this
                    return False
                if license == "*":
                    allowed = True
                if license.startswith("@") and group in license_groups[license[1:]]:
                    allowed = True
            return allowed
        if group[0] == "||":
            return any(accepted(license) for license in group)

        return all(accepted(license) for license in group)

    enabled, disabled = get_use(mod)
    return accepted(use_reduce(mod.LICENSE, enabled, disabled, opconvert=True))

    # TODO: implement package-specific license acceptance via package.license config file


@system_cache
def has_eula(package: Pybuild) -> bool:
    groups = _get_pkg_license_groups(package)

    # FIXME: This should be reworked.
    # For one thing, this doesn't currently handle || operators
    return any(
        license_name in groups.get("EULA", set())
        for license_name in use_reduce(
            package.LICENSE, get_use(package)[0], get_use(package)[1], flat=True
        )
    )
