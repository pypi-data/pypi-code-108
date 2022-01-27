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

import pytest

from pidcalib2 import binning


def test_p_binning():
    with pytest.raises(KeyError):
        binning.p_binning("graviton")

    reference_K_pi_p_binning = [
        3000,
        9300,
        15600,
        19000.0,
        24400.0,
        29800.0,
        35200.0,
        40600.0,
        46000.0,
        51400.0,
        56800.0,
        62200.0,
        67600.0,
        73000.0,
        78400.0,
        83800.0,
        89200.0,
        94600.0,
        100000.0,
    ]
    assert binning.p_binning("K") == reference_K_pi_p_binning
    assert binning.p_binning("Pi") == reference_K_pi_p_binning
    assert binning.p_binning("P") == reference_K_pi_p_binning

    assert binning.p_binning("Mu") == [
        3000,
        6000,
        8000,
        10000,
        12000,
        14500,
        17500,
        21500,
        27000,
        32000,
        40000,
        60000,
        70000,
        100000.0,
    ]

    with pytest.raises(KeyError):
        binning.p_binning("pi")

    with pytest.raises(KeyError):
        binning.p_binning("Nu")


def test_set_binning():
    with pytest.raises(TypeError):
        binning.set_binning("Pi", "P", 30)  # type: ignore

    binning.set_binning("GhostParticle", "P", [10, 20])
    assert binning.binnings["GhostParticle"]["P"] == {"bin_edges": [10, 20]}


def test_get_binning():
    with pytest.raises(KeyError):
        binning.get_binning("PION", "P")

    with pytest.raises(KeyError):
        binning.get_binning("Pi", "Non-existing var")
