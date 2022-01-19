###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

from os.path import join, splitext

import pytest

import LbAPCommon


@pytest.mark.timeout(100)
def test_parse_example1():
    with open(join(splitext(__file__)[0], "example1.yaml"), "rt") as fp:
        data = fp.read()
    jobs_data, checks_data = LbAPCommon.parse_yaml(data)
    assert len(jobs_data) == 168
