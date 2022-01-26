# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import re
from typing import Set

from .portmod import get_masters as native_get_masters


def get_masters(file: str) -> Set[str]:
    """
    Detects masters for the given file

    args:
        file: File to be examined
    returns:
        A set of all the master names
    """
    _, ext = os.path.splitext(file)
    if re.match(r"\.(esp|esm|omwaddon|omwgame)", ext, re.IGNORECASE):
        return set(native_get_masters(file))
    return set()
