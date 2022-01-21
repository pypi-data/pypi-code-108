from array import array
from typing import Sequence


def tridiag_solve(a: Sequence[float], b: Sequence[float], c: Sequence[float],
                  y: Sequence[float]) -> Sequence[float]:
    r"""
    Calculate the solution of a tridiagonal system of linear equations.
    Consider the linear system:

    .. math::
        \mathbf{M} \cdot \mathbf{x} = \mathbf{y}

    Where the matrix :math:`\mathbf{M}` is a tridiagonal matrix with the
    following form:

    .. math::
        \left( \begin{matrix}
        b_0 & c_0 &        &        &        &       0 \\
        a_1 & b_1 &    c_1 &        &        &         \\
            & a_2 &    b_2 &    c_2 &        &         \\
            &     & \ddots & \ddots & \ddots &         \\
            &     &        & a_{n-2}& b_{n-2}& c_{n-2} \\
          0 &     &        &        & a_{n-1}& b_{n-1}
        \end{matrix} \right)
        \cdot
        \left( \begin{matrix}
        x_0 \\
        x_1 \\
        x_2 \\
        \vdots \\
        x_{n-2}\\
        x_{n-1}
        \end{matrix} \right)
        =
        \left( \begin{matrix}
        y_0 \\
        y_1 \\
        y_2 \\
        \vdots \\
        y_{n-2}\\
        y_{n-1}
        \end{matrix} \right)

    Note that elements :math:`a_0` and :math:`c_{n-1}` are not used.

    This function returns the vector :math:`\mathbf{x}`.

    :param a: subdiagonal
    :param b: diagonal
    :param c: superdiagonal
    :param y: rhs
    :return: solution to the tridiagonal system
    """
    n = len(a)
    if len(b) != n or len(c) != n or len(y) != n:
        raise ValueError("All list arguments must have the same length:  "
                         "a.length=${a.length}, b.length=${b.length}, "
                         "c.length=${c.length}, y.length=${y.length}.")
    x = array('d', [0.0 for _ in range(n)])
    beta = b[0]
    u = array('d', [0.0 for _ in range(n)])
    if beta == 0.0:
        raise ValueError("algorithm encountered a zero value for b[0].")
    x[0] = y[0] / beta
    #  forward substitution
    for i in range(1, n):
        u[i] = c[i - 1] / beta
        beta = b[i] - a[i] * u[i]
        if beta == 0.0:
            raise ValueError("algorithm encountered a zero value for beta"
                             "while doing forward substitution.")
        x[i] = (y[i] - a[i] * x[i - 1]) / beta
    # backsubstitution.
    for i in range(n - 2, -1, -1):
        x[i] -= u[i + 1] * x[i + 1]
    return x
