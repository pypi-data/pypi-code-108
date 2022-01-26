# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3
"""
Module that interacts with the python-based portmod.conf config file
"""

import os
import sys
from copy import deepcopy
from textwrap import fill
from typing import Any, Dict, Optional

from portmod.globals import env, get_version
from portmod.parsers.flags import collapse_flags
from portmodlib._loader import MINIMAL_GLOBALS, Policy
from portmodlib.l10n import l10n

__COLLAPSE_KEYS = {
    "USE",
    "ACCEPT_LICENSE",
    "ACCEPT_KEYWORDS",
    "INFO_VARS",
    "INFO_PACKAGES",
    "USE_EXPAND",
    "USE_EXPAND_HIDDEN",
    "PROFILE_ONLY_VARIABLES",
    "CACHE_FIELDS",
    "REPOS",
}
__OVERRIDE_KEYS = {
    "TEXTURE_SIZE",
    "PORTMOD_MIRRORS",
    "CASE_INSENSITIVE_FILES",
    "EXEC_PATH",
    "OMWMERGE_DEFAULT_OPTS",
    "INSTALL_DEST",
    "DOC_DEST",
    "VFS",
}

__USER_ONLY_VARIABLES = {"TMP", "TMPDIR", "TEMP", "_SANDBOX_PERMISSIONS"}


def _comment_wrap(text: str) -> str:
    return "\n".join(
        [
            fill(paragraph, width=80, initial_indent="# ", subsequent_indent="# ")
            # Squelch text together as one paragraph, except for double linebreaks, which define
            # new paragraphs
            for paragraph in text.split("\n\n")
        ]
    )


def _create_config_placeholder():
    """
    Creates a placeholder config file to help the user initialize their
    config file for the first time
    """
    os.makedirs(env.prefix().CONFIG_DIR, exist_ok=True)
    version = get_version()
    with open(env.prefix().CONFIG, "w") as file:
        config_string = (
            # FIXME: Depending on how the wiki is localized, we may need to have wiki_page included in the localization
            # For now it is excluded so that it can be changed more easily across localizations
            _comment_wrap(
                l10n(
                    "config-placeholder-header",
                    version=version,
                    info_command=f"`portmod {env.PREFIX_NAME} info`",
                    wiki_page="https://gitlab.com/portmod/portmod/wikis/Portmod-Config",
                )
            )
            + "\n\n"
            + _comment_wrap(l10n("config-placeholder-global-use"))
            + '\n# USE=""\n\n'
            + _comment_wrap(l10n("config-placeholder-texture-size", default="min"))
            + '\n# TEXTURE_SIZE="min"\n\n'
            + _comment_wrap(l10n("config-placeholder-accept-keywords"))
            + '\n# ACCEPT_KEYWORDS="openmw"\n\n'
            + _comment_wrap(l10n("config-placeholder-accept-license"))
            + '\n# ACCEPT_LICENSE="* -EULA"\n\n'
            + _comment_wrap(l10n("config-placeholder-openmw-config"))
            + "\n\n"
            + _comment_wrap(l10n("config-placeholder-morrowind-path"))
        )
        print(config_string, file=file)


def read_config(path: str, old_config: Dict[str, Any], *, user: bool = False) -> Dict:
    """
    Reads a config file and converts the relevant fields into a dictionary
    """
    # Slow import
    from RestrictedPython import compile_restricted

    if user:
        # User-config should auto-detect encoding such that it matches the
        # user's editor
        encoding = None
    else:
        # Repository files should always be utf-8
        encoding = "utf-8"

    with open(path, "r", encoding=encoding) as file:
        config = file.read()

    if sys.platform == "win32":
        config = config.replace("\\", "\\\\")

    byte_code = compile_restricted(config, filename=path, mode="exec", policy=Policy)

    glob = deepcopy(MINIMAL_GLOBALS)
    glob["__builtins__"]["join"] = os.path.join
    new_config = old_config.copy()
    try:
        exec(byte_code, glob, new_config)
    except NameError as e:
        print(l10n("exec-error", error=e, file=path))
    except SyntaxError as e:
        print(l10n("exec-error", error=e, file=path))

    merged = old_config.copy()

    def line_of_key(key: str) -> Optional[int]:
        for index, line in enumerate(config.split("\n")):
            if key in line:
                return index
        return None

    def check_key(key):
        nonlocal new_config, old_config, merged
        if (
            user
            and key in merged.get("PROFILE_ONLY_VARIABLES", [])
            and new_config.get(key) is not None
            and new_config.get(key) != old_config.get(key)
        ):
            raise UserWarning(
                f"{path}:{line_of_key(key)}\n" + l10n("reserved-variable", key=key)
            )

        if (
            not user
            and key in __USER_ONLY_VARIABLES
            and new_config.get(key) is not None
            and new_config.get(key) != old_config.get(key)
        ):
            raise UserWarning(
                f"{path}:{line_of_key(key)}\n" + l10n("user-reserved-variable", key=key)
            )

    for key in __COLLAPSE_KEYS:
        check_key(key)

        if isinstance(new_config.get(key, ""), str):
            new_config[key] = set(new_config.get(key, "").split())
        merged[key] = collapse_flags(merged.get(key, set()), new_config.get(key, set()))

    for key in __OVERRIDE_KEYS:
        check_key(key)

        if key in new_config and new_config[key]:
            merged[key] = new_config.get(key)

    for key in old_config.keys() | new_config.keys():
        check_key(key)

        if key not in __COLLAPSE_KEYS | __OVERRIDE_KEYS:
            if key in new_config:
                merged[key] = new_config[key]
            else:
                merged[key] = old_config[key]

    return merged
