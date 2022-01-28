"""Tests that a mirror signal scatters HOM correctly."""
import pytest
import finesse
import numpy as np

P00 = 1
P01 = 100


@pytest.fixture
def sol():
    kat = finesse.Model()
    kat.parse(
        """
        fsig(1)
        l L0 P=1
        s s1 L0.p1 ITM.p1

        m ITM R=1 T=0

        sgen sig ITM.mech.z 1 0

        ad a ITM.p1.o 0 n=0 m=0
        ad b ITM.p1.o 0 n=0 m=1

        ad c ITM.p1.o &fsig.f n=0 m=0
        ad d ITM.p1.o &fsig.f n=0 m=1

        ad e ITM.p1.o -&fsig.f n=0 m=0
        ad f ITM.p1.o -&fsig.f n=0 m=1

        gauss g1 L0.p1.o z=0 w0=1e-3

        modes(maxtem=1)
        """
    )
    kat.L0.tem(0, 0, P00, 0)
    kat.L0.tem(0, 1, P01, 0)

    return kat.run()


def test_mech_z_scatter_HOM(sol):
    """Assert that the correct ratio of input carrier hom get scattered into signal
    sidebands."""
    assert abs(sol["a"] * np.sqrt(P01 / P00) - sol["b"]) < 1e-15
    assert abs(sol["c"] * np.sqrt(P01 / P00) - sol["d"]) < 1e-15
    assert abs(sol["e"] * np.sqrt(P01 / P00) - sol["f"]) < 1e-15

    assert abs(sol["c"] - sol["e"]) < 1e-15
