import finesse
import pytest
from finesse.detectors import KnmDetector


@pytest.fixture()
def model_cavity():
    IFO = finesse.Model()
    IFO.parse(
        """
        l L0 P=3
        s s0 L0.p1 ITM.p1
        m ITM T=7m L=37.5u Rc=-5580
        s LY ITM.p2 ETM.p1 L=10k
        m ETM T=6u L=37.5u Rc=5580
        var dummy 6000
        cav ARM ITM.p2
        """
    )
    return IFO.deepcopy()


@pytest.mark.parametrize("mirror", ("ETM", "ITM"))
@pytest.mark.parametrize("direction", ("x", "y"))
@pytest.mark.parametrize("node1", (1, 2))
@pytest.mark.parametrize("node2", (1, 2))
@pytest.mark.parametrize("dummy", (True, False))
def test_ABCDs_xaxis_reset(model_cavity, mirror, direction, node1, node2, dummy):
    if dummy:
        # use dummy variable to scan RoCs instead
        model_cavity.ETM.Rcx = model_cavity.dummy.value.ref
        model_cavity.parse("xaxis(dummy.value, lin, 6000, 9000, 1)")
    else:
        model_cavity.parse("xaxis(ETM.Rcx, lin, 6000, 9000, 1)")

    model_cavity.ETM.Rcy = model_cavity.ETM.Rcx.ref
    model_cavity.ITM.Rcx = -1 * model_cavity.ETM.Rcx.ref
    model_cavity.ITM.Rcy = -1 * model_cavity.ETM.Rcx.ref

    m1 = model_cavity.elements[mirror].ABCD(node1, node2, direction=direction).copy()
    model_cavity.run()
    m2 = model_cavity.elements[mirror].ABCD(node1, node2, direction=direction).copy()
    assert (m1 == m2).all()


def test_cvalues_update_abcd(model_cavity):
    IFO = model_cavity
    IFO.ETM.Rcy = IFO.ETM.Rcx.ref
    IFO.ITM.Rcx = -1 * IFO.ETM.Rcx.ref
    IFO.ITM.Rcy = -1 * IFO.ETM.Rcx.ref
    IFO.parse("xaxis(ETM.Rcx, lin, 5580, 9000, 1)")
    IFO.add_matched_gauss(IFO.L0.p1.o, "gL0")
    IFO.add(KnmDetector("k00", IFO.ITM, "11", 0, 0, 0, 0))

    out1 = IFO.run()
    out2 = IFO.run()
    assert (out1["k00"] == out2["k00"]).all()


def test_cvalues_update_abcd_dummy_var(model_cavity):
    IFO = model_cavity
    IFO.ETM.Rcx = IFO.dummy.value.ref
    IFO.ETM.Rcy = IFO.dummy.value.ref
    IFO.ITM.Rcx = -1 * IFO.dummy.value.ref
    IFO.ITM.Rcy = -1 * IFO.dummy.value.ref
    IFO.parse("xaxis(dummy.value, lin, 5580, 9000, 1)")
    IFO.add_matched_gauss(IFO.L0.p1.o, "gL0")
    IFO.add(KnmDetector("k00", IFO.ITM, "11", 0, 0, 0, 0))

    out1 = IFO.run()
    out2 = IFO.run()
    assert (out1["k00"] == out2["k00"]).all()
