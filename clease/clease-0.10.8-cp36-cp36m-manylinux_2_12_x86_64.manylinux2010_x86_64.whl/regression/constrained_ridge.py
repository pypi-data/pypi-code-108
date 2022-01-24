from typing import Tuple
import numpy as np
from .regression import LinearRegression

__all__ = ('ConstrainedRidge',)


class ConstrainedRidge(LinearRegression):
    """
    Tikhonov regularized fitting scheme that supports linear
    constraints.

    :param alpha: Vector or matrix with the regularization
        parameters. If it is a vector, it is assumed that it
        corresponds to the diagonal of the Thikonov matrix.
        The length of the vector must be the same as the
        number of features to be fitted.
    """

    def __init__(self, alpha: np.ndarray):
        super().__init__()
        self.alpha = alpha
        if len(alpha.shape) == 1:
            self.alpha = np.diag(alpha)
        self._constraint = None

    def add_constraint(self, A: np.ndarray, c: np.ndarray) -> None:
        """
        Add a constraint to the system of equations A.dot(coeff) = c

        :param A: Matrix describing the linear system of equation
        :param c: Right hand side of the linear system of equations
        """
        self._constraint = {
            'A': A,
            'c': c,
        }

    def kkt_system(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Return the Karush-Kuhn-Tucker (KKT) system of equations. By solving
        the KKT system, one solves the problem

        minimize (X.dot(coeff) - y)^2 subject to A.dot(coeff) = c

        where A and c are set via `add_constraint`.

        The linear system of equations to be solved is given
        in block matrix form as

        | 2X^T.dot(X) + 2*alpha      A^T || coeff |   | 2X^T.dot(y) |
        |                                ||       | = |             |
        |         A                  0   ||  lamb |   |      c      |

        where coeff is the sought solution, and lamb is a set of Lagrange
        multipliers.
        """
        if self._constraint is None:
            return X.T.dot(X) + self.alpha, X.T.dot(y)

        A = self._constraint['A']
        zero = np.zeros((A.shape[0], A.shape[0]))
        matrix = np.block([[2.0 * X.T.dot(X) + self.alpha, A.T], [A, zero]])
        rhs = 2.0 * X.T.dot(y)
        rhs_constraint = self._constraint['c']
        return matrix, np.concatenate((rhs, rhs_constraint))

    def fit(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Find the least square solution to the X*coeff = y,
        where the coefficient satisfies eventual constraints
        attached. If no constraints are added, this is equivalent
        to normal Tikhonov regularized fit. In this case, it is
        recommended to use the Tikhonov scheme instead.

        :param X: Design matrix
        :param y: target values
        """
        matrix, rhs = self.kkt_system(X, y)
        coeff = np.linalg.solve(matrix, rhs)
        return coeff[:X.shape[1]]
