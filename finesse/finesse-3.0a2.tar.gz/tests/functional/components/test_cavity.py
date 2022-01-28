"""Cavity unit tests."""

import pytest
from networkx.exception import NetworkXNoPath
from finesse import Model
from finesse.components import Cavity, Beamsplitter
from ...util import assert_cavities_equivalent


def mdl_triangular():
    """Triangular cavity model.

    NOTE: this isn't a @pytest.fixture because it's used multiple times in functions below.
    """
    m1 = Beamsplitter("m1", T=500e-6, L=0, Rc=12)
    m2 = Beamsplitter("m2", T=15e-6, L=0)
    m3 = Beamsplitter("m3", T=15e-6, L=0)
    model = Model()
    model.connect(m1.p1, m2.p2, L=6)
    model.connect(m2.p1, m3.p2, L=6)
    model.connect(m3.p1, m1.p2, L=6)
    return model


def test_choice_of_cavity_via_doesnt_matter():
    """Test that changing the via node to another node within the cavity makes no difference to \
    the computed cavity properties."""
    # Cavity without via.
    mdl_ref = mdl_triangular()
    cav_ref = Cavity("cav_ref", mdl_ref.m1.p1.o, mdl_ref.m1.p2.i)
    mdl_ref.add(cav_ref)

    # Cavities with vias.
    mdl_via1 = mdl_triangular()
    cav_via1 = Cavity("cav_via1", mdl_via1.m1.p1.o, via=mdl_via1.m2.p2.i)
    mdl_via1.add(cav_via1)
    mdl_via2 = mdl_triangular()
    cav_via2 = Cavity("cav_via2", mdl_via2.m1.p1.o, via=mdl_via2.m2.p1.o)
    mdl_via2.add(cav_via2)
    mdl_via3 = mdl_triangular()
    cav_via3 = Cavity("cav_via3", mdl_via3.m1.p1.o, via=mdl_via3.m3.p2.i)
    mdl_via3.add(cav_via3)
    mdl_via4 = mdl_triangular()
    cav_via4 = Cavity("cav_via4", mdl_via4.m1.p1.o, via=mdl_via4.m3.p1.o)
    mdl_via4.add(cav_via4)

    assert_cavities_equivalent(cav_ref, cav_via1)
    assert_cavities_equivalent(cav_ref, cav_via2)
    assert_cavities_equivalent(cav_ref, cav_via3)
    assert_cavities_equivalent(cav_ref, cav_via4)


def test_cavity_via_not_in_path_raises_exception():
    """Test that when a via node is specified that's not in the path, an exception is raised.

    See Also
    --------
    :func:`tests.unit.models.tracing.test_paths.test_optical_path_via_node_not_in_path_raises_exception`
    """

    # The used model connects m1.p1.o -> m2.p2.i, m2.p1.o -> m3.p2.i, m3.p1.o -> m1.p2.i.
    with pytest.raises(NetworkXNoPath):
        mdl = mdl_triangular()
        cav = Cavity("cav", mdl.m1.p1.o, via=mdl.m1.p1.i)
        mdl.add(cav)
    with pytest.raises(NetworkXNoPath):
        mdl = mdl_triangular()
        cav = Cavity("cav", mdl.m1.p1.o, via=mdl.m1.p3.i)
        mdl.add(cav)
    with pytest.raises(NetworkXNoPath):
        mdl = mdl_triangular()
        cav = Cavity("cav", mdl.m1.p1.o, via=mdl.m2.p2.o)
        mdl.add(cav)
    with pytest.raises(NetworkXNoPath):
        mdl = mdl_triangular()
        cav = Cavity("cav", mdl.m1.p1.o, via=mdl.m2.p4.o)
        mdl.add(cav)
