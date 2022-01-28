"""Tests ensuring that data points of a simulation scan where cavities become unstable
correctly transition to a contingent forest mode if any other stable dependency is in
the model."""

import warnings
import numpy as np
import pytest
from finesse import Model
from finesse.analysis.actions import Xaxis
from finesse.components import Gauss
from finesse.gaussian import BeamParam
from finesse.warnings import CavityUnstableWarning


@pytest.fixture
def fp_cavity_model_with_gauss():
    IFO = Model()
    IFO.parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1

        m ITM Rc=-2
        s sc ITM.p2 ETM.p1 L=1
        m ETM Rc=2

        cp cav_q FP q
        # Add a detector relying on internal FP trace tree
        bp fp_q ITM.p2.o q
        # and another relying on an external FP trace tree
        bp in_w L0.p1.o w

        # Add a detector for the g-factor, the outputs of
        # this should never be masked
        cp fp_g FP g

        cav FP ITM.p2
        """
    )
    IFO.ITM.Rcy = IFO.ITM.Rcx.ref
    IFO.ETM.Rcy = IFO.ETM.Rcx.ref

    # Make sure output values of fp_q detector are BeamParam objects
    IFO.fp_q.q_as_bp = True

    # Add an input beam with q matched to cavity
    trace = IFO.beam_trace()
    IFO.add(Gauss("gL0", IFO.L0.p1.o, q=trace[IFO.L0.p1.o]))

    return IFO


def test_critically_stable_fp(fp_cavity_model_with_gauss: Model):
    IFO = fp_cavity_model_with_gauss

    # Ignore the unstable cavity warning for the purposes of this test.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        # Scan lengths [1.9, 2.0, 2.1] -> 2 should give g = 0
        out = IFO.run(Xaxis("sc.L", "lin", 1.9, 2.1, 2))

    q_modes = out["cav_q"]
    qs = out["fp_q"]
    ws = out["in_w"]
    gs = out["fp_g"]

    # FP has entered critically stable point but gL0 still exists
    # so the simulation should use the tree from gL0 as a contingent
    # forest now --- meaning nothing should be masked
    assert not np.ma.is_masked(qs)
    assert not np.ma.is_masked(ws)
    assert not np.ma.is_masked(gs)

    assert gs[1] == 0

    gauss_q = BeamParam(q=IFO.gL0.qx)

    assert qs[0] != gauss_q
    assert qs[2] != gauss_q
    # q at cavity node should be equal to gauss q (as L=0 between L0 and ITM)
    # for the point where the cavity becomes critically stable
    assert qs[1] == gauss_q

    # Cavity eigenmode at g = 0 point should be NaN
    assert np.isnan(q_modes[1])


def test_unstable_fp(fp_cavity_model_with_gauss: Model):
    IFO = fp_cavity_model_with_gauss

    # Ignore the unstable cavity warning for the purposes of this test.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        # Scan lengths [3.9, 4.0, 4.1] -> 4 should give g = 1, 4.1 should give g > 1
        out = IFO.run(Xaxis("sc.L", "lin", 3.9, 4.1, 2))

    q_modes = out["cav_q"]
    qs = out["fp_q"]
    ws = out["in_w"]
    gs = out["fp_g"]

    # FP has entered critically stable point but gL0 still exists
    # so the simulation should use the tree from gL0 as a contingent
    # forest now --- meaning nothing should be masked
    assert not np.ma.is_masked(qs)
    assert not np.ma.is_masked(ws)
    assert not np.ma.is_masked(gs)

    assert gs[1] == 1
    assert gs[2] > 1

    gauss_q = BeamParam(q=IFO.gL0.qx)

    assert qs[0] != gauss_q
    # q at cavity node should be equal to gauss q (as L=0 between L0 and ITM)
    # for g = 1 and g > 1
    assert qs[1] == gauss_q
    assert qs[2] == gauss_q

    # Cavity eigenmode at g >= 1 points should be NaN
    assert np.isnan(q_modes[1])
    assert np.isnan(q_modes[2])


# TODO (sjr) More tests for other configurations, especially those which include
#            coupled / overlapping cavities
