import finesse
import pytest


@pytest.fixture
def coupled_cavity_input_telescope():
    model = finesse.Model()
    model.parse(
        """
    laser l1 P=40
    bs bs1 Rc=[inf, &bs1.Rcx]
    bs bs2 Rc=[inf, &bs2.Rcx]
    bs bs3 Rc=[inf, &bs3.Rcx]
    m m1 T=0.04835 L=30u Rc=[-1430.0, &m1.Rcx]
    s s1 m1.p2 m2.p1 L=5.9399
    m m2 T=0.01377 L=27u Rc=[-1424.6, &m2.Rcx]
    s s2 m2.p2 m3.p1 L=2999.8
    m m3 T=4.4u L=27u Rc=[1790.0, &m3.Rcx]
    link(l1,bs1,bs2,bs3,m1)
    cav cav1 m1.p2.o
    cav cav2 m2.p2.o
    gauss g1 bs1.p2.i w0=1 z=0
    modes(even, maxtem=0)
    """
    )
    return model


def test_flag_changing_q_nodes_m3_change(coupled_cavity_input_telescope):
    model = coupled_cavity_input_telescope.deepcopy()
    model.beam_trace()
    model.m3.Rcx.is_tunable = True
    found = model.trace_forest.get_nodes_with_changing_q()
    # cav2 and end mirror should be found as changing
    correct_nodes = set(model.cav2.path.nodes_only + list(model.m3.p2.nodes))
    assert found == correct_nodes


def test_flag_changing_q_nodes_m2_change(coupled_cavity_input_telescope):
    model = coupled_cavity_input_telescope.deepcopy()
    model.beam_trace()
    model.m2.Rcx.is_tunable = True
    found = model.trace_forest.get_nodes_with_changing_q()
    # If we change m2 then cav1 and cav2 change, as well as the nodes from cav1
    # all the way to the p2 and p4 on bs2. p1 an p3 on bs2 are set by the gauss
    correct_nodes = set(model.optical_nodes) - set(
        list(model.bs2.p1.nodes)
        + list(model.bs2.p3.nodes)
        + list(model.bs1.optical_nodes)
        + list(model.l1.optical_nodes)
    )
    assert found == correct_nodes


def test_flag_changing_q_nodes_m1_change(coupled_cavity_input_telescope):
    model = coupled_cavity_input_telescope.deepcopy()
    model.beam_trace()
    model.m1.Rcx.is_tunable = True
    found = model.trace_forest.get_nodes_with_changing_q()
    correct_nodes = set(model.optical_nodes) - set(
        list(model.bs2.p1.nodes)
        + list(model.bs2.p3.nodes)
        + list(model.bs1.optical_nodes)
        + list(model.l1.optical_nodes)
        + model.cav2.path.nodes_only
        + list(model.m3.optical_nodes)
    )
    assert found == correct_nodes
