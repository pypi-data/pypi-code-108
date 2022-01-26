# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3
"""Helper functions for getting win32-specific information"""

import sys


def get_personal() -> str:
    if sys.platform == "win32":
        import ctypes.wintypes

        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(
            None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf
        )
        return buf.value
    raise Exception("get_personal should not be called on platforms other than win32!")
