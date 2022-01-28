import finesse.ligo
import pytest


def test_parse():
    model = finesse.Model()
    model.parse(finesse.ligo.aligo_katscript)


def test_run_aligo_noxaxis():
    model = finesse.Model()
    model.parse(finesse.ligo.aligo_katscript)
    model.run()


def test_SRC_PRC_length_symbols():
    model = finesse.Model()
    model.parse(finesse.ligo.aligo_katscript)
    path = model.path("PRM.p2.o", "ITMX.p1.i")
    LPRCX = sum(s.L * s.nr for s in path.spaces).eval()
    path = model.path("PRM.p2.o", "ITMY.p1.i")
    LPRCY = sum(s.L * s.nr for s in path.spaces).eval()
    assert (LPRCX + LPRCY) / 2 == model.lPRC.value.eval()

    path = model.path("SRM.p1.o", "ITMX.p1.i")
    LSRCX = sum(s.L * s.nr for s in path.spaces).eval()
    path = model.path("SRM.p1.o", "ITMY.p1.i")
    LSRCY = sum(s.L * s.nr for s in path.spaces).eval()
    assert (LSRCX + LSRCY) / 2 == model.lSRC.value.eval()


@pytest.mark.parametrize("RF_AS_readout", (True, False))
def test_make_model(RF_AS_readout):
    finesse.ligo.make_aligo(RF_AS_readout)


def test_locks():
    base = finesse.ligo.make_aligo()
    base.parse("run_locks()")
    base.run()


@pytest.mark.parametrize("L", (0.01, 0.05, 0.1))
def test_schnupp_length_experiment(L):
    """RF locks each arm and measures the optimal AS45 demodulation phase.

    From this back out the schnupp asymetry.
    """
    import numpy as np
    from finesse.ligo import DRFPMI_state
    from finesse.analysis.actions import Series, OptimiseRFReadoutPhaseDC

    base = finesse.ligo.make_aligo()
    base.lschnupp.value = L
    a = Series(
        DRFPMI_state("XARM"),
        OptimiseRFReadoutPhaseDC("XARM", "AS45", name="xarm"),
        DRFPMI_state("YARM"),
        OptimiseRFReadoutPhaseDC("YARM", "AS45", name="yarm"),
        DRFPMI_state("DRFPMI"),
    )
    sol = base.run(a)
    phase = np.deg2rad(sol["yarm"].phases["AS45"] - sol["xarm"].phases["AS45"])
    f = base.f2.value.eval()
    lmbda = 299792458 / f
    k = 2 * np.pi / lmbda
    schnupp = phase / k / 2
    assert abs(schnupp - base.lschnupp.value) < 1e-6
