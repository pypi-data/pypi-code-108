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
from pathlib import Path

import pytest

from pidcalib2 import ref_calib


@pytest.fixture
def test_path():
    return Path(os.path.dirname(os.path.abspath(__file__)))


def test_ref_calib(test_path, tmp_path):
    config = {
        "sample": "Turbo18",
        "magnet": "up",
        "bin_vars": '{"P": "P", "ETA": "ETA", "nTracks": "nTracks"}',
        "histo_dir": str(test_path / "test_data"),
        "output_file": str(tmp_path / "PIDCalibResults.root"),
        "merge": False,
        "ref_file": str(test_path / "test_data/ref_test_data.root"),
        "ref_tree": "DecayTree",
        "ref_pars": '{"Bach": ["K", "DLLK > 4"]}',
        "verbose": False,
    }

    assert ref_calib.ref_calib(config) == pytest.approx(0.8798221261720731)
    assert (tmp_path / "PIDCalibResults.root").exists()

    with pytest.raises(SyntaxError):
        config = {
            "sample": "Turbo18",
            "magnet": "up",
            "bin_vars": '{"P", "ETA", "nTracks"}',
            "output_file": str(tmp_path / "test_data/test_data_PIDCalibResults.root"),
            "merge": False,
            "ref_file": str(test_path / "test_data/ref_test_data.root"),
            "ref_tree": "DecayTree",
            "ref_pars": '{"Bach": ["K", "DLLK > 4"]}',
            "verbose": False,
        }
        ref_calib.ref_calib(config)

    with pytest.raises(SyntaxError):
        config = {
            "sample": "Turbo18",
            "magnet": "up",
            "bin_vars": '{"P": "P", "ETA": "ETA", "nTracks": "nTracks"}',
            "output_file": str(tmp_path / "test_data/test_data_PIDCalibResults.root"),
            "merge": False,
            "ref_file": str(test_path / "test_data/ref_test_data.root"),
            "ref_tree": "DecayTree",
            "ref_pars": '{"Bach"}',
            "verbose": False,
        }
        ref_calib.ref_calib(config)


def test_decode_arguments():
    assert (
        ref_calib.decode_arguments(
            [
                "--sample=Turbo18",
                "-m=up",
                "--ref-file=ref_file.root",
                "--ref-pars={'Ref': ['pi', 'DLLK<5']}",
                "--output-file=output.root",
            ]
        ).magnet
        == "up"
    )

    with pytest.raises(SystemExit):
        ref_calib.decode_arguments(
            [
                "--sample=Turbo18",
                "-m=up",
                "--ref-file=ref_file.root",
                "--ref-pars={'Ref': ['pi', 'DLLK<5']}",
            ]
        ).magnet

    with pytest.raises(SystemExit):
        ref_calib.decode_arguments(
            [
                "--sample=Turbo18",
                "-m=up",
                "--ref-file=ref_file.root",
                "--ref-pars={'Ref': ['pi', 'DLLK<5']}",
                "--particle=K",
            ]
        )

    with pytest.raises(SystemExit):
        ref_calib.decode_arguments(
            [
                "--sample=Turbo18",
                "-m=MagUp",
                "--ref-file=ref_file.root",
                "--ref-pars={'Ref': ['pi', 'DLLK<5']}",
            ]
        )

    with pytest.raises(SystemExit):
        ref_calib.decode_arguments(
            [
                "--sample=Turbo18",
                "-m=up",
                "--ref-file=ref_file.root",
            ]
        )
