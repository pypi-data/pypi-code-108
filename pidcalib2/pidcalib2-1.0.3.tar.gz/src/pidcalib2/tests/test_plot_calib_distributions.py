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

import pickle

import boost_histogram as bh
import numpy as np
import pytest

from pidcalib2 import binning, plot_calib_distributions


@pytest.mark.xrootd
@pytest.mark.slow
def test_plot_calib_distributions(tmp_path):
    config = {
        "particle": "K",
        "magnet": "down",
        "sample": "Turbo18",
        "max_files": 1,
        "bin_vars": ["DLLK"],
        "bins": 50,
        "force_uniform": True,
        "verbose": True,
        "output_dir": tmp_path,
        "file_list": None,
        "samples_file": None,
        "binning_file": None,
        "format": "png",
        "cuts": ["P > 10000"],
    }
    # Save and restore binnings that are destroyed by "force_uniform" to avoid
    # breaking following tests
    orig_binnings = binning.binnings.copy()
    plot_calib_distributions.plot_calib_distributions(config)
    binning.binnings = orig_binnings

    plot_path = tmp_path / "DLLK.png"
    assert plot_path.stat().st_size > 2e4

    with open(tmp_path / "plot_calib_distributions.pkl", "rb") as f:
        saved_hist = pickle.load(f)
    assert saved_hist.values().sum() == pytest.approx(99626.4631959981)
    assert saved_hist.variances().sum() == pytest.approx(128093.73652275163)


@pytest.mark.xrootd
@pytest.mark.slow
def test_create_plot_histograms():
    config = {
        "particle": "K",
        "bin_vars": ["DLLK"],
        "bins": 50,
        "force_uniform": False,
        "cuts": None,
    }
    calib_sample = {
        "files": [
            "root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/LHCb/Collision15/PIDCALIB.ROOT/00064787/0000/00064787_00000037_1.pidcalib.root",  # noqa
        ]
    }
    tree_paths = ["DSt_KPTuple/DecayTree"]
    branch_names = {"sWeight": "probe_sWeight", "DLLK": "probe_PIDK"}

    hists = plot_calib_distributions.create_plot_histograms(
        config, calib_sample, tree_paths, branch_names
    )

    assert hists[calib_sample["files"][0]]["DLLK"].sum().value == pytest.approx(  # type: ignore # noqa
        6682.033686340834
    )


def test_save_plots(tmp_path):
    hists = {}
    data = np.random.normal(3.5, 2.5, size=100)
    hist = bh.Histogram(bh.axis.Regular(40, -2, 10))  # type: ignore
    hist.fill(data)
    hists["test_var"] = hist
    plot_calib_distributions.save_plots(hists, tmp_path, "png")
    plot_path = tmp_path / "test_var.png"
    assert plot_path.stat().st_size > 2e4


def test_save_histograms(tmp_path):
    hists = {}
    data = np.random.normal(3.5, 2.5, size=100)
    hist = bh.Histogram(bh.axis.Regular(40, -2, 10))  # type: ignore
    hist.fill(data)
    hists["test_var"] = hist
    plot_calib_distributions.save_histograms(hists, tmp_path)
    with open(tmp_path / "plot_calib_distributions.pkl", "rb") as f:
        saved_hist = pickle.load(f)
    assert saved_hist == hist


def test_decode_arguments():
    assert (
        plot_calib_distributions.decode_arguments(
            [
                "--sample=Turbo18",
                "--magnet=up",
                "--particle=Pi",
                "--bin-var=DLLK",
                "--bin-var=P",
                "--output-dir=pidcalib_output",
            ]
        ).magnet
        == "up"
    )

    with pytest.raises(SystemExit):
        plot_calib_distributions.decode_arguments(
            [
                "--sample=Turbo18",
                "--magnet=up",
                "--bin-var=DLLK",
                "--bin-var=P",
                "--output-dir=pidcalib_output",
            ]
        )
