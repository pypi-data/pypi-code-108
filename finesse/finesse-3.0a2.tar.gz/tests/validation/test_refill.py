import pytest
import finesse
import numpy as np
import warnings
from finesse.warnings import CavityUnstableWarning


@pytest.fixture
def coupled_cavity():
    model = finesse.Model()
    model.parse(
        """
    laser l1 P=40
    m m1 T=0.04835 L=30u Rc=-1430.0 phi=90
    s s1 m1.p2 m2.p1 L=5.9399
    m m2 T=0.01377 L=27u Rc=-1424.6
    s s2 m2.p2 m3.p1 L=2999.8
    m m3 T=4.4u L=27u Rc=1790.0
    link(l1, m1)
    cav cav1 m1.p2.o
    cav cav2 m2.p2.o
    modes(even, maxtem=2)
    fd E1 m2.p1.o 0
    fd E2 m2.p2.o 0
    """
    )
    return model


@pytest.mark.parametrize(
    "param",
    [
        "m1.Rcx",
        "m1.Rcy",
        "m2.Rcx",
        "m2.Rcy",
        "m3.Rcx",
        "m3.Rcy",
        "s1.L",
        "s2.L",
        "m1.phi",
        "m2.phi",
        "m3.phi",
    ],
)
def test_change_param(coupled_cavity, param):
    """Ensure that changing some geometric parameters in a coupled cavity actually
    recomputes and solves correctly.

    Just checks that the numbers are actually different. during the axis sweep.
    """
    model = coupled_cavity.deepcopy()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        sol = model.run(f"xaxis({param}, lin, 0, 1, 1, True)")
    assert not np.allclose(sol["E1"][0], sol["E1"][1])
    assert not np.allclose(sol["E2"][0], sol["E2"][1])
