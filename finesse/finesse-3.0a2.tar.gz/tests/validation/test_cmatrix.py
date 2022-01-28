from finesse.cmatrix import KLUMatrix
import numpy as np
from scipy.sparse import random
import pytest


def test_fill_za_zmvc():
    M = KLUMatrix("M")
    M.declare_equations(3, 0, "a")
    M.declare_equations(3, 1, "b")
    M.declare_equations(1, 2, "c")

    Vac = M.declare_submatrix_view(0, 2, "a->c", False)
    Vbc = M.declare_submatrix_view(1, 2, "b->c", True)

    Vca = M.declare_submatrix_view(2, 0, "c->a", False)
    Vcb = M.declare_submatrix_view(2, 1, "c->b", True)

    M.construct()

    I = np.array([[1, 2j, 3], [4, 5, 6j], [7, 8j, 9]], dtype=np.complex128)
    V = np.array([1, 2j, 3], dtype=np.complex128)

    Vac.do_fill_za_zmvc(3j, I, V)
    assert (abs(Vac.view - 3j * (I @ V.conj())) < 1e-15).all()

    Vbc.do_fill_za_zmvc(3j, I, V)
    assert (abs(Vbc.view - (3j * I @ V.conj()).conj()) < 1e-15).all()

    Vca.do_fill_za_zmvc(3j, I, V)
    assert (abs(Vca.view.T - 3j * I @ V.conj()) < 1e-15).all()

    Vcb.do_fill_za_zmvc(3j, I, V)
    assert (abs(Vcb.view.T - (3j * I @ V.conj()).conj()) < 1e-15).all()


@pytest.mark.parametrize("conj", (True, False))
@pytest.mark.parametrize("incr", (True, False))
@pytest.mark.parametrize("rhs_value", (1, 4j + 3))
def test_sparse_do_fill_prop_za_zm(conj, incr, rhs_value):
    M = KLUMatrix("M")
    M.declare_equations(3, 0, "a")
    M.declare_equations(3, 1, "b")
    M.declare_equations(1, 2, "c")

    Vac = M.declare_submatrix_view(0, 2, "a->c", False)
    Vbc = M.declare_submatrix_view(1, 2, "b->c", True)
    Vab = M.declare_submatrix_view(0, 1, "a->b", False)
    Vca = M.declare_submatrix_view(2, 0, "c->a", conj)
    Vcb = M.declare_submatrix_view(2, 1, "c->b", True)

    M.construct()

    I = np.array([[1, 2j, 3], [4, 5, 6j], [7, 8j, 9]], dtype=np.complex128)
    V = np.array([1, 2j, 3], dtype=np.complex128)

    Vac.do_fill_za_zmvc(3j, I, V)
    Vbc.do_fill_za_zmvc(3j, I, V)
    Vcb.do_fill_za_zmvc(3j, I, V)

    M.clear_rhs()
    for i in range(7):
        M.set_rhs(i, rhs_value, 0)

    M.factor()
    M.solve()

    for i in range(3):
        Vab[:] = random(3, 3, dtype=complex, density=1).todense()
        a = 3.1 + 1j
        m = random(3, 3, dtype=complex, density=1).todense()

        if incr:
            if conj:
                Vca[:] = np.conj(-np.atleast_2d(m[:, 0]))
            else:
                Vca[:] = -np.atleast_2d(
                    m[:, 0]
                )  # this does a negtive set behind the scenes

        Vca.do_fill_prop_za_zm(Vab, 0, a, m, incr)

        if incr:
            if conj:
                assert np.allclose(
                    Vca[:],
                    np.atleast_2d(m[:, 0])
                    + np.conj(m @ (a * Vab[:] @ np.atleast_2d(Vab.from_rhs_view).T)),
                    atol=1e-14,
                )
            else:
                assert np.allclose(
                    Vca[:],
                    np.atleast_2d(m[:, 0])
                    + m @ (a * Vab[:] @ np.atleast_2d(Vab.from_rhs_view).T),
                    atol=1e-14,
                )
        else:
            if conj:
                assert np.allclose(
                    Vca[:],
                    np.conj(m @ (a * Vab[:] @ np.atleast_2d(Vab.from_rhs_view).T)),
                    atol=1e-14,
                )
            else:
                assert np.allclose(
                    Vca[:],
                    m @ (a * Vab[:] @ np.atleast_2d(Vab.from_rhs_view).T),
                    atol=1e-14,
                )
