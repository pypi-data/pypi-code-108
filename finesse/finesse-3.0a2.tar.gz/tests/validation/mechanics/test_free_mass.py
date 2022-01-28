import pytest


@pytest.fixture
def kat(model):
    model.parse(
        """
        l l1 P=1
        s s1 l1.p1 m1.p1
        m m1 R=1 T=0
        free_mass m1_sus m1.mech mass=1

        sgen sig l1.amp.i 1 0

        ad adz m1.mech.z &fsig.f
        ad adF_z m1.mech.F_z &fsig.f

        fsig(1)
        """
    )
    return model


def test_amplitude(kat):
    sol = kat.run()
    from scipy.constants import c, pi

    P = kat.l1.P.value
    M = kat.m1_sus.mass.value
    w = 2 * pi * kat.fsig.f.value
    analytic = -2 * P / c * 1 / (-M * w ** 2)
    assert abs(sol["adz"] - analytic) < 1e-15
