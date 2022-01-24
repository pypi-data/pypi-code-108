from typing import Tuple
import numpy as np


class DataNormalizer:
    """
    Class for normalizing a data set to zero mean and unit variance

    Parameters:

    fail_on_constant: bool
        If True the normalizer will raise an error if a constant column
        is encountered. Otherwise, the standard deviation of these column
        will be set to 1.0
    """

    def __init__(self, fail_on_constant=False):
        self.meanX = None
        self.stdX = None
        self.meanY = None
        self.fail_on_constant = fail_on_constant

    def normalize(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Normalizes the each column of X to zero mean and unit variance. y is
        shifted to zero mean (variance is not altered)

        :param X: Design matrix shape (N x M)
        :param y: Target values length N

        Returns:
            X_norm, y_shifted (e.g. normalized X matrix and shifted y values)
        """
        self.meanY = np.mean(y)
        y_shifted = y - self.meanY
        self.meanX = np.mean(X, axis=0)
        self.stdX = np.std(X, axis=0, ddof=1)
        tol = 1e-16
        if np.any(self.stdX < tol) and self.fail_on_constant:
            raise ValueError(f"DataNormalizer: The following columns has a "
                             f"constant value:\n{self.constant_cols(X)}\n"
                             f"Please remove these.")
        self.stdX[self.stdX < tol] = 1.0
        X_norm = (X - self.meanX) / self.stdX
        return X_norm, y_shifted

    def constant_cols(self, X: np.ndarray, tol=1e-16) -> np.ndarray:
        """
        Return indices of columns in X that are constant

        Parameters:

        X: np.ndarray
            Design matrix for fitting

        tol: float
            Columns with a standard deviation smaller than this value are
            considered to be constant
        """
        # pylint: disable=no-self-use
        std = np.std(X, axis=0, ddof=1)
        return np.argwhere(std < tol)[:, 0]

    def varying_cols(self, X: np.ndarray, tol=1e-16) -> np.ndarray:
        """
        Return the indices of the columns that vary

        Parameters:

        X: np.ndarray
            Design matrix for fitting

        tol: float
            Columns with a standard deviation larger than this value are
            considered to be varying
        """
        # pylint: disable=no-self-use
        std = np.std(X, axis=0, ddof=1)
        return np.argwhere(std >= tol)[:, 0]

    def convert(self, coeff: np.ndarray) -> np.ndarray:
        """
        Converts coefficients obtained via X_norm.dot(coeff) = y_shifted to
        the ones that would have been obtained via X.dot(coeff) = y. Consult,
        the normalize function for an in depth explination of the difference
        between X_norm and X.

        Parameter:

        coeff: np.ndarray
            Array of coefficients obtained by using a normalized design matrix
            during fitting.

        Returns:
            converted coefficients
        """
        return coeff / self.stdX

    def bias(self, coeff: np.ndarray) -> float:
        """
        Return the bias term.
        """
        return self.meanY - np.sum(coeff * self.meanX / self.stdX)
