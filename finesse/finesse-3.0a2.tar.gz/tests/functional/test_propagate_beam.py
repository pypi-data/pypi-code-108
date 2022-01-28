"""Tests on propagate_beam tracing tools function, using a model of the aLIGO PRX + XARM
cavities."""

from functools import reduce
import numpy as np
from numpy.testing import assert_allclose
import pytest
from finesse import Model
from finesse.components import Gauss
from finesse.gaussian import BeamParam
from finesse.symbols import evaluate
from finesse.utilities import pairwise


@pytest.fixture()
def aligo_prx_model():
    ifo = Model()
    ifo.parse(
        """
        variable nsilica 1.45
        variable Mloss 30u
        variable Larm 3994

        ###   laser
        ###########################################################################
        # Laser and input optics
        laser L0 P=125
        link(L0, PRMAR)

        ###########################################################################
        ###   PRC
        ###########################################################################
        m PRMAR R=0 L=40u xbeta=&PRM.xbeta ybeta=&PRM.ybeta phi=&PRM.phi
        s sPRMsub1 PRMAR.p2 PRM.p1 L=0.0737 nr=&nsilica
        m PRM T=0.03 L=8.5u Rc=11.009
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

        ################
        ### Cavities ###
        ################

        cav cavXARM ITMX.p2
        cav cavPRX PRM.p2 ITMX.p1.i
        """
    )

    return ifo


@pytest.mark.parametrize(
    "start,end",
    (
        ("PRM.p2.o", "ITMX.p1.i"),
        ("PRM.p2", "ETMX.p1"),
        ("L0.p1", "ITMXlens.p2.o"),
        ("PR3.p1.i", "BS.p1"),
    ),
)
@pytest.mark.parametrize("use_path", (True, False))
def test_start_end_nodes(aligo_prx_model: Model, start, end, use_path):
    """Test path creation in propagate_beam via start and end node checking."""
    ifo = aligo_prx_model
    if use_path:
        beam = ifo.propagate_beam(path=ifo.path(start, end))
    else:
        beam = ifo.propagate_beam(start, end)

    # Expect start ports to default to output node...
    if start.count(".") == 1:
        start += ".o"
    # ... and end ports to input node.
    if end.count(".") == 1:
        end += ".i"

    start = ifo.get(start)
    end = ifo.get(end)

    assert beam.start_node is start
    assert beam.end_node is end


@pytest.mark.parametrize("use_path", (True, False))
def test_same_start_end_node_raises_exception(aligo_prx_model: Model, use_path):
    """Test that attempting to use same start and end node for propagate_beam call
    raises an exception."""
    ifo = aligo_prx_model

    with pytest.raises(ValueError):
        if use_path:
            ifo.propagate_beam(path=ifo.path(ifo.PRM.p2.o, ifo.PRM.p2.o))
        else:
            ifo.propagate_beam(ifo.PRM.p2.o, ifo.PRM.p2.o)


@pytest.mark.parametrize(
    "start,end",
    (("PRM.p2.o", "ITMX.p1.i"), ("ITMX.p2.i", "PRM.p2"), ("L0.p1", "ITMXlens.p2.o")),
)
@pytest.mark.parametrize(
    "enable_only", [("cavXARM", "cavPRX"), ("cavXARM",), ("cavPRX",)]
)
@pytest.mark.parametrize("direction", ("x", "y"))
def test_default_qin(aligo_prx_model: Model, start, end, enable_only, direction):
    """Test that specifying no input q uses the correct beam parameter for given start
    node."""
    ifo = aligo_prx_model
    beam = ifo.propagate_beam(start, end, enable_only=enable_only, direction=direction)
    trace = ifo.beam_trace(enable_only=enable_only)

    # Expect start ports to default to output node
    if start.count(".") == 1:
        start += ".o"

    start = ifo.get(start)

    assert getattr(trace[start], f"q{direction}") == beam.q(beam.start_node)


@pytest.mark.parametrize(
    "start,end",
    (
        ("PRM.p2.o", "ITMX.p1.i"),
        ("ITMX.p2.i", "PRM.p2"),
        ("L0.p1", "ITMXlens.p2.o"),
        ("PR3.p2.o", "BS.p1.i"),
    ),
)
@pytest.mark.parametrize("direction", ("x", "y"))
@pytest.mark.parametrize("symbolic", (True, False))
def test_composite_abcd(aligo_prx_model: Model, start, end, direction, symbolic):
    """Test 'composite' ABCD matrices computed by propagate_beam."""
    ifo = aligo_prx_model
    beam = ifo.propagate_beam(start, end, direction=direction, symbolic=symbolic)

    # Collect the individual ABCD matrices of each component
    abcds = []
    for n1, n2 in pairwise(beam.nodes):
        abcd = ifo.ABCD(n1, n2, direction=direction, symbolic=symbolic).M
        abcds.append(evaluate(abcd))

    # And compute the full matrix on these
    expect_abcd = reduce(np.dot, reversed(abcds))

    assert_allclose(evaluate(beam.full_ABCD), expect_abcd)


