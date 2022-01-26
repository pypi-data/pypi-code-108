# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3
"""
Module that interacts with the various portmod config files

Files are stored both in the portmod local directory and in the profile directory tree,
with the user's config file overriding and extending defaults set by the profile
"""

import os
import sys
import warnings
from typing import Any, Dict, Optional

from portmod.config.profiles import profile_exists, profile_parents
from portmod.functools import prefix_aware_cache
from portmod.globals import env
from portmod.win32 import get_personal

from .pyconf import (
    __COLLAPSE_KEYS,
    __OVERRIDE_KEYS,
    _create_config_placeholder,
    read_config,
)


def get_config_value(key: str, default: Optional[Any] = None):
    """
    Parses the user's configuration, overriding defaults from their profile

    returns:
        The config value matching key, or default if it was not specified
    """
    return get_config().get(key, default)


@prefix_aware_cache
def get_config() -> Dict[str, Any]:
    """
    Parses the user's configuration, overriding defaults from their profile
    """
    total_config: Dict[str, Any] = {
        # Default cannot be set in profile due to the value depending on platform
        "PLATFORM": sys.platform,
    }

    for attr in os.environ:
        total_config[attr] = os.environ[attr]

    if env.PREFIX_NAME is not None:
        total_config["ARCH"] = env.prefix().ARCH
        total_config["ROOT"] = env.prefix().ROOT

    if sys.platform == "win32":
        total_config["PERSONAL"] = get_personal()

    if profile_exists():
        for parent in profile_parents():
            path = os.path.join(parent, "defaults.conf")
            if os.path.exists(path):
                total_config = read_config(path, total_config)

    if os.path.exists(env.GLOBAL_PORTMOD_CONFIG):
        total_config = read_config(env.GLOBAL_PORTMOD_CONFIG, total_config, user=True)

    if env.PREFIX_NAME:
        if os.path.exists(env.prefix().CONFIG):
            total_config = read_config(env.prefix().CONFIG, total_config, user=True)
        else:
            _create_config_placeholder()

    # Set defaults and add to os.environ (for use in portmodlib)
    for key in __OVERRIDE_KEYS:
        if not total_config.get(key):
            total_config[key] = ""
        elif isinstance(total_config[key], (str, bool)) and total_config[key]:
            os.environ[key] = str(total_config[key])

    for key in __COLLAPSE_KEYS:
        if not total_config.get(key):
            total_config[key] = set()
        elif isinstance(total_config[key], (str, bool)) and total_config[key]:
            os.environ[key] = str(total_config[key])

    for key in ["TMPDIR", "TEMP", "TMP"]:
        if total_config.get(key):
            os.environ[key] = total_config[key]

    return total_config


def config_to_string(config: Dict) -> str:
    """Prints the given dictionary config as a string"""
    lines = []
    for key in sorted(config):
        if isinstance(config[key], (list, set)):
            lines.append("{} = {}".format(key, " ".join(sorted(config[key]))))
        else:
            lines.append("{} = {}".format(key, config[key]))
    return "\n".join(lines)


def set_config_value(key: str, value: str, path: Optional[str] = None) -> Optional[str]:
    """
    Sets the given key-value pair in portmod.conf

    The previous value is returned, if any
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        from redbaron import RedBaron
        from redbaron.nodes import AssignmentNode, NameNode

    if not path:
        path = env.prefix().CONFIG

    old = None
    with open(path, "r") as file:
        node = RedBaron(file.read())

        string = '"' + value + '"'

        for elem in node:
            if (
                isinstance(elem, AssignmentNode)
                and isinstance(elem.target, NameNode)
                and elem.target.value == key
            ):
                old = elem.value
                elem.value = string

        if not old:
            node.append(f"{key} = {string}")

        with open(path, "w") as file:
            file.write(node.dumps())

    get_config.cache_clear()
    return old
