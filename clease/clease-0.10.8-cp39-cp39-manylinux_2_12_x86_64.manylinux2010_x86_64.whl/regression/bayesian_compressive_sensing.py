import time
import json
import logging
from itertools import product
import numpy as np
from scipy.special import polygamma
from scipy.optimize import brentq
from matplotlib import pyplot as plt
from .regression import LinearRegression

logger = logging.getLogger(__name__)

__all__ = ('BayesianCompressiveSensing',)


class BayesianCompressiveSensing(LinearRegression):
    """
    Fit a sparse CE model to data. Based on the method
    described in

    Babacan, S. Derin, Rafael Molina, and Aggelos K. Katsaggelos.
    "Bayesian compressive sensing using Laplace priors."
    IEEE Transactions on Image Processing 19.1 (2010): 53-63.

    Different values has different priors.

    1. For the ECIs a normal distribution is assumed
        (the i-th eci is: eci_i -- N(J | 0, var_i)=
    2. The inverce variance of each ECI is gamma distributed
        (i.e. 1/var_i -- gamma(x | 1, lambda/2))
    3. The lambda parameter above is also gamma distributed
        (i.e. lamb -- gamma(x | shape_lamb/2, shape_lamb/2))
    4. The noise parameter is uniformly distributed on the
        positive axis (i.e. noise -- uniform(x | 0, inf)

    Parameters:

    shape_var: float
        Shape parameter for the gamma distribution for the
        inverse variance (1/var -- gamma(x | shape_var/2, rate_var/2))
    rate_var: float
        Rate parameter for the gamma distribution for the
        inverse variance (1/var -- gamma(x | shape_var/2, rate_var/2))
    shape_lamb: float
        Shape parameter for gamma distribution for the
        lambda parameter (lambda -- gamma(x | 1, shape_lamb))
    variance_opt_start: int
        Optimization of inverse variance starts after this amount
        of iterations
    lamb_opt_start: int
        Optimization of lambda and shape_lamb starts after this
        amount of iterations. If this number is set very high,
        lambda will be kept at zero, making the algorithm
        efficitively a Relvance Vector Machine (RVM)
    fname: str
        Backup file for parameters
    maxiter: int
        Maximum number of iterations
    output_rate_sec: int
        Interval in seconds between status messages
    select_strategy: str
        Strategy for selecting new correlation function for each iteration.
        If 'max_increase' it will select the basis function that leads
        to the largest increase in likelihood value.
        If 'random' correlation functions are selected at random
    noise: float
        Initial estimate of the noise in the data
    init_lamb: float
        Initial value for the lambda parameter
    penalty: float
        Penalization value added to the diagonal of matrice
        to avoid singular matrices
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 shape_var=0.5,
                 rate_var=0.5,
                 shape_lamb=0.5,
                 lamb_opt_start=200,
                 variance_opt_start=100,
                 fname="bayes_compr_sens.json",
                 maxiter=100000,
                 output_rate_sec=2,
                 select_strategy="max_increase",
                 noise=0.1,
                 init_lamb=0.0,
                 penalty=1E-8):
        # pylint: disable=too-many-arguments
        super().__init__()

        # Paramters
        self.shape_var = shape_var
        self.rate_var = rate_var
        self.shape_lamb = shape_lamb
        self.variance_opt_start = variance_opt_start
        self.maxiter = maxiter
        self.output_rate_sec = output_rate_sec
        self.select_strategy = select_strategy
        self.fname = fname
        self.noise = noise
        self.lamb_opt_start = lamb_opt_start
        self.penalty = penalty

        # Store a copy of all the key-word arguments
        # passed by the user
        self.user_supplied_args = {
            "shape_var": shape_var,
            "rate_var": rate_var,
            "shape_lamb": shape_lamb,
            "lamb_opt_start": lamb_opt_start,
            "variance_opt_start": variance_opt_start,
            "fname": fname,
            "maxiter": maxiter,
            "output_rate_sec": output_rate_sec,
            "select_strategy": select_strategy,
            "noise": noise,
            "init_lamb": init_lamb,
            "penalty": penalty
        }

        # Arrays used during fitting
        self.X = None
        self.y = None

        self.gammas = None
        self.eci = None
        self.inv_variance = None
        self.lamb = init_lamb
        self.inverse_sigma = None
        self.eci = None

        # Quantities used for fast updates
        self.S = None
        self.Q = None
        self.ss = None
        self.qq = None

    def _initialize(self, reset=False):
        """
        Initialize all parameters after X and y is given
        """
        if reset:
            self.__dict__.update(self.user_supplied_args)
        num_features = self.X.shape[1]
        if reset or self.gammas is None:
            self.gammas = np.zeros(num_features)
        self.eci = np.zeros_like(self.gammas)

        if reset or self.inv_variance is None:
            self.inv_variance = 1.0 / self.noise**2

        if reset or self.lamb is None:
            self.lamb = 0.0

        self.inverse_sigma = np.zeros((num_features, num_features))
        self.eci = np.zeros(num_features)

        if self.X is not None:
            # Quantities used for fast updates
            self.S = np.diag(self.inv_variance * self.X.T.dot(self.X))
            self.Q = self.inv_variance * self.X.T.dot(self.y)
            self.ss = self.S / (1.0 - self.gammas * self.S)
            self.qq = self.Q / (1.0 - self.gammas * self.S)

    def precision_matrix(self, X):
        """
        Return the precision matrix needed by the Evaluate class.
        Only contributions from the correlation functions with
        gamma > 0 are included.
        """
        if not np.allclose(X, self.X):
            raise RuntimeError("Inconsistent design matrix given!")
        sel_indx = self.selected
        X_sel = self.X[:, sel_indx]
        N = len(sel_indx)
        prec = np.linalg.inv(X_sel.T.dot(X_sel) + self.penalty * np.eye(N))

        N = self.X.shape[1]
        full_prec = np.zeros((N, N))

        indx = list(range(len(sel_indx)))
        for i in product(indx, indx):
            full_prec[sel_indx[i[0]], sel_indx[i[1]]] = prec[i[0], i[1]]
        return full_prec

    def mu(self):
        """
        Calculate the expectation value for the ECIs
        """
        sel = self.selected
        return self.inv_variance * self.inverse_sigma.dot(self.X[:, sel].T.dot(self.y))

    def optimal_gamma(self, indx):
        """
        Return the gamma value that maximize the likelihood

        Parameters:

        indx: int
            Index of the selected correlation function
        """
        s = self.ss[indx]

        # Conda had divide by zero error
        if abs(s) < 1E-6:
            s = 1E-6
        qsq = self.qq[indx]**2

        if self.lamb < 1E-6:
            return (self.qq[indx] / s)**2 - 1.0 / s

        term1 = s + 2 * self.lamb

        delta = s**2 + 4 * self.lamb * qsq

        gamma = (np.sqrt(delta) - term1) / (2 * self.lamb * s)
        return gamma

    def optimal_lamb(self):
        """Calculate the optimal value for the lambda parameter. """
        N = self.X.shape[1]  # Number of ECIs
        return 2*(N - 1 + 0.5*self.shape_lamb) / \
            (np.sum(self.gammas) + self.shape_lamb)

    def optimal_inv_variance(self):
        """Calculate the optimal value for the inverse variance"""
        N = self.X.shape[0]  # Number of data points
        a = 1.0
        b = 0.0
        mse = np.sum((self.y - self.X.dot(self.eci))**2)
        return (0.5 * N + a) / (0.5 * mse + b)

    def optimal_shape_lamb(self):
        """Calculate the optimal value for the shape paremeter for lambda."""
        res = brentq(shape_parameter_equation, 1E-30, 1E100, args=(self.lamb,), maxiter=10000)
        return res

    def update_quantities(self):
        """Update helper parameters needed for the next iteration."""
        sel = self.selected
        X_sel = self.X[:, sel]
        prec = X_sel.dot(self.inverse_sigma).dot(X_sel.T)

        self.S = \
            np.diag(self.inv_variance*self.X.T.dot(self.X)
                    - self.inv_variance**2 * self.X.T.dot(prec.dot(self.X)))
        self.Q = self.inv_variance*self.X.T.dot(self.y) - \
            self.inv_variance**2 * self.X.T.dot(prec.dot(self.y))

        self.ss = self.S / (1.0 - self.gammas * self.S)
        self.qq = self.Q / (1.0 - self.gammas * self.S)

    @property
    def selected(self):
        return np.argwhere(self.gammas > 0.0)[:, 0]

    def update_sigma_mu(self):
        """Update sigma and mu."""
        X_sel = self.X[:, self.selected]
        sigma = self.inv_variance*X_sel.T.dot(X_sel) + \
            np.diag(1.0/self.gammas[self.selected])
        try:
            self.inverse_sigma = np.linalg.inv(sigma)
        except np.linalg.LinAlgError:
            self.inverse_sigma = np.linalg.pinv(sigma)
        self.eci[self.selected] = self.mu()

    def get_basis_function_index(self, select_strategy) -> int:
        """Select a new correlation function."""
        if select_strategy == "random":
            return np.random.randint(low=0, high=len(self.gammas))
        if select_strategy == "max_increase":
            return self._get_bf_with_max_increase()
        raise ValueError(f'Unknown select strategy: {select_strategy}')

    def log_likelihood_for_each_gamma(self, gammas):
        """Log likelihood value for all gammas.

        Arguments
        =========
        gammas: np.ndarray
            Value for all the gammas
        """
        denum = 1 + gammas * self.ss

        # quantities leading to a negativie denuminator should not
        # be possible (but because of iterative increment they occure)
        # once in a while. Set such numbers to a number close to zero.
        denum[denum <= 0.0] = 1E-10
        return np.log(1 / denum) + self.qq**2 * gammas / denum - self.lamb * gammas

    def _get_bf_with_max_increase(self):
        """Return the index of the correlation function that leads
           to the largest increase in likelihiood value."""

        new_gammas = np.array([self.optimal_gamma(i) for i in range(len(self.gammas))])

        if np.all(new_gammas < 0.0):
            rand_gam = np.random.randint(0, high=(len(self.gammas)))
            logger.warning(
                "Cannot determine which gamma to include. Trying random selection, gamma=%.3f ...",
                rand_gam)
            return rand_gam

        new_gammas[new_gammas < 0.0] = 0.0
        current_likeli = self.log_likelihood_for_each_gamma(self.gammas)
        new_likeli = self.log_likelihood_for_each_gamma(new_gammas)

        diff = new_likeli - current_likeli
        return np.argmax(diff)

    def rmse(self):
        """Return root mean square error."""
        indx = self.selected
        pred = self.X[:, indx].dot(self.eci[indx])
        return np.sqrt(np.mean((pred - self.y)**2))

    @property
    def num_ecis(self):
        return np.count_nonzero(self.gammas)

    def todict(self):
        """Convert all parameters to a dictionary."""
        data = {}

        # Selection of vars we want to save
        vars_to_save = ("inv_variance", 'gammas', 'shape_var', 'rate_var', 'shape_lamb', 'lamb',
                        'maxiter', 'output_rate_sec', 'select_strategy', 'noise', 'lamb_opt_start')
        for var in vars_to_save:
            val = getattr(self, var)
            if isinstance(val, np.ndarray):
                val = val.tolist()
            data[var] = val

        return data

    def save(self):
        """Save the results from file."""
        with open(self.fname, 'w') as outfile:
            json.dump(self.todict(), outfile)
        logger.info("Backup data written to %s", self.fname)

    @staticmethod
    def load(fname):
        bayes = BayesianCompressiveSensing()
        bayes.fname = fname
        with open(fname, 'r') as infile:
            data = json.load(infile)

        for key, value in data.items():
            if value is not None:
                setattr(bayes, key, value)
        return bayes

    def __eq__(self, other):
        """Compare to BayesianCompressiveSensing objects."""
        equal = True

        # Required fields to be equal if two objects
        # should be considered equal
        items = [
            "fname", "gammas", "inv_variance", "lamb", "shape_var", "rate_var", "shape_lamb",
            "lamb", "maxiter", "select_strategy", "output_rate_sec", "noise", "variance_opt_start"
        ]
        for k in items:
            v = self.__dict__[k]
            if isinstance(v, np.ndarray):
                equal = equal and np.allclose(v, other.__dict__[k])
            elif isinstance(v, float):
                equal = equal and abs(v - other.__dict__[k]) < 1E-6
            else:
                equal = equal and (v == other.__dict__[k])
        return equal

    def estimate_loocv(self):
        """Return an estimate of the LOOCV."""
        X_sel = self.X[:, self.selected]
        e_pred = self.X.dot(self.eci)
        delta_e = e_pred - self.y
        N = X_sel.shape[1]
        prec = np.linalg.inv(X_sel.T.dot(X_sel) + self.penalty * np.eye(N))

        delta_cv = delta_e / (1 - np.diag(X_sel.dot(prec).dot(X_sel.T)))
        cv_sq = np.mean(delta_cv**2)
        return np.sqrt(cv_sq)

    def fit(self, X, y):
        """Fit ECIs to the data

        Parameters:

        X: np.ndarray
            Design matrix (NxM: N number of datapoints,
            M number of correlation functions)
        y: np.ndarray
            Array of length N with the energies
        """
        # pylint: disable=too-many-branches, too-many-statements
        # XXX: Needs some cleaning
        allowed_strategies = ["random", "max_increase"]

        if self.select_strategy not in allowed_strategies:
            msg = f"select_strategy has to be one of {allowed_strategies}"
            raise ValueError(msg)

        self.X = X
        self.y = y
        self._initialize(reset=True)

        is_first = True
        iteration = 0
        now = time.time()
        d_gamma = 1E100
        while iteration < self.maxiter:
            if time.time() - now > self.output_rate_sec:
                msg = f"Iter: {iteration} "
                msg += f"RMSE: {1000.0*self.rmse():.3E} "
                msg += f"LOOCV (approx.): {1000.0*self.estimate_loocv():.3E} "
                msg += f"Num ECI: {self.num_ecis} "
                msg += f"Lamb: {self.lamb:.3E} "
                msg += f"Shape lamb: {self.shape_lamb:.3E} "
                msg += f"Noise: {np.sqrt(1.0/self.inv_variance):.3E}"
                logger.info(msg)
                now = time.time()

            iteration += 1
            already_excluded = False

            if is_first:
                indx = np.argmax(self.qq**2 - self.ss)
                is_first = False
            else:
                indx = self.get_basis_function_index(self.select_strategy)
            gamma = self.optimal_gamma(indx)

            d_gamma = 0.0
            if gamma > 0.0:
                d_gamma = gamma - self.gammas[indx]
                self.gammas[indx] = gamma
            else:
                gamma = self.gammas[indx]

                if abs(gamma) < 1E-6:
                    already_excluded = True

                self.gammas[indx] = 0.0
                self.eci[indx] = 0.0

            if already_excluded:
                continue

            self.update_sigma_mu()
            self.update_quantities()

            if iteration > self.lamb_opt_start:
                self.lamb = self.optimal_lamb()
                self.shape_lamb = self.optimal_shape_lamb()

            if iteration > self.variance_opt_start:
                self.inv_variance = self.optimal_inv_variance()

            if abs(d_gamma) < 1E-8:
                break

        # Save backup for future restart
        if self.fname:
            self.save()

        return self.eci

    def show_shape_parameter(self):
        """Show a plot of the transient equation for the optimal
            shape parameter for lambda."""
        x = np.logspace(-10, 10)

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x, shape_parameter_equation(x, self.lamb))
        ax.axhline(0, ls="--")
        ax.set_xscale("log")
        plt.show()

    @property
    def weight_matrix(self):
        return LinearRegression.weight_matrix(self)


def shape_parameter_equation(x, lamb):
    return np.log(x / 2.0) + 1 - polygamma(0, x / 2) + np.log(lamb) - lamb
