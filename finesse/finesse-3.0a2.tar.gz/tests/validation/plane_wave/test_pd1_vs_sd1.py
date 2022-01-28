import pytest
import numpy as np


@pytest.fixture
def kat(model):
    model.parse(
        """
        l l1 P=1 phase=2.19571

        readout_dc REFL l1.p1.o

        pd1 REFL_DC1 l1.p1.o &fsig
        ad REFL_DC2 REFL.DC.o &fsig

        fsig(1)
        """
    )
    return model


def test_amp(kat):
    kat.parse("sgen DIFF l1.amp.i phase=10")
    sol = kat.run()
    assert np.allclose(sol["REFL_DC1"], sol["REFL_DC2"])
    assert np.allclose(abs(sol["REFL_DC1"]), 1)
    assert np.allclose(np.rad2deg(np.angle(sol["REFL_DC1"])), 10)


def test_frq(kat):
    kat.parse("sgen DIFF l1.frq.i phase=10")
    sol = kat.run()
    assert np.allclose(sol["REFL_DC1"], sol["REFL_DC2"])
    assert np.allclose(abs(sol["REFL_DC1"]), 0)


def test_phs(kat):
    kat.parse("sgen DIFF l1.phs.i phase=10")
    sol = kat.run()
    assert np.allclose(sol["REFL_DC1"], sol["REFL_DC2"])
    assert np.allclose(abs(sol["REFL_DC1"]), 0)
