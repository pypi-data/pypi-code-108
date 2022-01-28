"""Tests for model trace forest structure when cavities which overlap are included."""

from itertools import permutations

import pytest
from finesse import Model
import finesse.ligo
from finesse.tracing.tree import TraceTree
from ...util import assert_trace_trees_equal


@pytest.fixture()
def aligo_model():
    IFO = Model()
    IFO.parse(finesse.ligo.aligo_katscript)
    return IFO


@pytest.mark.parametrize("order", list(permutations(["PRX", "PRY"])))
def test_overlapping_prx_pry_forest(aligo_model: Model, order):
    """Test that overlapping power recycling cavities in X and Y arms are structured
    correctly in the model trace forest."""
    IFO = aligo_model

    IFO.parse(
        """
    cav PRX PRM.p2 ITMX.p1.i
    cav PRY PRM.p2 ITMY.p1.i
    """
    )

    IFO.beam_trace(order=order)

    expect = [TraceTree.from_cavity(getattr(IFO, cav)) for cav in order]
    expect.reverse()

    # Arm cavities don't overlap with anything so will constitute
    # the first block of internal trace trees
    expect.insert(0, TraceTree.from_cavity(IFO.cavXARM))
    expect.insert(1, TraceTree.from_cavity(IFO.cavYARM))

    # Only really care about the internal trace trees, other
    # tests cover external forest structures
    for i in range(len(expect)):
        assert_trace_trees_equal(IFO.trace_forest.forest[i], expect[i])


@pytest.mark.parametrize("order", list(permutations(["SRX", "SRY"])))
def test_overlapping_srx_sry_forest(aligo_model: Model, order):
    """Test that overlapping signal recycling cavities in X and Y arms are structured
    correctly in the model trace forest."""
    IFO = aligo_model

    IFO.parse(
        """
    cav SRX SRM.p1 ITMX.p1.i
    cav SRY SRM.p1 ITMY.p1.i
    """
    )

    IFO.beam_trace(order=order)

    expect = [TraceTree.from_cavity(getattr(IFO, cav)) for cav in order]
    expect.reverse()

    # Arm cavities don't overlap with anything so will constitute
    # the first block of internal trace trees
    expect.insert(0, TraceTree.from_cavity(IFO.cavXARM))
    expect.insert(1, TraceTree.from_cavity(IFO.cavYARM))

    # Only really care about the internal trace trees, other
    # tests cover external forest structures
    for i in range(len(expect)):
        assert_trace_trees_equal(IFO.trace_forest.forest[i], expect[i])


@pytest.mark.parametrize("order", list(permutations(["SRX", "SRY", "PRX", "PRY"])))
def test_overlapping_all_recycling_cavs_forest(aligo_model: Model, order):
    """Test that overlapping both recycling cavities in X and Y arms are structured
    correctly in the model trace forest."""
    IFO = aligo_model

    IFO.parse(
        """
    cav SRX SRM.p1 ITMX.p1.i
    cav SRY SRM.p1 ITMY.p1.i
    cav PRX PRM.p2 ITMX.p1.i
    cav PRY PRM.p2 ITMY.p1.i
    """
    )
    IFO.remove("cavXARM")
    IFO.remove("cavYARM")

    IFO.beam_trace(order=order)

    expect = [TraceTree.from_cavity(getattr(IFO, cav)) for cav in order]
    expect.reverse()

    # Only really care about the internal trace trees, other
    # tests cover external forest structures
    for i in range(len(expect)):
        assert_trace_trees_equal(IFO.trace_forest.forest[i], expect[i])
