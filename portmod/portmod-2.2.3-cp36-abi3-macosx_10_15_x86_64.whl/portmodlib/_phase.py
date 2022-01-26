# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
from typing import Dict, List, Optional, Set, cast

from .source import Source


class PhaseState:
    """
    Information passed to the phase functions for use during execution

    These fields match those of the same names listed and documented
    by :class:`~pybuild.Pybuild1`
    """

    A: List[Source]
    FILESDIR: str
    T: Optional[str]
    D: str
    USE: Set[str]
    WORKDIR: str
    ROOT: str
    UNFETCHED: List[Source]
    S: Optional[str]

    def __init__(self, build_dir: Optional[str] = None):
        if build_dir:
            self.T = os.path.join(build_dir, "temp")
        else:
            self.T = None

    @classmethod
    def from_json(cls, dictionary: Dict):
        new = PhaseState()
        for key, value in dictionary.items():
            setattr(new, key, value)
        if hasattr(new, "A"):
            new.A = [Source(**x) for x in cast(Dict, new.A)]
        if hasattr(new, "UNFETCHED"):
            new.UNFETCHED = [Source(**x) for x in cast(Dict, new.UNFETCHED)]
        return new
