# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

# pylint: disable=no-member

"""
Helper functions for interacting with the Windows registry
"""

import os
import sys
from typing import Any, Dict, Optional, Union


def read_reg(
    key: str, subkey: str, entry: Optional[str] = None
) -> Union[Any, Dict[str, Any]]:
    """
    Reads the given registry key/subkey

    args:
        key: Registry key to read from
        subkey: Registry subkey to read from
        entry: Optional name in the dictionary stored at the given key/subkey
               to use.
    returns:
        Key data, type is usually a string. If the key contains subkeys and the entry
        is not provided, returns a dictionary mapping subkey names to their values
    """
    if sys.platform == "win32":
        import winreg  # pylint: disable=import-error

        with winreg.ConnectRegistry(None, key) as reg:
            try:
                rawkey = winreg.OpenKey(
                    reg, subkey, access=winreg.KEY_READ | winreg.KEY_WOW64_64KEY
                )
            except FileNotFoundError:
                try:
                    rawkey = winreg.OpenKey(
                        reg, subkey, access=winreg.KEY_READ | winreg.KEY_WOW64_32KEY
                    )
                except FileNotFoundError:
                    return None

            if entry is None:
                subkeys = {}
                i = 0
                try:
                    while True:
                        subsubkey = winreg.EnumKey(rawkey, i)
                        subkeys[subsubkey] = read_reg(
                            key, subkey + os.sep + subsubkey, entry
                        )
                        i += 1
                except WindowsError:  # pylint: disable=undefined-variable
                    if subkeys:
                        return subkeys
            try:
                i = 0
                while True:
                    name, value, _ = winreg.EnumValue(rawkey, i)
                    if entry is None:
                        return value
                    if name == entry:
                        return value
                    i += 1
            except WindowsError:  # pylint: disable=undefined-variable
                return None
    else:
        raise Exception("read_reg should not be called on platforms other than win32!")
