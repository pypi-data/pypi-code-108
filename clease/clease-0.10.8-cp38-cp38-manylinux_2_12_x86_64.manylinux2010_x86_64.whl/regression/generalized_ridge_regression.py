import logging
import numpy as np
from scipy.optimize import minimize

from .regression import LinearRegression

logger = logging.getLogger(__name__)

__all__ = ('EigenDecomposition', 'GeneralizedRidgeRegression')


class EigenDecomposition:

    def __init__(self) -> None:
        self.eigvals = None
        self.eigvec = None

    def decompose(self, X: np.ndarray) -> None:
        """
        Performs eigen decomposition of a symmetric matrix X
        """
        self.eigvals, self.eigvec = np.linalg.eigh(X)


class GeneralizedRidgeRegression(LinearRegression):
    """
    GeneralizedRidgeRegression performs a ridge regression where each feature
    has its own penalization term. The optimimal value for each penalization
    coefficient is optimed by minimizing the generalized CV score. The method
    is based on the ideas presented in

    Golub, G.H., Heath, M. and Wahba, G., 1979.
    Generalized cross-validation as a method for choosing a good ridge
    parameter. Technometrics, 21(2), pp.215-223.

    :param alpha: Initial guess for the penalization parameters. If not
        given, the initial guess will be set to zero for all coefficients.
        Internally, a local optimization method is used to find the optimal
        penalization values. Thus, in case there are multiple local minima
        (which it normally is), the result from fit may vary when different
        initial guesses for alpha is provided.
    """

    def __init__(self, alpha: np.ndarray = None) -> None:
        super().__init__()
        self.alpha = alpha

        # Dictionary that will be populated with results from the
        # hyperparameter optimization
        self.opt_result = {}

        # Dictionary that is unpacked and passed to scipy.optimize.minimize
        # (e.g. minimize(**self.minimize_args)). See doc of
        # scipy.optimize.minimize for a detailed description of possible
        # options
        self.minimize_args = {}

    @staticmethod
    def _A(X: np.ndarray, eigen: EigenDecomposition, alpha: np.ndarray) -> np.ndarray:
        """
        Helper method to form the matrix
        X(X^TX + N*diag(alpha))^{-1}X^T, where N
        is the number of rows in X

        :param X: Design matrix
        :param eigen: Eigen decomposition of X^TX
        :param alpha: Vector with penalization values
        """
        N = X.shape[0]
        return np.linalg.multi_dot(
            [X, eigen.eigvec,
             np.diag(1.0 / (eigen.eigvals + N * alpha)), eigen.eigvec.T, X.T])

    def _coeff(self, X: np.ndarray, y: np.ndarray, eigen: EigenDecomposition) -> np.ndarray:
        """
        Calculate the coefficients using self.alpha as regularization

        :param X: Design matrix
        :param y: Target values
        :param eigen: Eigen decomposition of X^TX
        """
        N = X.shape[0]
        return np.linalg.multi_dot(
            [eigen.eigvec,
             np.diag(1.0 / (eigen.eigvals + N * self.alpha)), eigen.eigvec.T, X.T, y])

    @staticmethod
    def _grad_A(X: np.ndarray, eigen: EigenDecomposition, alpha: np.ndarray,
                component: int) -> np.ndarray:
        """
        Return a matrix representing the gradient of the A matrix.
        See the `_A` method.

        :param X: Design matrix
        :param eigen: Eigen decomposition of X^TX
        :param alpha: Vector with penalization value
        :param component: Integer specifying which component of
            the gradient that should be calculated
        """
        N = X.shape[0]
        XdotP = np.dot(X, eigen.eigvec[:, component])
        weight = N / (eigen.eigvals[component] + N * alpha[component])**2
        return -np.outer(XdotP, XdotP.T) * weight

    def _gcv_squared(self, alpha: np.ndarray, X: np.ndarray, y: np.ndarray,
                     eigen: EigenDecomposition) -> float:
        """
        Return the generalized CV score of a fit

        :param alpha: Vector of length M with regularization parameters
        :param X: Design matrix (N x M)
        :param y: Target values of length N
        :param eigen: EigenDecomposition of X^TX
        """
        A = self._A(X, eigen, alpha)
        N = len(y)
        mse = np.mean((y - A.dot(y))**2)
        denum = (1.0 - np.trace(A) / N)**2
        return mse / denum

    def _grad_gcv_squared(self, alpha: np.ndarray, X: np.ndarray, y: np.ndarray,
                          eigen: EigenDecomposition) -> np.ndarray:
        """
        Return the gradient of the squared generalized CV score.

        :param alpha: Vector of length M with regularization parameters
        :param X: Design matrix (N x M)
        :param y: Target values of length N
        :param eigen: EigenDecomposition of X^TX
        """
        num_alpha = len(alpha)
        grad = np.zeros(num_alpha)
        A = self._A(X, eigen, alpha)
        dev = y - A.dot(y)
        mse = np.mean(dev**2)
        N = len(y)
        denum = (1.0 - np.trace(A) / N)
        for i in range(num_alpha):
            gradA = self._grad_A(X, eigen, alpha, i)
            new_grad = -2.0 * np.sum(np.outer(dev, y) * gradA) / (N * denum**2)

            # There is an additional contribution for the diagonal terms
            # in gradA
            new_grad += 2.0 * mse * np.trace(gradA) / (N * denum**3)
            grad[i] = new_grad
        return grad

    def fit(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Fit X*coeff = y. The hyper parameters are optimized internally.

        :param X: Design matrix
        :param y: Target values
        """
        if self.alpha is None:
            self.alpha = np.zeros(X.shape[1])
        eigen = EigenDecomposition()
        eigen.decompose(X.T.dot(X))

        def cost_func(alpha):
            # Make sure that we always have positive penalization
            x = np.exp(alpha)
            return self._gcv_squared(x, X, y, eigen)

        def jac_cost_func(alpha):
            x = np.exp(alpha)
            grad = self._grad_gcv_squared(x, X, y, eigen)
            return grad * x

        res = minimize(cost_func, np.log(self.alpha), jac=jac_cost_func, **self.minimize_args)
        self.alpha = np.exp(res.x)

        if not res.success:
            logger.warning("Failed to find optimal regularization parameters.")
            logger.warning(res.message)

        # Sanity checks
        A = self._A(X, eigen, self.alpha)
        eff_num_params = np.trace(A)
        if eff_num_params < 0.0:
            logger.warning(("Warning! The effective number of parameters is negative. "
                            "Try to change the initial guess for alpha."))
        logger.info('Best GCV: %.3f', np.sqrt(res.fun))
        coeff = self._coeff(X, y, eigen)
        self.opt_result = {
            'gcv': np.sqrt(res.fun),
            'scipy_opt_res': res,
            'gcv_dev': (y - X.dot(coeff)) / (1.0 - eff_num_params / X.shape[0]),
            'press_dev': (y - X.dot(coeff)) / (1.0 - np.diag(A))
        }
        return coeff
