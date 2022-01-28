import pytest
import finesse
from finesse.exceptions import FinesseException


@pytest.mark.parametrize("A", ("l1", "l1.p1"))
@pytest.mark.parametrize("B", ("PD", "PD.p1"))
@pytest.mark.parametrize("name", (None, "s1"))
def test_connect_optical_optical(A, B, name):
    """Each of these inputs should connect optical to optical ports by default."""
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    readout_dc PD
    """
    )
    model.connect(A, B, name=name)
    if name is None:
        s = model.spaces.l1_p1__PD_p1
    else:
        s = model.s1

    assert s.portA == model.l1.p1
    assert s.portB == model.PD.p1


def test_connect_no_optical_port_left():
    model = finesse.Model()

    model.parse(
        """
    l l1 P=1
    readout_dc PD
    link(l1, PD)
    """
    )
    # There should be no optical ports left for link to connect here
    with pytest.raises(FinesseException):
        model.connect("l1", "PD")


@pytest.mark.parametrize("A", ("l1.amp", "l1.frq", "l1.phs"))
@pytest.mark.parametrize("B", ("PD.DC",))
@pytest.mark.parametrize("name", (None, "w1"))
def test_connect_elecrical(A, B, name):
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    readout_dc PD
    link(l1, PD)
    """
    )
    model.connect(A, B, name=name)
    if name is None:
        _A = model.get(A)
        _B = model.get(B)
        compA = _A.component.name
        compB = _B.component.name
        w = model.get(f"wires.{compA}_{_A.name}__{compB}_{_B.name}")
    else:
        w = model.get(name)

    assert w.nodeA == model.get(A).i
    assert w.nodeB == model.PD.DC.o


@pytest.fixture
def laser_mirror_readout_feedback():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    m m1
    readout_dc PD
    zpk ZPK [] []
    link(l1, m1, PD, PD.DC, ZPK, l1.amp)
    """
    )
    return model


def test_link_components(laser_mirror_readout_feedback):
    model = laser_mirror_readout_feedback
    path = model.path("l1.p1", "PD.p1")
    assert path.nodes_only == [
        model.l1.p1.o,
        model.m1.p1.i,
        model.m1.p2.o,
        model.PD.p1.i,
    ]
