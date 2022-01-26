# Copyright (C) 2021 FernOfSigma.

# This file is part of owoifier.

# owoifier is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# owoifier is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# owoifier. If not, see <https://www.gnu.org/licenses/>.

"""OwO what's this?"""

import random

from .constants import PREFIXES, SUFFIXES


MAPPINGS = [
    ["r", "w"],
    ["l", "w"],
    ["na", "nya"],
    ["ni", "nyi"],
    ["nu", "nyu"],
    ["ne", "nye"],
    ["no", "nyo"],
    ["ove", "uv"]
]

def _extend_mapping(attr: str) -> None:
    for old in MAPPINGS:
        new = [getattr(i, attr)() for i in old]
        if new not in MAPPINGS:
            MAPPINGS.append(new)

_extend_mapping("upper")
_extend_mapping("capitalize")

def owoify(text: str, prefix: bool=False, suffix: bool=False) -> str:
    """Translates English text to OwO.

    Parameters
    ----------
    text : str
        The string that needs to be translated.

    prefix : bool, default False
        Set whether to use a funny prefix. Disabled by default.

    suffix : bool, default False
        Set whether to use a funny suffix. Disabled by default.

    Returns
    -------
    str
        The twanswated stwing.
    """
    for src, dst in MAPPINGS:
        if src in text:
            text = text.replace(src, dst)

    if prefix is True:
        text = f"{random.choice(PREFIXES)} {text}"

    if suffix is True:
        text = f"{text} {random.choice(SUFFIXES)}"

    return text
