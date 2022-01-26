# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Helper functions for interacting with the Windows registry

Also provides the following constants from the ``winreg`` builtin module::

    HKEY_CLASSES_ROOT: int
    HKEY_CURRENT_CONFIG: int
    HKEY_CURRENT_USER: int
    HKEY_LOCAL_MACHINE: int
    HKEY_USERS: int
"""

import sys

from portmodlib.winreg import read_reg

if sys.platform == "win32":
    from winreg import (  # noqa  # pylint: disable=unused-import,import-error,no-name-in-module
        HKEY_CLASSES_ROOT,
        HKEY_CURRENT_CONFIG,
        HKEY_CURRENT_USER,
        HKEY_LOCAL_MACHINE,
        HKEY_USERS,
    )

__all__ = [
    "read_reg",
]
