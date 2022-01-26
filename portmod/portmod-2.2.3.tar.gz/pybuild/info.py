# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Importing values from this module fills them with information about the
pybuild file from which they were imported
"""
# Note: This module should be removed from sys.modules prior to importing to ensure that
# the cached version is not used instead.

import os
from pathlib import Path
from typing import Optional

from portmodlib.atom import VAtom

CATEGORY: str
P: str
PF: str
PN: str
PV: str
PR: Optional[str]
PVR: str


def _set_info(filename):
    """Puts module information in the global scope so that it can be imported"""
    global P, PF, PN, PV, PR, PVR, CATEGORY
    if filename is not None:
        CATEGORY = Path(filename).resolve().parent.parent.name
        atom = VAtom(
            "{}/{}".format(CATEGORY, os.path.basename(filename)[: -len(".pybuild")])
        )

        P = atom.P
        PF = atom.PF
        PN = atom.PN
        PV = atom.PV
        PR = atom.PR
        PVR = atom.PV
        if atom.PR is not None:
            PVR += "-" + atom.PR
