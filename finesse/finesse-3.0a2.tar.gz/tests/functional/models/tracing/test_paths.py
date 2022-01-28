# pylint: disable=no-member

"""Model path tests."""

import pytest
from networkx.exception import NetworkXNoPath
from finesse.components import Laser, Mirror, Beamsplitter


def test_optical_path_lengths(model):
    """Test path lengths are the sum of the lengths of its spaces."""
    l1 = Laser("lsr")
    m1 = Mirror("m1")
    m2 = Mirror("m2")
    m3 = Mirror("m3")
    model.chain(l1, 0.5, m1, 3.25, m2, 10.5, m3)
    path = model.path(l1.p1.o, m3.p1.i)
    assert path.length == 14.25


def test_optical_path_lengths__non_unity_nr(model):
    """Test path lengths account for index of refraction."""
    l1 = Laser("lsr")
    m1 = Mirror("m1")
    m2 = Mirror("m2")
    m3 = Mirror("m3")
    model.chain(l1, {"L": 3.0, "nr": 1.5}, m1, 3.25, m2, {"L": 10.5, "nr": 2}, m3)
    path = model.path(l1.p1.o, m3.p1.i)
    assert path.length == 10.5


def test_optical_path_via_node_not_in_path_raises_exception(model):
    """Test that specifying a via not on the path causes an exception."""
    # Triangular cavity with each beamsplitter's p1/p2 sides connected.
    m1 = Beamsplitter("m1", T=500e-6, L=0, Rc=12)
    m2 = Beamsplitter("m2", T=15e-6, L=0)
    m3 = Beamsplitter("m3", T=15e-6, L=0)
    model.connect(m1.p1, m2.p2, L=6)
    model.connect(m2.p1, m3.p2, L=6)
    model.connect(m3.p1, m1.p2, L=6)

    # m1
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m1.p1.i)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m1.p3.i)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m1.p3.o)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m1.p4.i)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m1.p4.o)
    # m2
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m2.p1.i)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m2.p2.o)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m2.p3.i)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m2.p3.o)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m2.p4.i)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m2.p4.o)
    # m3
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m3.p1.i)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m3.p2.o)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m3.p3.i)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m3.p3.o)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m3.p4.i)
    with pytest.raises(NetworkXNoPath):
        model.path(m1.p1.o, m1.p2.i, via_node=m3.p4.o)
