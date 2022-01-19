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
import re
from pathlib import Path

import pytest

from LbAPCommon import checks

pytest.importorskip("XRootD")


def test_num_entries_passing():
    data_in = {
        "check": {
            "type": "num_entries",
            "count": 1000,
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert result.passed
    assert result.messages == ["Found 5135823 in DecayTree (1000 required)"]
    assert result.tree_data["DecayTree"]["num_entries"] == 5135823


def test_num_entries_passing_multiple_files():
    data_in = {
        "check": {
            "type": "num_entries",
            "count": 1000,
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root",
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetUp.root",
        ],
    )["check"]
    assert result.passed
    assert result.messages == ["Found 8556118 in DecayTree (1000 required)"]
    assert result.tree_data["DecayTree"]["num_entries"] == 8556118


def test_num_entries_failing():
    data_in = {
        "check": {
            "type": "num_entries",
            "count": 1000000000,
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == ["Found 5135823 in DecayTree (1000000000 required)"]
    assert result.tree_data["DecayTree"]["num_entries"] == 5135823


def test_num_entries_failing_tree_name():
    data_in = {
        "check": {
            "type": "num_entries",
            "count": 1000,
            "tree_pattern": "RandomName",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
    for _key, data in result.tree_data.items():
        assert data["histograms"] == []


def test_num_entries_per_invpb_passing():
    data_in = {
        "check": {
            "type": "num_entries_per_invpb",
            "count_per_invpb": 10000,
            "tree_pattern": "DecayTree",
            "lumi_pattern": "LumiTuple",
        }
    }
    file_list = [Path(__file__).parent.absolute() / "example_tuple_with_lumi.root"]
    result = checks.run_job_checks(
        ["check"],
        data_in,
        file_list,
    )["check"]
    assert result.passed
    assert result.messages == [
        "Found 23026.2 entries per unit luminosity (pb-1) in DecayTree (10000 required)"
    ]
    assert result.tree_data["DecayTree"]["num_entries_per_invpb"] == 23026.2


def test_num_entries_per_invpb_failing():
    data_in = {
        "check": {
            "type": "num_entries_per_invpb",
            "count_per_invpb": 10000000,
            "tree_pattern": "DecayTree",
            "lumi_pattern": "LumiTuple",
        }
    }
    file_list = [Path(__file__).parent.absolute() / "example_tuple_with_lumi.root"]
    result = checks.run_job_checks(
        ["check"],
        data_in,
        file_list,
    )["check"]
    assert not result.passed
    assert result.messages == [
        "Found 23026.2 entries per unit luminosity (pb-1) in DecayTree (10000000 required)"
    ]
    assert result.tree_data["DecayTree"]["num_entries_per_invpb"] == 23026.2


def test_num_entries_per_invpb_failing_MC():
    data_in = {
        "check": {
            "type": "num_entries_per_invpb",
            "count_per_invpb": 10000,
            "tree_pattern": "DecayTree",
            "lumi_pattern": "LumiTuple",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == [
        "Failed to get luminosity information (total luminosity = 0)"
    ]


def test_num_entries_per_invpb_failing_MC_nameTTree():
    data_in = {
        "check": {
            "type": "num_entries_per_invpb",
            "count_per_invpb": 10000,
            "tree_pattern": "RandomName",
            "lumi_pattern": "LumiTuple",
        }
    }
    file_list = [Path(__file__).parent.absolute() / "example_tuple_with_lumi.root"]
    result = checks.run_job_checks(
        ["check"],
        data_in,
        file_list,
    )["check"]
    assert not result.passed
    assert result.messages == [
        "No TTree objects found that match RandomName",
    ]


def test_range_check_passing():
    data_in = {
        "check": {
            "type": "range",
            "expression": "H1_PZ",
            "limits": {"min": 0.0, "max": 500000.0},
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert result.passed
    assert result.messages == [
        "Histogram of H1_PZ successfully filled from TTree DecayTree (contains 5134459.0 events)"
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []
    assert result.tree_data["DecayTree"]["num_entries"] == 5134459


def test_range_check_passing_multiple_files():
    data_in = {
        "check": {
            "type": "range",
            "expression": "H1_PZ",
            "limits": {"min": 0.0, "max": 500000.0},
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root",
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetUp.root",
        ],
    )["check"]
    assert result.passed
    assert result.messages == [
        "Histogram of H1_PZ successfully filled from TTree DecayTree (contains 8553802.0 events)"
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []
    assert result.tree_data["DecayTree"]["num_entries"] == 8553802


def test_range_check_failing_range():
    data_in = {
        "check": {
            "type": "range",
            "expression": "H1_PZ",
            "limits": {"min": -100000.0, "max": -99999.0},
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == ["No events found in range for Tree DecayTree"]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    for h in result.tree_data["DecayTree"]["histograms"]:
        assert h.sum() == 0


def test_range_check_failing_missing_branch():
    data_in = {
        "check": {
            "type": "range",
            "expression": "Dst_M",
            "limits": {"min": 1800.0, "max": 2300.0},
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    message = result.messages[0]
    pattern = r"Missing branch in "
    matched = False
    if re.match(pattern, message):
        matched = True
    assert not result.passed
    assert matched
    assert list(result.tree_data.keys()) == ["DecayTree"]
    for h in result.tree_data["DecayTree"]["histograms"]:
        assert h.sum() == 0


def test_range_check_failing_tree_name():
    data_in = {
        "check": {
            "type": "range",
            "expression": "H1_PZ",
            "limits": {"min": 0.0, "max": 500000.0},
            "blind_ranges": [],
            "tree_pattern": "RandomName",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
    assert list(result.tree_data.keys()) == []


def test_range_check_failing_bad_mean():
    data_in = {
        "check": {
            "type": "range",
            "expression": "H1_PZ",
            "limits": {"min": 0.0, "max": 500000.0},
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
            "exp_mean": 500000.0,
            "mean_tolerance": 1.0,
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == [
        "The observed mean (49110.65313794501) differs from the expected value by 450889.346862055 (<=1.0 required)"
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []
    assert result.tree_data["DecayTree"]["num_entries"] == 5134459


def test_range_check_failing_bad_stddev():
    data_in = {
        "check": {
            "type": "range",
            "expression": "H1_PZ",
            "limits": {"min": 0.0, "max": 500000.0},
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
            "exp_std": 500000.0,
            "std_tolerance": 1.0,
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == [
        "The observed standard deviation (53099.76473607609) differs from the expected value by 446900.2352639239 (<=1.0 required)"
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []
    assert result.tree_data["DecayTree"]["num_entries"] == 5134459


def test_range_check_nd_passing():
    data_in = {
        "check": {
            "type": "range_nd",
            "expressions": {"x": "H1_PZ", "y": "H2_PZ", "z": "H2_PX"},
            "limits": {
                "x": {"min": 0.0, "max": 500000.0},
                "y": {"min": 0.0, "max": 500000.0},
                "z": {"min": 0.0, "max": 500000.0},
            },
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert result.passed
    assert result.messages == [
        "Histogram of H1_PZ, H2_PZ successfully filled from TTree DecayTree (contains 5134453.0 events)",
        "Histogram of H1_PZ, H2_PX successfully filled from TTree DecayTree (contains 2525193.0 events)",
        "Histogram of H2_PZ, H2_PX successfully filled from TTree DecayTree (contains 2525806.0 events)",
        "Histogram of H1_PZ, H2_PZ, H2_PX successfully filled from TTree DecayTree (contains 2525189.0 events)",
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []


def test_range_check_nd_failing_num_var():
    data_in = {
        "check": {
            "type": "range_nd",
            "expressions": {"x": "H1_PZ"},
            "limits": {
                "x": {"min": 0.0, "max": 500000.0},
            },
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == ["Expected two or three variables."]
    assert list(result.tree_data.keys()) == []


def test_range_check_nd_failing_missing_limit():
    data_in = {
        "check": {
            "type": "range_nd",
            "expressions": {"x": "H1_PZ", "y": "H2_PZ"},
            "limits": {
                "x": {"min": 0.0, "max": 500000.0},
            },
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == [
        "For each variable, a corresponding range should be defined."
    ]
    assert list(result.tree_data.keys()) == []


def test_range_check_nd_failing_missing_branch():
    data_in = {
        "check": {
            "type": "range_nd",
            "expressions": {"x": "H1_PZ", "y": "Dst_M-D0_M"},
            "limits": {
                "x": {"min": 0.0, "max": 500000.0},
                "y": {"min": 138.0, "max": 150.0},
            },
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    message = result.messages[0]
    pattern = r"Missing branch in "
    matched = False
    if re.match(pattern, message):
        matched = True
    assert not result.passed
    assert matched
    assert list(result.tree_data.keys()) == ["DecayTree"]
    for h in result.tree_data["DecayTree"]["histograms"]:
        assert h.sum() == 0


def test_range_check_nd_failing_range():
    data_in = {
        "check": {
            "type": "range_nd",
            "expressions": {"x": "H1_PZ", "y": "H2_PZ"},
            "limits": {
                "x": {"min": -1000000.0, "max": -999999.0},
                "y": {"min": -1000000.0, "max": -999999.0},
            },
            "blind_ranges": [],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == ["No events found in range for Tree DecayTree"]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    for h in result.tree_data["DecayTree"]["histograms"]:
        assert h.sum() == 0


def test_range_check_nd_failing_tree_name():
    data_in = {
        "check": {
            "type": "range_nd",
            "expressions": {"x": "H1_PZ", "y": "H2_PZ"},
            "limits": {
                "x": {"min": 0.0, "max": 500000.0},
                "y": {"min": 0.0, "max": 500000.0},
            },
            "blind_ranges": [],
            "tree_pattern": "RandomName",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
    assert list(result.tree_data.keys()) == []


def test_range_check_bkg_subtracted_passing():
    data_in = {
        "check": {
            "type": "range_bkg_subtracted",
            "expression": "D0_PT",
            "limits": {"min": 0.0, "max": 500000.0},
            "expr_for_subtraction": "D0_MM",
            "mean_sig": 1865.0,
            "background_shift": 30.0,
            "background_window": 10.0,
            "signal_window": 20.0,
            "blind_ranges": {"min": 10000.0, "max": 30000.0},
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/MasterclassDatasets/D0lifetime/2014/MasterclassData.root"
        ],
    )["check"]
    assert result.passed
    assert (
        result.messages[0]
        == "Background subtraction performed successfully for Tree DecayTree"
    )
    assert list(result.tree_data.keys())[0] == "DecayTree"
    assert not result.tree_data["DecayTree"]["histograms"] == []


def test_range_check_bkg_subtracted_failing_range():
    data_in = {
        "check": {
            "type": "range_bkg_subtracted",
            "expression": "D0_PT",
            "limits": {"min": -1000000.0, "max": -999999.0},
            "expr_for_subtraction": "D0_MM",
            "mean_sig": 1865.0,
            "background_shift": 30.0,
            "background_window": 10.0,
            "signal_window": 20.0,
            "blind_ranges": {"min": 10000.0, "max": 30000.0},
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/MasterclassDatasets/D0lifetime/2014/MasterclassData.root"
        ],
    )["check"]
    assert not result.passed
    assert (
        result.messages[0]
        == "Not enough events for background subtraction found in range for Tree DecayTree"
    )
    assert list(result.tree_data.keys())[0] == "DecayTree"


def test_range_check_bkg_subtracted_failing_missing_branch():
    data_in = {
        "check": {
            "type": "range_bkg_subtracted",
            "expression": "D0_PT",
            "limits": {"min": 0.0, "max": 500000.0},
            "expr_for_subtraction": "Dst_M",
            "mean_sig": 1865.0,
            "background_shift": 30.0,
            "background_window": 10.0,
            "signal_window": 20.0,
            "blind_ranges": {"min": 10000.0, "max": 30000.0},
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/MasterclassDatasets/D0lifetime/2014/MasterclassData.root"
        ],
    )["check"]
    message = result.messages[0]
    print(message)
    pattern = r"Missing branch in "
    matched = False
    if re.match(pattern, message):
        matched = True
    assert not result.passed
    assert matched
    assert list(result.tree_data.keys())[0] == "DecayTree"


def test_range_check_bkg_subtracted_failing_tree_name():
    data_in = {
        "check": {
            "type": "range_bkg_subtracted",
            "expression": "D0_PT",
            "limits": {"min": 0.0, "max": 500000.0},
            "expr_for_subtraction": "D0_MM",
            "mean_sig": 1865.0,
            "background_shift": 30.0,
            "background_window": 10.0,
            "signal_window": 20.0,
            "blind_ranges": {"min": 10000.0, "max": 30000.0},
            "tree_pattern": "RandomName",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/MasterclassDatasets/D0lifetime/2014/MasterclassData.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
    assert list(result.tree_data.keys()) == []


def test_branches_exist_passing():
    data_in = {
        "check": {
            "type": "branches_exist",
            "branches": ["H1_PZ", "H2_PZ"],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert result.passed
    assert result.messages == ["All required branches were found in Tree DecayTree"]


def test_branches_exist_failing_missing_branches():
    data_in = {
        "check": {
            "type": "branches_exist",
            "branches": ["H1_PZ", "H2_PZ", "RandomName"],
            "tree_pattern": "DecayTree",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == [
        "Required branches not found in Tree DecayTree: ['RandomName']"
    ]


def test_branches_exist_failing_tree_name():
    data_in = {
        "check": {
            "type": "branches_exist",
            "branches": ["H1_PZ", "H2_PZ"],
            "tree_pattern": "RandomName",
        }
    }
    result = checks.run_job_checks(
        ["check"],
        data_in,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )["check"]
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
