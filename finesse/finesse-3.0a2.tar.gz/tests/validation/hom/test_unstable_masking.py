"""Tests ensuring that data points of a simulation scan get masked correctly when no
stable cavities nor gauss objects are present."""

import warnings

import numpy as np
import pytest

from finesse import Model
from finesse.analysis.actions import Xaxis
from finesse.warnings import CavityUnstableWarning


@pytest.fixture
def fp_cavity_model():
    IFO = Model()
    IFO.parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1

        m ITM Rc=-2
        s sc ITM.p2 ETM.p1 L=1
        m ETM Rc=2

        # Add a detector relying on internal FP trace tree
        cp fp_q FP q
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

    return IFO


def test_masked_critically_stable_fp(fp_cavity_model: Model):
    """Test data point with critically stable FP with g = 0 is masked
    for the relevant detectors."""
    IFO = fp_cavity_model

    # Ignore the unstable cavity warning for the purposes of this test.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        # Scan lengths [1.9, 2.0, 2.1] -> 2 should give g = 0
        out = IFO.run(Xaxis("sc.L", "lin", 1.9, 2.1, 2))

    qs = out["fp_q"]
    ws = out["in_w"]
    gs = out["fp_g"]

    assert np.ma.is_masked(qs)
    assert np.ma.is_masked(ws)

    assert np.all(np.ma.getmask(qs) == [False, True, False])
    assert np.all(np.ma.getmask(ws) == [False, True, False])

    assert not np.ma.is_masked(gs)

    assert gs[1] == 0


def test_masked_unstable_fp(fp_cavity_model: Model):
    """Test data points with critically stable -> unstable FP with
    g = 1, g > 1 masked for the relevant detectors."""
    IFO = fp_cavity_model

    # Ignore the unstable cavity warning for the purposes of this test.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        # Scan lengths [3.9, 4.0, 4.1] -> 4 should give g = 1, 4.1 should give g > 1
        out = IFO.run(Xaxis("sc.L", "lin", 3.9, 4.1, 2))

    qs = out["fp_q"]
    ws = out["in_w"]
    gs = out["fp_g"]

    assert np.ma.is_masked(qs)
    assert np.ma.is_masked(ws)

    assert np.all(np.ma.getmask(qs) == [False, True, True])
    assert np.all(np.ma.getmask(ws) == [False, True, True])

    assert not np.ma.is_masked(gs)

    assert gs[1] == 1


def test_allpoints_masked_unstable_fp(fp_cavity_model: Model):
    """Test data points with unstable FP for all points with g > 1 masked for the
    relevant detectors."""
    IFO = fp_cavity_model

    # Ignore the unstable cavity warning for the purposes of this test.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        # Scan lengths in [5, 6] -> all should give g > 1
        out = IFO.run(Xaxis("sc.L", "lin", 5, 6, 2))

    qs = out["fp_q"]
    ws = out["in_w"]
    gs = out["fp_g"]

    assert np.ma.is_masked(qs)
    assert np.ma.is_masked(ws)

    assert np.all(np.ma.getmask(qs) == [True, True, True])
    assert np.all(np.ma.getmask(ws) == [True, True, True])

    assert not np.ma.is_masked(gs)

    assert np.all(gs > 1)


@pytest.fixture
def fp_cavity_model_with_disabled_gauss():
    IFO = Model()
    IFO.parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1

        m ITM Rc=-2
        s sc ITM.p2 ETM.p1 L=1
        m ETM Rc=2

        # Add a detector relying on internal FP trace tree
        cp fp_q FP q
        # and another relying on an external FP trace tree
        bp in_w L0.p1.o w

        # Add a detector for the g-factor, the outputs of
        # this should never be masked
        cp fp_g FP g

        cav FP ITM.p2
        # Add a gauss at the laser now...
        gauss gL0 L0.p1.o w0=0.5m z=-0.5
        """
    )
    IFO.ITM.Rcy = IFO.ITM.Rcx.ref
    IFO.ETM.Rcy = IFO.ETM.Rcx.ref

    # ... but explicitly disable this gauss object for simulations
    IFO.sim_trace_config["disable"] = "gL0"

    return IFO


def test_masked_critically_stable_fp_disabled_gauss(
    fp_cavity_model_with_disabled_gauss: Model,
):
    """Test data point with critically stable FP with g = 0 is masked
    for the relevant detectors; when the additional Gauss object is disabled
    via sim_trace_config."""
    IFO = fp_cavity_model_with_disabled_gauss

    # Ignore the unstable cavity warning for the purposes of this test.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        # Scan lengths [1.9, 2.0, 2.1] -> 2 should give g = 0
        out = IFO.run(Xaxis("sc.L", "lin", 1.9, 2.1, 2))

    qs = out["fp_q"]
    ws = out["in_w"]
    gs = out["fp_g"]

    assert np.ma.is_masked(qs)
    assert np.ma.is_masked(ws)

    assert np.all(np.ma.getmask(qs) == [False, True, False])
    assert np.all(np.ma.getmask(ws) == [False, True, False])

    assert not np.ma.is_masked(gs)

    assert gs[1] == 0


def test_masked_unstable_fp_disabled_gauss(fp_cavity_model_with_disabled_gauss: Model):
    """Test data points with critically stable -> unstable FP with
    g = 1, g > 1 masked for the relevant detectors; when the additional
    Gauss object is disabled via sim_trace_config."""
    IFO = fp_cavity_model_with_disabled_gauss

    # Ignore the unstable cavity warning for the purposes of this test.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        # Scan lengths [3.9, 4.0, 4.1] -> 4 should give g = 1, 4.1 should give g > 1
        out = IFO.run(Xaxis("sc.L", "lin", 3.9, 4.1, 2))

    qs = out["fp_q"]
    ws = out["in_w"]
    gs = out["fp_g"]

    assert np.ma.is_masked(qs)
    assert np.ma.is_masked(ws)

    assert np.all(np.ma.getmask(qs) == [False, True, True])
    assert np.all(np.ma.getmask(ws) == [False, True, True])

    assert not np.ma.is_masked(gs)

    assert gs[1] == 1


def test_allpoints_masked_unstable_fp_disabled_gauss(
    fp_cavity_model_with_disabled_gauss: Model,
):
    """Test data points with unstable FP for all points with g > 1 masked for the
    relevant detectors; when the additional Gauss object is disabled via
    sim_trace_config."""
    IFO = fp_cavity_model_with_disabled_gauss

    # Ignore the unstable cavity warning for the purposes of this test.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        # Scan lengths in [5, 6] -> all should give g > 1
        out = IFO.run(Xaxis("sc.L", "lin", 5, 6, 2))

    qs = out["fp_q"]
    ws = out["in_w"]
    gs = out["fp_g"]

    assert np.ma.is_masked(qs)
    assert np.ma.is_masked(ws)

    assert np.all(np.ma.getmask(qs) == [True, True, True])
    assert np.all(np.ma.getmask(ws) == [True, True, True])

    assert not np.ma.is_masked(gs)

    assert np.all(gs > 1)
