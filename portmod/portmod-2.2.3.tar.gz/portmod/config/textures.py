# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import re
from typing import List, Optional

from . import get_config


def select_texture_size(texture_sizes: List[int]) -> Optional[int]:
    """
    Chooses the appropriate texture size using user settings

    args:
        texture_sizes: List of possible texture sizes to choose from

    returns:
        texture size number chosen from the texture_sizes list
    """
    TEXTURE_SIZE = get_config()["TEXTURE_SIZE"]
    expr = re.compile(r"(?P<OP>(min|max))( (?P<G>(>=|<=)) (?P<NUM>[0-9]+))?")
    match = expr.match(TEXTURE_SIZE)
    if not texture_sizes:
        return None

    assert match
    operator = match.group("OP")
    comparison = match.group("G")
    value = match.group("NUM")

    if operator and comparison and value:
        if comparison == ">=":
            filtered = [x for x in texture_sizes if x >= int(value)]
        else:
            filtered = [x for x in texture_sizes if x <= int(value)]

        if len(filtered) > 0:
            if operator == "min":
                return min(filtered)
            else:
                return max(filtered)
        else:
            # Rule tried to filter based on size, but no size fell within interval.
            # Choose a texture based on the >= or <=
            if operator == "min" and comparison == ">=":
                return max(texture_sizes)
            elif operator == "max" and comparison == "<=":
                return min(texture_sizes)
            # For the remaining two, user either set min <= (<= is redundant)
            elif operator == "min":
                return min(texture_sizes)
            # or max >= (>= is redundant)
            else:
                return max(texture_sizes)

    elif operator and comparison is None and value is None:
        if match.group("OP") == "min":
            return min(texture_sizes)
        else:
            return max(texture_sizes)
    else:
        raise Exception('Invalid TEXTURE_SIZE config: "{}"'.format(TEXTURE_SIZE))
