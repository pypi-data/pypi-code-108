# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
from typing import Optional

from portmod.globals import env
from portmod.parsers.flags import add_flag, get_flags, remove_flag

from ..config import get_config
from ..pybuild import Pybuild


def add_keyword(atom, keyword):
    """Adds keyword for the given atom. Does not modify any existing keywords."""
    keyword_file = os.path.join(env.prefix().CONFIG_DIR, "package.accept_keywords")
    add_flag(keyword_file, atom, keyword)


def remove_keyword(atom, keyword):
    keyword_file = os.path.join(env.prefix().CONFIG_DIR, "package.accept_keywords")
    remove_flag(keyword_file, atom, keyword)


def get_keywords(atom):
    keyword_file = os.path.join(env.prefix().CONFIG_DIR, "package.accept_keywords")
    ACCEPT_KEYWORDS = set(get_config()["ACCEPT_KEYWORDS"])
    return get_flags(keyword_file, atom).union(ACCEPT_KEYWORDS)


def accepts_stable(arch, keywords):
    return (
        # Package is always visible
        "**" in keywords
        # Package is visible if any architecture is stable
        or (
            "*" in keywords
            and any(x not in ("~*", "*") and x[0] not in ("-", "~") for x in keywords)
        )
        # Package is explicitly keyworded as stable for this architecture
        or any([keyword == arch for keyword in keywords])
    )


def accepts_testing(arch, keywords):
    return (
        accepts_stable(arch, keywords)
        # Package is explicitly keyworded as testing for this architecture
        or any(keyword == f"~{arch}" for keyword in keywords)
        # Package is visible if any architecture is testing
        or (
            "~*" in keywords
            and any(x not in ("~*", "*") and x[0] != "-" for x in keywords)
        )
    )


def accepts(accept_keywords, keywords):
    for keyword in accept_keywords:
        if keyword == "*":
            # Accepts stable on all architectures. Valid if keywords contains a stable
            # keyword for any keyword
            if any(keyword[0] not in ("~", "*", "-") for keyword in keywords):
                return True
        elif keyword == "~*":
            # Accepts testing on all architectures. Valid if keywords contains either
            # testing or stable for any keyword
            if any(not keyword.startswith("*") for keyword in keywords):
                return True
        elif keyword == "**":
            # Accepts any configuration
            return True
        elif keyword.startswith("~"):
            # Accepts testing on this architecture. Valid if keywords contains either
            # testing or stable for this keyword
            if accepts_testing(keyword[1:], keywords):
                return True
        else:  # regular keyword
            if accepts_stable(keyword, keywords):
                return True

    return "**" in keywords


def get_unstable_flag(mod: Pybuild) -> Optional[str]:
    """Returns the keyword for the user's current configuration of the given mod"""
    keywords = get_keywords(mod.ATOM)
    arch = env.prefix().ARCH
    if accepts(keywords, mod.KEYWORDS):
        return None

    if accepts_testing(arch, mod.KEYWORDS) or accepts_testing(arch, keywords):
        return "~"

    return "*"
