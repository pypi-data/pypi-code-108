"""Tests checking that symbolic equations are set-up correctly during simulations."""

import numpy as np
from numpy.testing import assert_allclose
from finesse import Model


def test_mirror_refl_trns_self_ref():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    link(L0, ITM)
    m ITM R=1 T=1-&ITM.R

    pd refl ITM.p1.o
    pd trns ITM.p2.o

    xaxis(ITM.R, lin, 0, 1, 2)
    """
    )

    out = IFO.run()

    assert_allclose(out["refl"], np.array([0, 0.5, 1]))
    assert_allclose(out["trns"], np.array([1, 0.5, 0]))


def test_mirror_refl_trns_via_variable():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    link(L0, ITM)
    m ITM R=&v T=1-&v

    pd refl ITM.p1.o
    pd trns ITM.p2.o

    var v 1
    xaxis(v.value, lin, 0, 1, 2)
    """
    )

    out = IFO.run()

    assert_allclose(out["refl"], np.array([0, 0.5, 1]))
    assert_allclose(out["trns"], np.array([1, 0.5, 0]))
