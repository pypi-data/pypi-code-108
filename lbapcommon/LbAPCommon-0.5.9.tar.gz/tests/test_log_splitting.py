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

from os.path import dirname, join

import pytest


def test_spit_by_level_simple_WARNING():
    from LbAPCommon.validators.logs import _spit_by_level

    result = _spit_by_level(
        "2020-06-17 06:49:21 UTC Dsp2KmKppip.LoK...WARNING "
        "LoKi::LifetimeFitter:: Error from LoKi::Fitters::ctau_step,reset StatusCode=407"
    )
    assert dict(result) == {
        "WARNING": [
            (
                1,
                None,
                "2020-06-17 06:49:21 UTC",
                "Dsp2KmKppip.LoK...",
                "LoKi::LifetimeFitter:: Error from LoKi::Fitters::ctau_step,reset StatusCode=407",
            )
        ]
    }


def test_spit_by_level_simple_INFO():
    from LbAPCommon.validators.logs import _spit_by_level

    result = _spit_by_level(
        "2020-06-17 08:04:34 UTC L0MuonFromRaw        INFO "
        "L0MuonProcCand Q4     -> nb of banks seen     : 83033"
    )
    assert dict(result) == {
        "INFO": [
            (
                1,
                None,
                "2020-06-17 08:04:34 UTC",
                "L0MuonFromRaw",
                "L0MuonProcCand Q4     -> nb of banks seen     : 83033",
            )
        ]
    }


def test_spit_by_level_simple_SUCCESS():
    from LbAPCommon.validators.logs import _spit_by_level

    result = _spit_by_level(
        "2020-06-17 07:47:04 UTC EventSelector     SUCCESS "
        "Reading Event record 930001. Record number within stream 8: 18066"
    )
    assert dict(result) == {
        "SUCCESS": [
            (
                1,
                None,
                "2020-06-17 07:47:04 UTC",
                "EventSelector",
                "Reading Event record 930001. Record number within stream 8: 18066",
            )
        ]
    }


@pytest.mark.parametrize(
    "log_fn,expected_counts",
    [
        ("error-failed-to-read-file.log", (0, 0, 684, 2, 4, 0, 0, 382)),
        ("error-illegal-instruction.log", (0, 0, 8, 0, 0, 0, 0, 0)),
        ("error-missing-shared-library.log", (0, 0, 0, 0, 0, 0, 0, 0)),
        ("error-platform-unsupported.log", (0, 0, 0, 0, 0, 0, 0, 0)),
        ("good-DaVinci_00110296_00000038_1.log", (0, 0, 276, 3, 0, 0, 0, 345)),
        ("good-DaVinci_00110296_00000194_1.log", (0, 0, 306, 3, 0, 0, 0, 346)),
        ("good-Gauss_00104988_00000011_1.log", (0, 0, 3039, 63, 4, 0, 0, 401)),
    ],
)
def test_spit_by_level_full(log_fn, expected_counts):
    from LbAPCommon.validators.logs import _spit_by_level

    with open(join(dirname(__file__), "example-logs", log_fn), "rt") as fp:
        text = fp.read()
    result = _spit_by_level(text)

    levels = [
        "VERBOSE",
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "FATAL",
        "ALWAYS",
        "SUCCESS",
    ]
    counts = tuple(len(result[level]) for level in levels)
    print(counts)
    for level, expected in zip(levels, expected_counts):
        assert len(result[level]) == expected
