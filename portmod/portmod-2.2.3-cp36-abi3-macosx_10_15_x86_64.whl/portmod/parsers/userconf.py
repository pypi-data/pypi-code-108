# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module for interacting with game configuration files as defined by
Config objects in the profile
"""

import csv
import os
from logging import warning
from typing import Dict, Set

from portmodlib.l10n import l10n


def read_userconfig(path: str) -> Dict[str, Set[str]]:
    """
    Parses csv-based user sorting rules

    args:
        path: Path of the file to be parsed
    returns:
        A dictionary mapping high-priority strings to strings they should override
    """
    userconfig = {}

    if os.path.exists(path):
        # Read user config
        with open(path, newline="") as csvfile:
            csvreader = csv.reader(csvfile, skipinitialspace=True)
            for row in csvreader:
                if row:
                    if len(row) == 1:
                        warning(l10n("user-config-warning", path=path, line=row[0]))
                    else:
                        atom = row[0].strip()
                        if atom not in userconfig:
                            userconfig[atom] = set(map(lambda x: x.strip(), row[1:]))
                        else:
                            userconfig[atom] |= set(map(lambda x: x.strip(), row[1:]))

    return userconfig
