import numpy as np

__all__ = ('SVD',)


class SVD:
    """
    Class that stores the singular value decomposition of a matrix X.
    This class can be used if the singular value decomposition of X can
    be re-used many times
    """

    def __init__(self):
        self._U = None  # Right unitary matrix
        self._Vh = None  # Left unititary matrix
        self._S = None  # Singular values

    @property
    def U(self) -> np.ndarray:
        return self._U

    @property
    def Vh(self) -> np.ndarray:
        return self._Vh

    @property
    def S(self) -> np.ndarray:
        return self._S

    def calculate(self, X: np.ndarray) -> None:
        """
        Calculate the SVD of the matrix X

        :param X: Matrix that should be decomposed
        """
        self._U, self._S, self._Vh = np.linalg.svd(X, full_matrices=False)

    def clear(self) -> None:
        """
        Set all stored matrices to None
        """
        self._U = None
        self._Vh = None
        self._S = None

    def has_matrices(self) -> bool:
        """
        Return True if matrices are stored in the attributes
        """
        return self._U is not None and self._Vh is not None and self._S is not None
