"""Mode mismatch detector tests."""

import pytest
from finesse import Model
from finesse.analysis.actions import Xaxis
from finesse.components import Gauss
from finesse.detectors import BeamPropertyDetector
from finesse.gaussian import transform_beam_param, BeamParam
from numpy.testing import assert_allclose


@pytest.fixture
def matched_input_to_cavity_model():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    s s0 L0.p1 ITM.p1

    m ITM Rc=-2.5
    s sc ITM.p2 ETM.p1 L=1
    m ETM Rc=2.5

    cav FP ITM.p2

    mmd mmt1 ITM.p1 ITM.p2
    mmd mmt2 ITM.p2 ITM.p1
    cp fp_q FP q
    """
    )
    IFO.ITM.Rcy = IFO.ITM.Rcx.ref
    IFO.ETM.Rcy = IFO.ETM.Rcx.ref

    # Add an input beam with q matched to cavity
    trace = IFO.beam_trace()
    IFO.add(Gauss("gL0", IFO.L0.p1.o, q=trace[IFO.L0.p1.o]))

    return IFO


def test_eigenmode_scan_with_etm_roc_changing(matched_input_to_cavity_model):
    """Test sweeping of ETM RoC gives mode mismatch with input beam."""
    IFO = matched_input_to_cavity_model
    out = IFO.run(Xaxis("ETM.Rcx", "lin", 2.5, 10, 100))
    mmt1 = out["mmt1"]
    mmt2 = out["mmt2"]

    # First check that mismatch is equal for both
    # transmission couplings at ITM
    assert_allclose(mmt1, mmt2)

    q2s = out["fp_q"]
    q1 = IFO.beam_trace()[IFO.ITM.p1.i].qx
    q1p = transform_beam_param(IFO.ITM.abcd12x, q1)
    mms = 1.0 - BeamParam.overlap(q1p, q2s)

    assert_allclose(mmt1, mms)


def test_eigenmode_scan_with_itm_roc_changing(matched_input_to_cavity_model):
    """Test sweeping of ITM RoC gives mode mismatch with input beam."""
    IFO = matched_input_to_cavity_model
    out = IFO.run(Xaxis("ITM.Rcx", "lin", 2.5, 10, 100))
    mmt1 = out["mmt1"]
    mmt2 = out["mmt2"]

    # First check that mismatch is equal for both
    # transmission couplings at ITM
    assert_allclose(mmt1, mmt2)

    q2s = out["fp_q"]
    q1 = IFO.beam_trace()[IFO.ITM.p1.i].qx
    q1p = transform_beam_param(IFO.ITM.abcd12x, q1)
    mms = 1.0 - BeamParam.overlap(q1p, q2s)

    assert_allclose(mmt1, mms)


def test_input_beam_waist_size_x_scan(matched_input_to_cavity_model):
    """Test sweeping of input beam waist size gives mode mismatch to cavity."""
    IFO = matched_input_to_cavity_model
    IFO.add(BeamPropertyDetector("q1", IFO.ITM.p1.i, "q"))
    out = IFO.run(Xaxis("gL0.w0x", "lin", IFO.gL0.w0x.value, 2 * IFO.gL0.w0x.value, 100))
    mmt1 = out["mmt1"]
    mmt2 = out["mmt2"]

    # First check that mismatch is equal for both
    # transmission couplings at ITM
    assert_allclose(mmt1, mmt2)

    q2s = out["fp_q"]
    # Check that eigenmode hasn't changed
    assert_allclose(q2s, IFO.FP.qx.q)

    q1 = out["q1"]
    q1p = transform_beam_param(IFO.ITM.abcd12x, q1)
    mms = 1.0 - BeamParam.overlap(q1p, q2s)

    assert_allclose(mmt1, mms)


def test_input_beam_waist_size_y_scan(matched_input_to_cavity_model):
    """Test that sweeping input beam waist size in sagittal plane results in zeroes for
    mismatch detectors (as they should be detecting in tangential plane)"""
    IFO = matched_input_to_cavity_model
    out = IFO.run(Xaxis("gL0.w0y", "lin", IFO.gL0.w0y.value, 2 * IFO.gL0.w0y.value, 100))
    mmt1 = out["mmt1"]
    mmt2 = out["mmt2"]

    # First check that mismatch is equal for both
    # transmission couplings at ITM
    assert_allclose(mmt1, mmt2)

    q2s = out["fp_q"]
    # Check that eigenmode hasn't changed
    assert_allclose(q2s, IFO.FP.qx.q)

    assert_allclose(mmt1, 0)


# TODO (sjr) Test mismatches at different components (e.g. beamsplitters)