@pytest.mark.parametrize(
    "start,end",
    (
        ("PRM.p2.o", "ITMX.p1.i"),
        ("ITMX.p1", "PRM.p2"),
        ("L0.p1", "ITMXlens.p2.o"),
        ("PR3.p2.o", "BS.p1.i"),
    ),
)
@pytest.mark.parametrize("direction", ("x", "y"))
@pytest.mark.parametrize("symbolic", (True, False))
def test_accumulated_gouy_phases(
    aligo_prx_model: Model, start, end, direction, symbolic
):
    """Test Gouy phases accumulated over specified paths computed via propagate_beam,
    against result from simulation using Gouy detector."""
    ifo = aligo_prx_model
    beam = ifo.propagate_beam(start, end, direction=direction, symbolic=symbolic)
    startn = start.replace(".", "_")
    endn = end.replace(".", "_")
    ifo.parse(
        f"gouy acc_gouy_{startn}_{endn} from_node={start} to_node={end} direction={direction}"
    )
    out = ifo.run()

    assert evaluate(beam.total_acc_gouy) == pytest.approx(
        out[f"acc_gouy_{startn}_{endn}"]
    )


@pytest.mark.parametrize(
    "cutoff,node",
    (
        ("PR2", "PR2.p1.i"),
        ("PR3", "PR3.p1.i"),
        ("BS", "BS.p1.i"),
        ("BSAR1", "BSAR1.p1.i"),
        ("ITMXlens", "ITMXlens.p1.i"),
        ("ITMX", "ITMX.p1.i"),
    ),
)
@pytest.mark.parametrize("direction", ("x", "y"))
def test_accumulated_gouy_phases__cut_off(
    aligo_prx_model: Model, cutoff, node, direction
):
    """Test Gouy phases accumulated over specified paths computed via propagate_beam, up
    to a specific cut-off component, against result from simulation using Gouy
    detector."""
    ifo = aligo_prx_model
    beam = ifo.propagate_beam("PRM.p2", "ITMX.p1", direction=direction)
    ifo.parse(
        f"gouy acc_gouy_{cutoff} from_node=PRM.p2 to_node={node} direction={direction}"
    )
    out = ifo.run()

    assert beam.acc_gouy_up_to(cutoff) == pytest.approx(out[f"acc_gouy_{cutoff}"])


@pytest.mark.parametrize(
    "start,end",
    (
        ("PRM.p2.o", "ITMX.p1.i"),
        ("ITMX.p1", "PRM.p2"),
        ("L0.p1", "ITMXlens.p2.o"),
        ("PR3.p2.o", "BS.p1.i"),
    ),
)
@pytest.mark.parametrize("direction", ("x", "y"))
def test_all_node_qs__same_cav(aligo_prx_model: Model, start, end, direction):
    """Test the beam parameters at all nodes of the propagation solution are correct,
    where the start and end nodes of the propagate_beam call are in the same cavity
    path."""
    ifo = aligo_prx_model
    beam = ifo.propagate_beam(start, end, direction=direction)
    qs = beam.qs
    trace = ifo.beam_trace()

    for node, q in qs.items():
        assert q == getattr(trace[node], f"q{direction}")


@pytest.mark.parametrize(
    "start,end", (("PRM.p2.o", "ETMX.p1.i"), ("ITMX.p2.i", "PRM.p2"))
)
@pytest.mark.parametrize("direction", ("x", "y"))
def test_all_node_qs__diff_cav(aligo_prx_model: Model, start, end, direction):
    """Test the beam parameters at all nodes of the propagation solution are correct,
    where the start and end nodes of the propagate_beam call are in different cavity
    paths --- only the cavity associated with start node should then be enabled."""
    ifo = aligo_prx_model
    beam = ifo.propagate_beam(start, end, direction=direction)
    qs = beam.qs

    start_node = ifo.get(start)
    # Get the cavity associated with the start node and only
    # enable this for the beam trace
    cav = None
    for cav in ifo.cavities:
        if start_node in cav.path.nodes_only:
            cav = cav
            break

    assert cav is not None

    trace = ifo.beam_trace(enable_only=cav)

    for node, q in qs.items():
        assert q == getattr(trace[node], f"q{direction}")


@pytest.mark.parametrize("qin", (7 + 5j, 6.52 + 7.1j, 5.31j))
@pytest.mark.parametrize("direction", ("x", "y"))
def test_all_node_qs__custom_qin(aligo_prx_model: Model, qin, direction):
    """Test the beam parameters at all nodes of the propagation solution are correct,
    where a custom input beam parameter is set."""
    ifo = aligo_prx_model

    beam = ifo.propagate_beam("PRM.p2", "ETMX.p1", q_in=qin, direction=direction)
    qs = beam.qs

    # Set a Gauss at PRM.p2.o using custom qin
    ifo.add(Gauss("gPRM2o", ifo.PRM.p2.o, q=qin))
    trace = ifo.beam_trace(enable_only="gPRM2o")

    for node, q in qs.items():
        assert q == getattr(trace[node], f"q{direction}")


@pytest.mark.parametrize(
    "start,end",
    (
        ("PRM.p2.o", "ITMX.p1.i"),
        ("ITMX.p1", "PRM.p2"),
        ("L0.p1", "ITMXlens.p2.o"),
        ("PR3.p2.o", "BS.p1.i"),
    ),
)
@pytest.mark.parametrize("symbolic", (True, False))
def test_astigmatic_propagation_overlaps(aligo_prx_model: Model, start, end, symbolic):
    """Test that overlaps between tangential and sagittal plane beam parameters are
    correct when using propagate_beam_astig function."""
    ifo = aligo_prx_model
    beam = ifo.propagate_beam_astig(start, end, symbolic=symbolic)
    overlaps = beam.overlaps
    trace = ifo.beam_trace()

    for node, Ov in overlaps.items():
        assert evaluate(Ov) == pytest.approx(BeamParam.overlap(*trace[node]))
