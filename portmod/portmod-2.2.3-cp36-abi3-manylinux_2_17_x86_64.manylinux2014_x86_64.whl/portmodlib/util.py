# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import fnmatch
import os
import re
from typing import List, Pattern, Union


def pybuild_dumper(obj):
    # Serialize as best we can. Sets become lists and unknown objects are
    # just stringified
    if isinstance(obj, set):
        return list(obj)
    if hasattr(obj, "to_json"):
        return obj.to_json()
    return "{}".format(obj)


def fnmatch_list_to_re(patterns: List[str]) -> Pattern:
    def to_re(value: Union[str, Pattern]):
        """
        Converts fn-match string into a regular expression string

        Note that normpath may not work as expected with fn-match strings
        if forward-slashes are present inside bracketed ranges (e.g. [/../]).
        """
        if isinstance(value, Pattern):
            return value
        return fnmatch.translate(os.path.normpath(value))

    flags = 0
    if os.environ.get("CASE_INSENSITIVE_FILES", False):
        flags = re.IGNORECASE
    return re.compile("|".join(map(to_re, patterns)), flags=flags)
