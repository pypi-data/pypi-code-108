from typing import List, Sequence, Dict, Union, Callable, Tuple
import time
import logging

import numpy as np
from numpy.random import choice
from scipy.linalg import solve_triangular

from clease.data_normalizer import DataNormalizer
from clease.tools import split_dataset
from .regression import LinearRegression
from .constrained_ridge import ConstrainedRidge

logger = logging.getLogger(__name__)

__all__ = ('PhysicalRidge',)


class PhysicalRidge(LinearRegression):
    """
    Physical Ridge is a special ridge regression scheme that enforces a
    convergent series. The physical motivation behind the choice of
    prior distributions is motivated by the fact that one expects that
    interactions strengths decays with both the number of atoms in the
    cluster and the diameter of the cluster. See for instance

    Cao, L., Li, C. and Mueller, T., 2018. The use of cluster expansions to
    predict the structures and properties of surfaces and nanostructured
    materials. Journal of chemical information and modeling, 58(12),
    pp.2401-2413.

    This fitting scheme uses Gaussian priors on the coefficients of the model

    P(M) = P_size(M)*P_dia(M), where

    P_size(M) = prod_i exp(-lamb_size*size_decay(size)*coeff_i^2)
    P_dia(M) = prod_i exp(-lamb_dia*dia_decay(dia)*coeff_i^2)

    where size_decay and dia_decay is a monotonically increasing function of
    the size and diameter respectively. The product goes over all coefficients
    in the model M.

    :param lamb_size: Prefactor in front of the size penalization

    :param lamb_dia: Prefactor in fron the the diameter penalization

    :param size_decay: The size_decay function in the priors explained above.
        It can be one of ['linear', 'exponential', 'polyN'],
        where N is any integer, or a callable function with
        the signature f(size), where size is the number of atoms in the
        cluster. If polyN is given the penalization is proportional to
        size**N

    :param dia_decay: The dia_decay function in the priors explained above.
        It can be one of ['linear', 'exponential', 'polyN']
        where N is any integer, of a callable function
        with the signature f(dia) where dia is the diameter.
        If polyN is given the penalization is proportional to dia**N

    :param normalize: If True the data will be normalized to unit variance
        and zero mean before fitting.

        NOTE: Normalization works only when the first column in X corresponds
        to a constant. If the X matrix contains several simultaneous fits
        (e.g. energy, pressure, bulk moduli) there will typically be different
        columns that corresponds to the bias term for the different groups. It
        is recommended to put normalize=False for such cases.
    """

    def __init__(self,
                 lamb_size: float = 1e-6,
                 lamb_dia: float = 1e-6,
                 size_decay: Union[str, Callable[[int], float]] = 'linear',
                 dia_decay: Union[str, Callable[[int], float]] = 'linear',
                 normalize: bool = True) -> None:
        super().__init__()
        self.lamb_size = lamb_size
        self.lamb_dia = lamb_dia
        self._size_decay = get_size_decay(size_decay)
        self._dia_decay = get_dia_decay(dia_decay)
        self.sizes = []
        self.diameters = []
        self.normalize = normalize
        self.normalizer = DataNormalizer()
        self._constraint = None

    def add_constraint(self, A: np.ndarray, c: np.ndarray) -> None:
        """
        Adds a constraint that the coefficients (ECI) has to obey,
        A.dot(coeff) = c

        :param A: Matrix describing the linear constraint
        :param c: Vector representing the right hand side of
            constraint equations
        """
        self._constraint = {'A': A, 'c': c}

    def fit_data(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        If normalize is True, a normalized version of the passed data is
        returned. Otherwise, X and y is returned as they are passed.

        :param X: Design matrix
        :param y: Target data
        """
        if self.normalize:
            X_fit, y_fit = self.normalizer.normalize(X, y)
            # Skip constant term since y is shifted to have mean zero
            # (and thus the constant term is zero)
            return X_fit[:, 1:], y_fit
        return X, y

    @property
    def size_decay(self) -> Callable[[int], float]:
        return self._size_decay

    @size_decay.setter
    def size_decay(self, decay: Union[str, Callable[[int], float]]) -> None:
        self._size_decay = get_size_decay(decay)

    @property
    def dia_decay(self) -> Callable[[int], float]:
        return self._dia_decay

    @dia_decay.setter
    def dia_decay(self, decay: Union[str, Callable[[int], float]]) -> None:
        self._dia_decay = get_dia_decay(decay)

    def sizes_from_names(self, names: List[str]) -> None:
        """
        Extract the sizes from a list of correlation function names

        :param names: List of cluster names.
            The length of the list has to match the
            number of columns in the X matrix passed to the fit method.
            Ex: ['c0', 'c1_1', 'c2_d0000_0_00']
        """
        self.sizes = [int(n[1]) for n in names]

    def diameters_from_names(self, names: List[str]) -> None:
        """
        Extract the diameters from a list of correltion function names

        :param names: List of cluster names.
            The length of the list has to match the
            number of columns in the X matrix passed to the fit method.
            Ex: ['c0', 'c1_1', 'c2_d0000_0_00']
        """
        diameters = []
        for n in names:
            if n[1] == '0' or n[1] == '1':
                diameters.append(0.0)
            else:
                dia_str = n.split('_')[1]
                dia = int(dia_str[1:])
                diameters.append(dia)
        self.diameters = diameters

    def fit(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Fit ECIs

        :param X: Design matrix with correlation functions. The shape is N x M,
            where N is the number of data points and M is the number of
            correlation functions

        :param y: Vector with target values. The length of this vector is N
            (e.g. equal to the number of rows in X)
        """
        if X.shape[1] != len(self.sizes) or X.shape[1] != len(self.diameters):
            msg = "Inconsistent number of columns in X. "
            msg += f"Num. columns: {X.shape[1]} "
            msg += f"Num. sizes: {len(self.sizes)} "
            msg += f"Num. diameters: {len(self.diameters)}"
            raise ValueError(msg)

        X_fit, y_fit = self.fit_data(X, y)

        size_decay_func = self.size_decay
        dia_decay_func = self.dia_decay

        size_decay = np.array([size_decay_func(x) for x in self.sizes])
        dia_decay = np.array([dia_decay_func(x) for x in self.diameters])

        penalty = self.lamb_size * size_decay + self.lamb_dia * dia_decay
        if len(penalty) == X_fit.shape[1] + 1:
            # In this case the constant term in X was removed
            penalty = penalty[1:]
        elif len(penalty) != X_fit.shape[1]:
            raise RuntimeError(f"Num. penalty {len(penalty)}. Num feature {X_fit.shape[1]}.")

        if self._constraint is not None:
            # Use the constrained Tikhonov verison
            regressor = ConstrainedRidge(penalty)
            regressor.add_constraint(self._constraint['A'], self._constraint['c'])
            coeff = regressor.fit(X_fit, y_fit)
        else:
            matrix = np.vstack((X_fit, np.diag(np.sqrt(penalty))))
            Q, R = np.linalg.qr(matrix)
            rhs = np.concatenate((y_fit, np.zeros(len(penalty))))
            coeff = solve_triangular(R, Q.T.dot(rhs), lower=False)

        if self.normalize:
            coeff_with_bias_term = np.concatenate(([0.0], coeff))
            coeff_transformed = self.normalizer.convert(coeff_with_bias_term)
            coeff_transformed[0] = self.normalizer.bias(coeff_with_bias_term)
            coeff = coeff_transformed
        return coeff


def linear_size(size: int) -> float:
    if size == 0:
        return 0.0
    return size


def linear_dia(dia: int) -> float:
    return dia


def exponential_size(size: int) -> float:
    if size == 0:
        return 0.0
    return np.exp(size - 1) - 1


def exponential_dia(dia: int) -> float:
    return np.exp(dia) - 1.0


def get_size_decay(decay: Union[str, Callable[[int], float]]) -> Callable[[int], float]:
    if isinstance(decay, str):
        if decay == 'linear':
            return linear_size
        if decay == 'exponential':
            return exponential_size
        if decay.startswith('poly'):
            power = int(decay[-1])
            return lambda size: size**power
        raise ValueError(f"Unknown decay type {decay}")
    if callable(decay):
        return decay

    raise ValueError("size_decay has to be either a string or callable")


def get_dia_decay(decay: Union[str, Callable[[int], float]]) -> Callable[[int], float]:
    if isinstance(decay, str):
        if decay == 'linear':
            return linear_dia
        if decay == 'exponential':
            return exponential_dia
        if decay.startswith('poly'):
            power = int(decay[-1])
            return lambda dia: dia**power
        raise ValueError(f"Unknown decay type {decay}")
    if callable(decay):
        return decay

    raise ValueError("dia_decay has to be either a string or callable")


def random_cv_hyper_opt(phys_ridge: PhysicalRidge,
                        params: Dict,
                        X: np.ndarray,
                        y: np.ndarray,
                        cv: int = 5,
                        num_trials: int = 100,
                        groups: Sequence[int] = ()) -> Dict:
    """
    Estimate the hyper parameters of the Physical Ridge by random search.

    :param phys_ridge: Instance of the physical ridge class

    :param params: Dictionary with candiates for all parameters. Example:
        {
            'lamb_dia': [1e-12, 1e-11, 1e-4, 1e-3],
            'lamb_size': [1e-12, 1e-11, 1e-4, 1e-3],
            'size_decay': ['linear', 'exponential'],
            'dia_decay': ['linear', 'exponential']
        }
        on each iteration a random combination of the the specified
        candidates will be attempted.

    :param cv: Number of folds used for cross validation

    :param num_trials: Number of combinations of hyper parameters
        that will be tried

    :param groups: Grouping information for X and y matrix. See docstring
        of `clease.tools.split_dataset` for furhter information.
    """
    # pylint: disable=too-many-locals
    best_param = None
    best_cv = 0.0
    best_mse = 0.0
    best_coeff = None

    cv_params = []
    last_print = time.time()
    partitions = split_dataset(X, y, nsplits=cv, groups=groups)

    for i in range(num_trials):
        lamb_dia = choice(params.get('lamb_dia', [phys_ridge.lamb_dia]))
        lamb_size = choice(params.get('lamb_size', [phys_ridge.lamb_size]))
        size_decay = choice(params.get('size_decay', [phys_ridge.size_decay]))
        dia_decay = choice(params.get('dia_decay', [phys_ridge.dia_decay]))

        phys_ridge.lamb_dia = lamb_dia
        phys_ridge.lamb_size = lamb_size
        phys_ridge.size_decay = size_decay
        phys_ridge.dia_decay = dia_decay

        param_dict = {
            'lamb_dia': lamb_dia,
            'lamb_size': lamb_size,
            'size_decay': size_decay,
            'dia_decay': dia_decay,
        }

        cv_score = 0.0
        mse = 0.0
        for p in partitions:
            coeff = phys_ridge.fit(p['train_X'], p['train_y'])
            pred = p['validate_X'].dot(coeff)
            cv_score += np.sqrt(np.mean((pred - p['validate_y'])**2))

            pred = p['train_X'].dot(coeff)
            mse += np.sqrt(np.mean((pred - p['train_y'])**2))

        cv_score /= len(partitions)
        mse /= len(partitions)

        cv_params.append((cv_score, param_dict))
        if best_param is None or cv_score < best_cv:
            best_cv = cv_score
            best_mse = mse
            best_coeff = coeff
            best_param = param_dict

        if time.time() - last_print > 30:
            msg = (f"{i} of {num_trials}. CV: {best_cv*1000.0} meV/atom. "
                   f"MSE: {best_mse*1000.0} meV/atom. Params: {best_param}")
            logger.info(msg)
            last_print = time.time()

    cv_params = sorted(cv_params, key=lambda x: x[0])
    res = {
        'best_coeffs': best_coeff,
        'best_params': best_param,
        'best_cv': best_cv,
        'cvs': [x[0] for x in cv_params],
        'params': [x[1] for x in cv_params]
    }
    return res
