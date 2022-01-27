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

import os
import shutil
from pathlib import Path

import pytest
import ROOT

from pidcalib2 import merge_trees


@pytest.fixture
def test_path():
    return Path(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.pyroot
def test_copy_tree(test_path, tmp_path):
    shutil.copy(
        test_path / "test_data/ref_test_data.root",
        tmp_path / "ref_test_data_copy.root",
    )

    merge_trees.copy_tree_and_set_as_friend(
        str(test_path / "test_data/ref_PID_eff.root"),
        "PID_eff_tree",
        str(tmp_path / "ref_test_data_copy.root"),
        "DecayTree",
    )

    new_file = ROOT.TFile(str(tmp_path / "ref_test_data_copy.root"))
    new_tree = new_file.Get("DecayTree")

    assert new_tree.GetEntry(0) == 84
    assert new_tree.PID_eff == pytest.approx(0.9933816230604905)


@pytest.mark.pyroot
def test_copy_tree_bad_filenames(test_path, tmp_path):
    shutil.copy(
        test_path / "test_data/ref_test_data.root",
        tmp_path / "ref_test_data_copy.root",
    )
    # It seems some versions of pyroot raise OSError when a file that should be
    # opened doesn't exist, while others don't and we catch the issue later,
    # raising a SystemExit
    with pytest.raises((OSError, SystemExit)):
        merge_trees.copy_tree_and_set_as_friend(
            str(test_path / "test_data/x.root"),
            "PID_eff_tree",
            str(tmp_path / "ref_test_data_copy.root"),
            "DecayTree",
        )

    with pytest.raises(SystemExit):
        merge_trees.copy_tree_and_set_as_friend(
            str(test_path / "test_data/ref_PID_eff.root"),
            "PID_eff_tree",
            str(test_path / "test_data/x.root"),
            "DecayTree",
        )


@pytest.mark.pyroot
def test_copy_tree_bad_treenames(test_path, tmp_path):
    shutil.copy(
        test_path / "test_data/ref_test_data.root",
        tmp_path / "ref_test_data_copy.root",
    )

    with pytest.raises(SystemExit):
        merge_trees.copy_tree_and_set_as_friend(
            str(test_path / "test_data/ref_PID_eff.root"),
            "x",
            str(tmp_path / "ref_test_data_copy.root"),
            "DecayTree",
        )

    with pytest.raises(SystemExit):
        merge_trees.copy_tree_and_set_as_friend(
            str(test_path / "test_data/ref_PID_eff.root"),
            "PID_eff_tree",
            str(tmp_path / "ref_test_data_copy.root"),
            "x",
        )
