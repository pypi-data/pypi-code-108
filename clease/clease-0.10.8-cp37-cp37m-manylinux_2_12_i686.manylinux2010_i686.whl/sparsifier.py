from typing import List, Tuple

import numpy as np
from matplotlib import pyplot as plt

from clease.regression import LinearRegression
from clease.tools import aicc


class Sparsifier:
    """
    Sparsifier can be used to remove coefficicients that has very low values.
    """

    def __init__(self):
        self._aicc = []
        self._num_features = []

    def clear(self):
        """
        Clears all attributes
        """
        self._aicc = []
        self._num_features = []

    def sparsify(self, fitter: LinearRegression, X: np.ndarray,
                 y: np.ndarray) -> Tuple[List[int], np.ndarray]:
        """
        Remove the feature corresponding to the smallest coefficient
        iteratively. On each step, modified Afaike information
        crieterion is calculated (AICC). The features in the model
        with the smallest AICC is selected. This will favour models
        with fewer coefficients.

        Parameters:

        fitter:
            LinearRegression fitting scheme

        X:
            Design matrix of size (N x M) where N is the number of data points
            and M is the number of features

        y:
            Numpy array with the target values. The length must be N.

        Return:
            List with the index of the coefficient selected in the model with
            the lowest CV score and the coefficient array.

            Example:

            If the following is returned
            [0, 4, 8, 9], [0.1, 0.5, 0.8, -1.0]
            it means that feature no. 0, 4, 8 and 9 was selected. The
            coefficients corresponding to these features are returned in the
            second array. The coefficients of all other features in the model
            is zero.
        """
        self.clear()
        best_selection = None
        best_coeff = None
        best_afaike = None

        min_num_features = 2
        removed = []
        X_masked = X.copy()
        for _ in range(X.shape[1] - min_num_features + 1):
            mask = [j for j in range(X.shape[1]) if j not in removed]
            X_masked = X[:, mask]
            coeff = fitter.fit(X_masked, y)
            min_coeff = np.argmin(np.abs(coeff))
            removed.append(mask[min_coeff])

            pred = X_masked.dot(coeff)
            diff = pred - y
            mse = np.mean(diff**2)
            afaike_ic = aicc(mse, len(mask), len(y))

            self._aicc.append(afaike_ic)
            self._num_features.append(X.shape[1] - len(removed) + 1)

            if best_afaike is None or afaike_ic < best_afaike:
                best_coeff = coeff
                best_selection = mask
                best_afaike = afaike_ic

        return best_selection, best_coeff

    def plot(self):
        """
        Creates a plot of the CV score as function of the number of data points

        Returns: pyplot.Figure
            Figure object used to plot
        """
        if not self._aicc:
            raise RuntimeError("Nothing to plot. Call sparsify first.")

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self._num_features, self._aicc)
        ax.set_xlabel("Num. features")
        ax.set_ylabel("AICC")
        return fig
