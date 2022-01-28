"""Tests for outputs from asymmetric tracing simulations. Typically checking for
zero scattering into HOMs due to the utility this type of tracing provides."""

import pytest
from finesse.analysis.actions import Noxaxis


def test_reflection_from_surface_mismatch(model):
    """Test that mismatch on reflection from a single curved mirror
    is zero when tracing asymmetrically."""
    model.parse(
        """
        l L0 P=1
        s s0 L0.p1 M.p1 L=1
        m M Rc=50

        gauss gL0 L0.p1.o w0=1m z=0

        mmd mmrx M.p1.i M.p1.o x
        mmd mmry M.p1.i M.p1.o y
        """
    )

    model.sim_trace_config["symmetric"] = False
    out = model.run(Noxaxis())

    # Mismatches (in both planes) on reflection from a mirror
    # should be zero when using asymmetric tracing
    assert out["mmrx"] == 0
    assert out["mmry"] == 0


def test_flat_michelson_output_power(model):
    """Test that output power from lossless, fully reflective Michelson with
    flat mirrors is equal to input power (when tuned to light fringe) in the
    case where asymmetric tracing is used. The input beam waist is positioned
    before the Michelson.
    """
    model.parse(
        """
        l L0 P=1
        s s0 L0.p1 BS.p1 L=5

        bs BS

        s sY BS.p2 MY.p1 L=10
        m MY R=1 T=0

        s sX BS.p3 MX.p1 L=10
        m MX R=1 T=0

        gauss gL0 L0.p1.o z=-2.5 w0=1m

        pd P BS.p4.o

        modes(maxtem=0)
        """
    )

    model.sim_trace_config["symmetric"] = False
    out = model.run(Noxaxis())

    # BS tuned to light fringe so fields in phase at output
    # should give P = laser power as mirrors fully reflective
    # -> Only true for asymmetric tracing, as spurious mismatches
    #    are avoided in this case
    assert out["P"] == pytest.approx(model.L0.P.value)
