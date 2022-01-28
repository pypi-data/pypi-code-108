# pylint: disable=no-member

"""Model path tracing tests."""

import pytest
from networkx.exception import NetworkXNoPath
from finesse.components import Beamsplitter, Laser, Mirror, Cavity
from finesse.detectors import PowerDetector


@pytest.fixture
def fabry_perot(model):
    """Fixture for constructing a Fabry-Perot cavity."""
    model.add([Laser("L0"), Mirror("ITM", Rc=-0.6), Mirror("ETM", Rc=0.6)])
    model.connect(model.L0.p1, model.ITM.p1)
    model.connect(model.ITM.p2, model.ETM.p1, L=1)
    model.add(Cavity("cav", model.ITM.p2.o, model.ITM.p2.i))
    model.add(PowerDetector("REFL", model.ITM.p1.o))

    return model


@pytest.fixture
def simple_michelson(model):
    """Fixture for constructing a simple Michelson interferometer."""
    model.add([Laser("L0"), Beamsplitter("BS"), Mirror("MX"), Mirror("MY")])
    model.connect(model.L0.p1, model.BS.p1)
    model.connect(model.BS.p2, model.MY.p1, L=1)
    model.connect(model.BS.p3, model.MX.p1, L=1)
    model.add(PowerDetector("AS", model.BS.p4.o))

    return model


def test_fullpath_laser_to_mirror(model):
    """Test path finding from a single laser to a single mirror."""
    model.add([Laser("L0"), Mirror("M")])
    model.connect(model.L0.p1, model.M.p1)

    # Transmitted through mirror.
    result_transmit = model.path(model.L0.p1.o, model.M.p2.o).data
    target_transmit = [
        (model.L0.p1.o, model.L0.p1.o.space),
        (model.M.p1.i, model.M),
        (model.M.p2.o, None),
    ]
    assert result_transmit == target_transmit

    # Reflected from mirror.
    result_reflect = model.path(model.L0.p1.o, model.M.p1.o).data
    target_reflect = [
        (model.L0.p1.o, model.L0.p1.o.space),
        (model.M.p1.i, model.M),
        (model.M.p1.o, model.L0.p1.o.space),
    ]
    assert result_reflect == target_reflect

    # Impossible path.
    with pytest.raises(NetworkXNoPath):
        model.path(model.L0.p1.o, model.M.p2.i)


def test_fullpath_fabry_perot(fabry_perot):
    """Test path finding from a single laser to a Fabry-Perot cavity."""
    # Transmitted through Fabry-Perot.
    result_transmit_all = fabry_perot.path(
        fabry_perot.L0.p1.o, fabry_perot.ETM.p2.o
    ).data
    target_transmit_all = [
        (fabry_perot.L0.p1.o, fabry_perot.L0.p1.o.space),
        (fabry_perot.ITM.p1.i, fabry_perot.ITM),
        (fabry_perot.ITM.p2.o, fabry_perot.ITM.p2.o.space),
        (fabry_perot.ETM.p1.i, fabry_perot.ETM),
        (fabry_perot.ETM.p2.o, None),
    ]
    assert result_transmit_all == target_transmit_all

    # Reflected back to ITM from ETM.
    result_half_roundtrip = fabry_perot.path(
        fabry_perot.L0.p1.o, fabry_perot.ITM.p2.i
    ).data
    target_half_roundtrip = [
        (fabry_perot.L0.p1.o, fabry_perot.L0.p1.o.space),
        (fabry_perot.ITM.p1.i, fabry_perot.ITM),
        (fabry_perot.ITM.p2.o, fabry_perot.ITM.p2.o.space),
        (fabry_perot.ETM.p1.i, fabry_perot.ETM),
        (fabry_perot.ETM.p1.o, fabry_perot.ETM.p1.o.space),
        (fabry_perot.ITM.p2.i, fabry_perot.ITM),
    ]
    assert result_half_roundtrip == target_half_roundtrip


