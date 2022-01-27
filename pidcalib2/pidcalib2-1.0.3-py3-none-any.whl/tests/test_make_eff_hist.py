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

import copy
import math
import os
from pathlib import Path

import pandas as pd
import pytest

from pidcalib2 import binning, make_eff_hists


@pytest.fixture
def test_path():
    return Path(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def config():
    return {
        "bin_vars": None,
        "binning_file": None,
        "cuts": None,
        "file_list": None,
        "list": None,
        "local_dataframe": None,
        "magnet": None,
        "output_dir": None,
        "particle": None,
        "pid_cuts": None,
        "sample": None,
        "samples_file": None,
        "verbose": True,
    }


def test_make_eff_hists(config, test_path, tmp_path):
    config.update(
        {
            "bin_vars": ["P"],
            "local_dataframe": str(test_path / "test_data/cal_test_data.csv"),
            "magnet": "up",
            "output_dir": str(tmp_path / "test_output"),
            "particle": "Pi",
            "pid_cuts": ["DLLK < 4", "DLLK<3"],
            "sample": "Turbo18",
        }
    )
    make_eff_hists.make_eff_hists(config)
    eff_histo = pd.read_pickle(
        tmp_path / "test_output/effhists-Turbo18-up-Pi-DLLK<4-P.pkl"
    )

    # These asserts might come in handy when some detail in the boost_histogram
    # implementation changes, thus failing the reference histogram comparison.
    assert eff_histo.sum(flow=False).value == pytest.approx(17.812484216412948)
    assert eff_histo.sum(flow=True).value == pytest.approx(23.57053953265155)
    assert eff_histo[1].value == 0.8978157343833105

    eff_histo_reference = pd.read_pickle(
        test_path / "test_data/effhists-Turbo18-up-pi-DLLK<4-P.pkl"
    )
    assert eff_histo == eff_histo_reference


def test_make_eff_hists_with_user_cuts(config, test_path, tmp_path):
    config.update(
        {
            "bin_vars": ["P"],
            "cuts": ["Dst_IPCHI2 < 100", "probe_TRACK_GHOSTPROB < 0.05"],
            "local_dataframe": str(test_path / "test_data/cal_test_data.csv"),
            "magnet": "up",
            "output_dir": str(tmp_path / "test_output"),
            "particle": "Pi",
            "pid_cuts": ["DLLK < 4", "DLLK<3"],
            "sample": "Turbo18",
        }
    )
    make_eff_hists.make_eff_hists(config)
    eff_histo = pd.read_pickle(
        tmp_path / "test_output/effhists-Turbo18-up-Pi-DLLK<4-P.pkl"
    )

    # These asserts might come in handy when some detail in the boost_histogram
    # implementation changes, thus failing the reference histogram comparison.
    assert eff_histo.sum(flow=False).value == pytest.approx(17.812484216412948)
    assert eff_histo.sum(flow=True).value == pytest.approx(23.57053953265155)
    assert eff_histo[1].value == 0.8978157343833105

    eff_histo_reference = pd.read_pickle(
        test_path / "test_data/effhists-Turbo18-up-pi-DLLK<4-P.pkl"
    )
    assert eff_histo == eff_histo_reference

    # Test that stricter cuts have an effect
    config["cuts"] = ["Dst_IPCHI2 < 9", "probe_TRACK_GHOSTPROB < 0.01"]
    make_eff_hists.make_eff_hists(config)
    eff_histo = pd.read_pickle(
        tmp_path / "test_output/effhists-Turbo18-up-Pi-DLLK<4-P.pkl"
    )

    # With stricter cuts, some bins in the efficiency histogram become empty
    assert math.isnan(eff_histo.sum(flow=False).value)
    assert math.isnan(eff_histo.sum(flow=True).value)
    assert eff_histo[1].value == 0.806456926487749

    assert eff_histo != eff_histo_reference


@pytest.mark.xrootd
@pytest.mark.slow
def test_make_eff_hists_with_hardcoded_cuts(config, tmp_path):
    config.update(
        {
            "bin_vars": ["P"],
            "magnet": "down",
            "max_files": 1,
            "output_dir": str(tmp_path / "test_output"),
            "particle": "P_IncLc",
            "pid_cuts": ["DLLp > 4"],
            "sample": "Turbo16",
        }
    )
    make_eff_hists.make_eff_hists(config)
    eff_histo = pd.read_pickle(
        tmp_path / "test_output/effhists-Turbo16-down-P_IncLc-DLLp>4-P.pkl"
    )

    # These asserts might come in handy when some detail in the boost_histogram
    # implementation changes, thus failing the reference histogram comparison.
    assert eff_histo.sum(flow=False) == eff_histo.sum(flow=True)
    assert eff_histo.sum(flow=True).value == pytest.approx(17.3387622437092)
    assert eff_histo[1].value == 0.9686555826741122


@pytest.mark.xrootd
@pytest.mark.slow
def test_make_eff_hists_local_file_list(config, test_path, tmp_path):
    config.update(
        {
            "bin_vars": ["P"],
            "file_list": str(test_path / "test_data/test_file_list"),
            "magnet": "up",
            "output_dir": str(tmp_path / "test_output"),
            "particle": "Pi",
            "pid_cuts": ["DLLK < 4", "DLLK<3"],
            "sample": "Turbo18",
        }
    )
    make_eff_hists.make_eff_hists(config)
    eff_histo = pd.read_pickle(
        tmp_path / "test_output/effhists-Turbo18-up-Pi-DLLK<4-P.pkl"
    )

    # These asserts might come in handy when some detail in the boost_histogram
    # implementation changes, thus failing the reference histogram comparison.
    assert eff_histo.sum(flow=False).value == pytest.approx(17.378390835392615)
    assert eff_histo[1].value == 0.9797018332573063


@pytest.mark.xrootd
@pytest.mark.slow
def test_make_eff_hists_file_list(config, test_path, tmp_path):
    config.update(
        {
            "bin_vars": ["P"],
            "magnet": "up",
            "max_files": 1,
            "output_dir": str(tmp_path / "test_output"),
            "particle": "Pi",
            "pid_cuts": ["DLLK < 4", "DLLK<3"],
            "sample": "Turbo18",
            "samples_file": str(test_path / "test_data/test_samples.json"),
        }
    )
    make_eff_hists.make_eff_hists(config)
    eff_histo = pd.read_pickle(
        tmp_path / "test_output/effhists-Turbo18-up-Pi-DLLK<4-P.pkl"
    )

    # These asserts might come in handy when some detail in the boost_histogram
    # implementation changes, thus failing the reference histogram comparison.
    assert eff_histo.sum(flow=False).value == pytest.approx(17.378390835392615)
    assert eff_histo[1].value == 0.9797018332573063


def test_decode_arguments(capsys, test_path, tmp_path):
    assert (
        make_eff_hists.decode_arguments(
            [
                "--sample=Turbo18",
                "-m=up",
                "--particle=K",
                "--pid-cut='DLLK>5'",
                "--bin-var=P",
            ]
        ).verbose
        is False
    )

    with pytest.raises(SystemExit):
        make_eff_hists.decode_arguments(
            ["-m=up", "--particle=K", "--pid-cut='DLLK>5'", "--bin-var=P"]
        )

    with pytest.raises(SystemExit):
        make_eff_hists.decode_arguments(
            ["--sample=Turbo18", "-m=up", "--particle=K", "--bin-var=P"]
        )

    with pytest.raises(SystemExit):
        make_eff_hists.decode_arguments(
            ["--list", str(test_path / "test_data/test_samples.json")]
        )
    captured = capsys.readouterr().out
    assert captured == (
        "Sample  | Magnet | Particle\n"
        "--------|--------|---------\n"
        "Turbo18 | up     | Pi\n"
    )


def test_make_eff_hists_with_custom_binning(config, test_path, tmp_path):
    # Save the original binnings so we can restore them later
    orig_binnings = copy.deepcopy(binning.binnings)

    config.update(
        {
            "bin_vars": ["P"],
            "binning_file": str(test_path / "test_data/custom_binning.json"),
            "local_dataframe": str(test_path / "test_data/cal_test_data.csv"),
            "magnet": "up",
            "output_dir": str(tmp_path / "test_output"),
            "particle": "Pi",
            "pid_cuts": ["DLLK < 4", "DLLK<3"],
            "sample": "Turbo18",
        }
    )

    make_eff_hists.make_eff_hists(config)
    eff_histo = pd.read_pickle(
        tmp_path / "test_output/effhists-Turbo18-up-Pi-DLLK<4-P.pkl"
    )

    # These asserts might come in handy when some detail in the boost_histogram
    # implementation changes, thus failing the reference histogram comparison.
    assert eff_histo.sum(flow=False).value == pytest.approx(1.8099485065453211)
    assert eff_histo.sum(flow=True).value == pytest.approx(41.404466293590865)
    assert eff_histo[1].value == 0.9625150986552666

    # Restore original binnings for other tests
    binning.binnings = orig_binnings
