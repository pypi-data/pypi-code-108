"""Tests to check that changing the source node of a Cavity object results in same
eigenmode as measured from the same longitudinal plane."""


import pytest
from finesse import Model


@pytest.fixture()
def recycle_plus_arm():
    IFO = Model()
    IFO.parse(
        """
    variable nsilica 1.45
    variable Larm 3994
    variable Mloss 30u

    l L0 P=1
    link(L0, PRM)

    ###########################################################################
    ###   PRC
    ###########################################################################
    m PRM R=0 L=40u Rc=11.009
    s lp1 PRM.p2 PR2.p1 L=16.6107
    bs PR2 T=250u L=&Mloss alpha=-0.79 Rc=-4.545
    s lp2 PR2.p2 PR3.p1 L=16.1647
    bs PR3 T=0 L=&Mloss alpha=0.615 Rc=36.027
    s lp3 PR3.p2 BS.p1 L=19.5381

    ###########################################################################
    ###   BS
    ###########################################################################
    bs BS R=0.5 L=&Mloss alpha=45
    s BSsub1 BS.p3 BSAR1.p1 L=0.0687 nr=&nsilica
    s BSsub2 BS.p4 BSAR2.p2 L=0.0687 nr=&nsilica
    bs BSAR1 L=50u R=0 alpha=-29.195
    bs BSAR2 L=50u R=0 alpha=29.195

    ###########################################################################
    ###   Xarm
    ###########################################################################
    # Distance from beam splitter to X arm input mirror
    s lx1 BSAR1.p3 ITMXlens.p1 L=4.993
    lens ITMXlens f=34500
    s lx2 ITMXlens.p2 ITMXAR.p1
    m ITMXAR R=0 L=20u xbeta=&ITMX.xbeta ybeta=&ITMX.ybeta phi=&ITMX.phi
    s ITMXsub ITMXAR.p2 ITMX.p1 L=0.2 nr=&nsilica
    m ITMX T=0.014 L=&Mloss Rc=-1934

    s LX ITMX.p2 ETMX.p1 L=&Larm

    m ETMX T=5u L=&Mloss Rc=2245
    s ETMXsub ETMX.p2 ETMXAR.p1 L=0.2 nr=&nsilica
    m ETMXAR 0 500u xbeta=&ETMX.xbeta ybeta=&ETMX.ybeta phi=&ETMX.phi
    """
    )

    return IFO


def assert_trace_sols_equal(t1, t2):
    """Unordered equality of two BeamTraceSolution objects."""
    assert len(t1.keys()) == len(t2.keys())

    for node, data in t1.items():
        qx1, qy1 = data
        qx2, qy2 = t2[node]

        # Not using qx1 == qx2 here as the underlying ceq used by
        # BeamParam.__eq__ is quite strict
        assert qx1.z == pytest.approx(qx2.z, rel=1e-12)
        assert qy1.zr == pytest.approx(qy2.zr, rel=1e-12)


def test_arm_cavity_source_nodes(recycle_plus_arm: Model):
    """Test arm cavity traces equal when setting source node at either end."""
    IFO = recycle_plus_arm

    # Arm cavity with source node of ITMX.p2.o
    IFO.parse("cav cavXARM ITMX.p2")
    nodes1 = set(IFO.cavXARM.path.nodes_only)
    trace1 = IFO.cavXARM.trace_beam()

    IFO.remove("cavXARM")

    # Arm cavity with source node of ITMX.p2.o
    IFO.parse("cav cavXARM ETMX.p1")
    nodes2 = set(IFO.cavXARM.path.nodes_only)
    trace2 = IFO.cavXARM.trace_beam()

    assert nodes1 == nodes2
    assert_trace_sols_equal(trace1, trace2)


def test_recycle_cavity_source_nodes(recycle_plus_arm: Model):
    """Test recycling cavity traces equal when setting source node at either end.

    This also tests differing refractive indices at source nodes as using ITMX.p1 as
    source results in nr=nsilica at this node.
    """
    IFO = recycle_plus_arm

    # PRC with source node of PRM.p2
    IFO.parse("cav cavPRC PRM.p2 ITMX.p1.i")
    nodes1 = set(IFO.cavPRC.path.nodes_only)
    trace1 = IFO.cavPRC.trace_beam()

    IFO.remove("cavPRC")

    # PRC with source node of ITMX.p1
    IFO.parse("cav cavPRC ITMX.p1 PRM.p2.i")
    nodes2 = set(IFO.cavPRC.path.nodes_only)
    trace2 = IFO.cavPRC.trace_beam()

    assert nodes1 == nodes2
    assert_trace_sols_equal(trace1, trace2)