def test_fullpath_fabry_perot_with_via_nodes(fabry_perot):
    """Test path finding from a single laser to a Fabry-Perot cavity via specified
    nodes."""
    # Full roundtrip.
    result_roundtrip = fabry_perot.path(
        fabry_perot.L0.p1.o, fabry_perot.ETM.p2.o, via_node=fabry_perot.ITM.p2.i
    ).data
    target_roundtrip = [
        (fabry_perot.L0.p1.o, fabry_perot.L0.p1.o.space),
        (fabry_perot.ITM.p1.i, fabry_perot.ITM),
        (fabry_perot.ITM.p2.o, fabry_perot.ITM.p2.o.space),
        (fabry_perot.ETM.p1.i, fabry_perot.ETM),
        (fabry_perot.ETM.p1.o, fabry_perot.ETM.p1.o.space),
        (fabry_perot.ITM.p2.i, fabry_perot.ITM),
        (fabry_perot.ITM.p2.o, fabry_perot.ITM.p2.o.space),
        (fabry_perot.ETM.p1.i, fabry_perot.ETM),
        (fabry_perot.ETM.p2.o, None),
    ]
    assert result_roundtrip == target_roundtrip

    # Reflection from ITM but via ETM.
    result_ITM_refl = fabry_perot.path(
        fabry_perot.L0.p1.o, fabry_perot.ITM.p1.o, via_node=fabry_perot.ETM.p1.i
    ).data
    target_ITM_refl = [
        (fabry_perot.L0.p1.o, fabry_perot.L0.p1.o.space),
        (fabry_perot.ITM.p1.i, fabry_perot.ITM),
        (fabry_perot.ITM.p2.o, fabry_perot.ITM.p2.o.space),
        (fabry_perot.ETM.p1.i, fabry_perot.ETM),
        (fabry_perot.ETM.p1.o, fabry_perot.ETM.p1.o.space),
        (fabry_perot.ITM.p2.i, fabry_perot.ITM),
        (fabry_perot.ITM.p1.o, fabry_perot.ITM.p1.o.space),
    ]
    assert result_ITM_refl == target_ITM_refl

    # Impossible path because of via node.
    with pytest.raises(NetworkXNoPath):
        fabry_perot.path(
            fabry_perot.L0.p1.o, fabry_perot.ITM.p1.o, fabry_perot.ETM.p2.i
        )


def test_fullpath_simple_michelson(simple_michelson):
    """Test path finding for a simple Michelson interferometer (no arm cavities)."""
    # Trace to end of XARM.
    result_XARM = simple_michelson.path(
        simple_michelson.L0.p1.o, simple_michelson.MX.p2.o
    ).data
    target_XARM = [
        (simple_michelson.L0.p1.o, simple_michelson.L0.p1.o.space),
        (simple_michelson.BS.p1.i, simple_michelson.BS),
        (simple_michelson.BS.p3.o, simple_michelson.BS.p3.o.space),
        (simple_michelson.MX.p1.i, simple_michelson.MX),
        (simple_michelson.MX.p2.o, None),
    ]
    assert result_XARM == target_XARM

    # Trace to end of YARM.
    result_YARM = simple_michelson.path(
        simple_michelson.L0.p1.o, simple_michelson.MY.p2.o
    ).data
    target_YARM = [
        (simple_michelson.L0.p1.o, simple_michelson.L0.p1.o.space),
        (simple_michelson.BS.p1.i, simple_michelson.BS),
        (simple_michelson.BS.p2.o, simple_michelson.BS.p2.o.space),
        (simple_michelson.MY.p1.i, simple_michelson.MY),
        (simple_michelson.MY.p2.o, None),
    ]
    assert result_YARM == target_YARM

    # Impossible path through beam splitter.
    with pytest.raises(NetworkXNoPath):
        simple_michelson.path(simple_michelson.MX.p1.o, simple_michelson.MY.p1.i)


def test_fullpath_simple_michelson_with_via_nodes(simple_michelson):
    """Test path finding for a simple Michelson interferometer using specified nodes."""
    # Trace to reflection port of IFO via YARM.
    result_IFO_refl = simple_michelson.path(
        simple_michelson.L0.p1.o,
        simple_michelson.BS.p1.o,
        via_node=simple_michelson.MY.p1.o,
    ).data
    target_IFO_refl = [
        (simple_michelson.L0.p1.o, simple_michelson.L0.p1.o.space),
        (simple_michelson.BS.p1.i, simple_michelson.BS),
        (simple_michelson.BS.p2.o, simple_michelson.BS.p2.o.space),
        (simple_michelson.MY.p1.i, simple_michelson.MY),
        (simple_michelson.MY.p1.o, simple_michelson.MY.p1.o.space),
        (simple_michelson.BS.p2.i, simple_michelson.BS),
        (simple_michelson.BS.p1.o, simple_michelson.BS.p1.o.space),
    ]
    assert result_IFO_refl == target_IFO_refl

    # Trace to AS port of IFO via XARM.
    result_AS = simple_michelson.path(
        simple_michelson.L0.p1.o,
        simple_michelson.BS.p4.o,
        via_node=simple_michelson.MX.p1.i,
    ).data
    target_AS = [
        (simple_michelson.L0.p1.o, simple_michelson.L0.p1.o.space),
        (simple_michelson.BS.p1.i, simple_michelson.BS),
        (simple_michelson.BS.p3.o, simple_michelson.BS.p3.o.space),
        (simple_michelson.MX.p1.i, simple_michelson.MX),
        (simple_michelson.MX.p1.o, simple_michelson.MX.p1.o.space),
        (simple_michelson.BS.p3.i, simple_michelson.BS),
        (simple_michelson.BS.p4.o, None),
    ]
    assert result_AS == target_AS
