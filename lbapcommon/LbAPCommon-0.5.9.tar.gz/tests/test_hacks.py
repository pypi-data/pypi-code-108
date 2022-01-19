###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import pytest

import LbAPCommon


@pytest.mark.parametrize(
    "app_name,app_version,expected",
    [
        ("DaVinci", "v36r3p1", True),
        ("DaVinci", "v36r4p1", False),
        ("davinci", "v36r3p1", True),
        ("davinci", "v36r4p1", False),
        ("DAVINCI", "v36r3p1", True),
        ("DAVINCI", "v36r4p1", False),
        ("DaVinci", "v3", True),
        ("DaVinci", "v35r33", True),
        ("DaVinci", "v35r3p1111", True),
        ("DAVINCI", "v50", False),
        ("DAVINCI", "v50r4", False),
        ("DAVINCI", "v50r4p11", False),
        ("Castelo", "v3r0", False),
        ("Castelo", "not-a-version", False),
    ],
)
def test_project_uses_cmt(app_name, app_version, expected):
    assert LbAPCommon.hacks.project_uses_cmt(app_name, app_version) is expected
