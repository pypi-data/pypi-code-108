import finesse
import numpy as np


def test_minimize_basic():
    # Test basic minimisation that uses nelder-mead arguments
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    pd P l1.p1.o
    minimize(P, l1.P)
    """
    )
    sol = model.run()
    assert sol.x < 1e-2


def test_minimize_basic_nelder_mead():
    # Test basic minimisation that uses nelder-mead arguments
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    pd P l1.p1.o
    minimize(P, l1.P, xatol=1e-6, adaptive=True)
    """
    )
    sol = model.run()
    assert sol.x < 1e-6


def test_minimize_RF_readout_phase():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    mod mod1 f=10M midx=0.1 mod_type=am
    link(l1, mod1)
    pd1 RF mod1.p2.o 10M 0
    minimize(RF, RF.phase, xatol=1e-6, adaptive=True)
    """
    )
    sol = model.run()
    # Max solution should be at 90 phase
    assert np.allclose(sol.x, 90, atol=1e-6)


def test_maximize_RF_readout_phase():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    mod mod1 f=10M midx=0.1 mod_type=am
    link(l1, mod1)
    pd1 RF mod1.p2.o 10M 0
    maximize(RF, RF.phase, xatol=1e-6, adaptive=True)
    """
    )
    sol = model.run()
    # Max solution should be at 0 phase
    assert np.allclose(sol.x, 0, atol=1e-6)


def test_maximize_multiple_targets():
    """Coupled cavity optimize."""
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    m m1 R=0.98 T=0.02 phi=10
    m m2 R=0.99 T=0.01
    m m3 R=1 T=0 phi=-20
    link(l1, m1, m2, m3)
    pd P m3.p1.i

    maximize(P, [m1.phi, m3.phi], xatol=1e-7, adaptive=True)
    """
    )
    sol = model.run()
    assert np.allclose(sol.x, [90, 0], atol=1e-6)


def test_bounds():
    model = finesse.Model()
    model.parse(
        """
    l l1
    l l2
    bs BS R=0.5 T=0.5
    link(l1, BS.p1)
    link(l2, BS.p4)
    pd P BS.p2.o
    """
    )

    sol = model.run(
        """
    series(
        maximize(P, [l1.P, l2.P, l1.phase], bounds=[[0,4], [0, 4], [-180, 180]]),
        noxaxis()
    )
    """
    )

    assert abs(sol["noxaxis"]["P"] - 8) < 1e-6
