"""Tests for Model.detect_mismatches()."""

import pytest
from finesse import Model


@pytest.fixture
def matched_cavity_model():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    s s0 L0.p1 ITM.p1

    m ITM Rc=-2.5
    s sc ITM.p2 ETM.p1 L=1
    m ETM Rc=2.5

    cav FP ITM.p2
    """
    )

    return IFO


def test_cavity_is_matched(matched_cavity_model):
    mms = matched_cavity_model.detect_mismatches()
    assert bool(mms) is False


def test_cavity_is_mismatched(matched_cavity_model):
    model = matched_cavity_model

    # create mismatch
    model.create_mismatch(model.ITM.p1.i, w0_mm=10, z_mm=-8)

    # detect
    mms = model.detect_mismatches()

    # assert test
    expected_couplings = [
        ["ITM.p1.i", "ITM.p1.o"],
        ["ITM.p2.i", "ITM.p1.o"],
        ["ITM.p1.i", "ITM.p2.o"],
    ]

    test_couplings = [[coupling.full_name for coupling in key] for key in mms.keys()]

    assert len(test_couplings) == len(expected_couplings)

    for expected_coupling in expected_couplings:
        assert expected_coupling in test_couplings
