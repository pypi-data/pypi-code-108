"""
A module for instantiating and performing operations on multivariate Gaussian distributions.
"""

# pylint: disable=cyclic-import
# pylint: disable=protected-access
# pylint: disable=no-self-use

# System imports
import cmath
import copy
import operator

# Third-party imports
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Local imports
from veroku.factors._factor import Factor
from veroku.factors import _factor_utils
from veroku.factors._factor_template import FactorTemplate
from veroku._constants import DEFAULT_FACTOR_RTOL, DEFAULT_FACTOR_ATOL
import veroku.factors.experimental.gaussian_mixture as gm


def make_random_gaussian(var_names, mean_range=None, cov_range=None):
    """
    Make a d dimensional random Gaussian by independently sampling the mean and covariance parameters from uniform
    distributions.

    :param var_names: The variable name of the factor
    :type var_names: str list
    :param mean_range: The range between which a mean will the uniformly sampled.
    :type mean_range: float list
    :param cov_range:The range between which a covariance will the uniformly sampled.
    :type cov_range: float list
    :return: The random Gaussian.
    :rtype: Gaussian
    """
    if mean_range is None:
        mean_range = [-10, 10]
    if cov_range is None:
        cov_range = [1, 10]
    assert var_names, "Error: var_names list cannot be empty."
    dim = len(var_names)
    # TODO: Add non diagonal covariance matrix sampling and add test for PSD covariance matrices.
    cov = np.random.uniform(cov_range[0], cov_range[1], [dim, dim]) * np.eye(dim, dim)
    mean = np.random.uniform(mean_range[0], mean_range[1], [dim, 1])
    random_gaussian = Gaussian(cov=cov, mean=mean, log_weight=0.0, var_names=var_names)
    return random_gaussian


def make_std_gaussian(var_names):
    """
    Make a d dimensional standard Gaussian.

    :param var_names: The variable name of the factor.
    :type var_names: str list
    :return: The standard Gaussian
    :rtype: Gaussian
    """
    assert var_names, "Error: var_names list cannot be empty."
    dim = len(var_names)
    cov = np.eye(dim, dim)
    mean = np.zeros([dim, 1])
    random_gaussian = Gaussian(cov=cov, mean=mean, log_weight=0.0, var_names=var_names)
    return random_gaussian


def make_linear_gaussian(a_mat, n_mat, conditioning_vars, conditional_vars):
    """
    Make a linear Gaussian factor.

    :param a_mat: The linear transform matrix.
    :type a_mat: numpy.ndarray
    :param n_mat: The additive noise covariance matrix.
    :type n_mat: numpy.ndarray
    :param conditioning_vars: The list of conditioning variables.
    :param conditional_vars: The list of conditional variables.
    :return: The linear Gaussian Template
    :rtype: Gaussian
    """

    # TODO: improve this by adding the correct equations for calculating the linear Gaussian parameters that do not rely
    #  on the dummy factor multiplication.
    x_dim = len(conditioning_vars)
    cov_xx = np.eye(x_dim)
    prec_xx = np.linalg.inv(cov_xx)

    u_x = np.zeros([x_dim, 1])
    h_x = prec_xx @ u_x
    g_x = -0.5 * u_x.T @ h_x + np.log(1.0) - 0.5 * np.log(np.linalg.det(2.0 * np.pi * cov_xx))

    cov = np.block([[cov_xx, cov_xx @ a_mat.T], [a_mat @ cov_xx, a_mat @ cov_xx @ a_mat.T + n_mat]])
    prec_joint = np.linalg.inv(cov)
    prec_cpd = prec_joint.copy()
    prec_cpd[:x_dim, :x_dim] = prec_cpd[:x_dim, :x_dim] - prec_xx

    mean_joint = np.block([[u_x], [a_mat.T @ u_x]])

    h_cpd = prec_joint @ mean_joint
    h_cpd[:x_dim] = h_cpd[:x_dim] - h_x

    utkux = mean_joint.T @ prec_joint @ mean_joint
    g_joint = 0.5 * utkux + np.log(1.0) - 0.5 * np.log(np.linalg.det(2.0 * np.pi * cov))
    g_cpd = g_joint - g_x

    return Gaussian(var_names=conditioning_vars + conditional_vars, prec=prec_cpd, h_vec=h_cpd, g_val=g_cpd)


def make_linear_gaussian_cpd_template(a_mat, n_mat, conditioning_var_templates, conditional_var_templates):
    """
    Make a linear Gaussian factor template.

    :param a_mat: The linear transform matrix.
    :type a_mat: numpy.ndarray
    :param n_mat: The additive noise covariance matrix.
    :type n_mat: numpy.ndarray
    :param conditioning_var_templates: The list of formattable strings for the conditioning variables (i.e: ['var_a{i}_{t}', 'var_b{i}_{t}'])
    :param conditional_var_templates: The list of formattable strings for the conditional variables (i.e: ['var_c{i}_{t}', 'var_d{i}_{t}'])
    :return: The linear Gaussian Template
    :rtype: Gaussian
    """
    assert len(conditioning_var_templates) == a_mat.shape[0]
    assert n_mat.shape[0] == a_mat.shape[0]
    nlg = make_linear_gaussian(a_mat, n_mat, conditioning_var_templates, conditional_var_templates)
    var_templates = conditioning_var_templates + conditional_var_templates
    gaussian_parameters = {"prec": nlg.get_prec(), "h": nlg.get_h(), "g": 0}
    return GaussianTemplate(gaussian_parameters, var_templates)


class Gaussian(Factor):
    """
    A class for instantiating and performing operations om multivariate Gaussian distributions.
    """

    def __init__(self, cov=None, mean=None, log_weight=None, prec=None, h_vec=None, g_val=None, var_names=None):
        """
        General constructor that can use either covariance form or canonical form parameters to construct a
        d-dimensional multivariate Gaussian object.

        :param cov: (covariance form) The covariance matrix (or variance scalar in 1-dimensional case).
        :type cov: dxd numpy.ndarray or float
        :param mean: (covariance form) The mean vector (or mean scalar in 1-dimensional case).
        :type mean: dx1 numpy.ndarray or float
        :param log_weight: (covariance form) The log of the weight (the Gaussian function integrates to the weight value)
        :type log_weight: float
        :param prec: (canonical form) The precision matrix (or precision scalar in 1-dimensional case).
        :type prec: dxd numpy.ndarray or float
        :param h_vec: (canonical form) The h vector  (or h scalar in 1-dimensional case).
        :type h_vec: dx1 numpy.ndarray or float
        :param g_val: (canonical form) The g parameter.
        :type g_val: float
        :param var_names: a list of variable names where the order of the names correspond to the order in the
                         mean and covariance (or precision and h vector)  parameters.
        :type var_names: str list

        Example:

        .. code-block:: python

            # Using covariance form parameters
            >>> Gaussian(cov=[[1, 0], [0, 1]], mean=[0, 0], log_weight=0.0, var_names=["a", "b"])
            # Using canonical form parameters
            >>> Gaussian(prec=[[1, 0], [0, 1]], h_vec=[0, 0], g_val=0.0, var_names=["a", "b"])

        """
        if var_names is None:
            raise ValueError("var_names not provided.")
        super().__init__(var_names=var_names)
        self._is_vacuous = False
        if all(v is None for v in [prec, h_vec, g_val]):
            if any(v is None for v in [cov, mean, log_weight]):
                raise ValueError("incomplete parameters")
            self.cov = _factor_utils.make_square_matrix(cov)
            self.mean = _factor_utils.make_column_vector(mean)
            assert len(self.cov.shape) == 2, "Error: Covariance matrix must be two dimensional."

            assert self.cov.shape[0] == self.dim, "Error: Covariance matrix dimension inconsistency."
            assert self.mean.shape[0] == self.dim, "Error: Mean vector dimension inconsistency."
            self.log_weight = _factor_utils.make_scalar(log_weight)
            self.prec, self.h_vec, self.g_val = None, None, None
            self.canform = False
            self.covform = True
        else:
            if any(v is None for v in [prec, h_vec, g_val]):
                raise ValueError("incomplete parameters")
            self.prec = _factor_utils.make_square_matrix(prec)
            self.h_vec = _factor_utils.make_column_vector(h_vec)
            if self.prec.shape[0] != self.dim:
                pass
            assert len(self.prec.shape) == 2, "Error: Precision matrix must be two dimensional."
            assert self.prec.shape[0] == self.dim, "Error: Precision matrix dimension inconsistency."
            h_error_msg = f"Error: h vector dimension inconsistency: {self.h_vec.shape[0]} (should be {self.dim})"
            assert self.h_vec.shape[0] == self.dim, h_error_msg
            self.g_val = _factor_utils.make_scalar(g_val)
            self.cov, self.mean, self.log_weight = None, None, None
            self.canform = True
            self.covform = False

            # Note: this is important to allow vacuous Gaussians (that arise, for exmaple, when Gaussians are divided by
            # identical distributions or with unconditioned nonlinear Gaussians) to be merginalised.
            if self.is_vacuous:
                self._is_vacuous = True

    @classmethod
    def make_vacuous(cls, var_names, g_val=0.0):
        """
        Make an vacuous Gaussian distribution with a zero precision matrix and zero h vector and zero g value.
        This 'Gaussian' is effectively a constant function (it has infinite variance and infinite mass) with value
        exp(g).

        :param var_names: The variable names.
        :type var_names: str list
        :param g_val: The g parameter.
        :type g_val: float
        :return: The vacuous Gaussian with zero K and h parameters.
        :rtype: Gaussian
        """
        dim = len(var_names)
        prec_zero = np.zeros([dim, dim])
        h_zero = np.zeros([dim, 1])
        g_zero = g_val
        return cls(prec=prec_zero, h_vec=h_zero, g_val=g_zero, var_names=var_names)

    def _reorder_parameters(self, new_order_vars):
        """
        Reorder the values in the matrix and vector parameters according to the order of new_order_vars

        :param new_order_vars: The same variable names as in self.var_names, in a different order
        :type new_order_vars: str list
        """
        if new_order_vars == self._var_names:
            return
        assert set(new_order_vars) == set(
            self._var_names
        ), "Error: new_order_vars must contain the same variable names as in var_names."
        new_order = [new_order_vars.index(var) for var in self._var_names]

        if self.canform:
            new_prec = np.zeros([self.dim, self.dim])
            new_h_vec = np.zeros([self.dim, 1])
            for i, new_i in enumerate(new_order):
                new_h_vec[new_i, 0] = self.h_vec[i, 0]
                for j, new_j in enumerate(new_order):
                    new_prec[new_i, new_j] = self.prec[i, j]
            self.prec = new_prec
            self.h_vec = new_h_vec

        if self.covform:
            new_cov = np.zeros([self.dim, self.dim])
            new_mean = np.zeros([self.dim, 1])
            for i, new_i in enumerate(new_order):
                new_mean[new_i, 0] = self.mean[i, 0]
                for j, new_j in enumerate(new_order):
                    new_cov[new_i, new_j] = self.cov[i, j]
            self.cov = new_cov
            self.mean = new_mean
        self._var_names = new_order_vars

    def _canform_equals(self, gaussian, rtol, atol):
        """
        Helper function for check equivalence of canonical form parameters.
        """
        if not np.isclose(self.g_val, gaussian.get_g(), rtol=rtol, atol=atol, equal_nan=False):
            return False
        gaussian._reorder_parameters(self.var_names)
        if not np.allclose(self.h_vec, gaussian.get_h(), rtol=rtol, atol=atol, equal_nan=False):
            return False
        if not np.allclose(self.prec, gaussian.get_prec(), rtol=rtol, atol=atol, equal_nan=False):
            return False
        return True

    def _covform_equals(self, gaussian, rtol, atol):
        """
        Helper function for check equivalence of covariance form parameters.
        """

        if not np.isclose(self.get_weight(), gaussian.get_weight(), rtol=rtol, atol=atol, equal_nan=False):
            return False
        gaussian._reorder_parameters(self.var_names)
        if not np.allclose(self.mean, gaussian.get_mean(), rtol=rtol, atol=atol, equal_nan=False):
            return False
        if not np.allclose(self.cov, gaussian.get_cov(), rtol=rtol, atol=atol, equal_nan=False):
            return False
        return True

    def equals(self, factor, rtol=DEFAULT_FACTOR_RTOL, atol=DEFAULT_FACTOR_ATOL):
        """
        Check if this factor is the same as another factor.

        :param factor: The factor to compare with.
        :type factor: Gaussian
        :param float rtol: The absolute tolerance parameter (see numpy Notes for allclose function).
        :param float atol: The absolute tolerance parameter (see numpy Notes for allclose function).
        :return: Result of equals comparison between self and gaussian
        rtype: bool
        """

        # TODO: extend this to cover other factors that could be equal (i.e Gaussian mixtures with one component or
        #  Gaussian factorised factors)
        if not isinstance(factor, Gaussian):
            raise ValueError(f"unexpected factor type {type(factor)} in Gaussian equals function.")

        if set(self._var_names) != set(factor.var_names):
            return False

        gaussian_copy = factor.copy()
        if self._var_names != factor.var_names:
            gaussian_copy._reorder_parameters(self._var_names)
        if gaussian_copy._is_vacuous and self._is_vacuous:
            return True
        if self.canform:
            if self._canform_equals(factor, rtol, atol):
                return True
            return False
        self._update_covform()
        if self.covform:
            if not self._covform_equals(factor, rtol, atol):
                return False
        return True

    def get_prec(self):
        """
        Get the precision parameter.

        :return: The prec parameter.
        :rtype: dxd numpy.ndarray or float
        """
        self._update_canform()
        if self.prec is not None:
            return self.prec.copy()
        return None

    def get_h(self):
        """
        Get the h vector.

        :return: The h parameter.
        :rtype: float
        """
        self._update_canform()
        if self.h_vec is not None:
            return self.h_vec.copy()
        return None

    def get_g(self):
        """
        Get the g parameter.

        :return: The g parameter.
        :rtype: float
        """
        self._update_canform()
        return self.g_val

    def _cov_exists(self):
        """
        Check is the cov matrix has or can be calculated (i.e the precision matrix is not singular).

        :return: The result of the check.
        :rtype: bool
        """
        if self.covform:
            return True
        try:
            np.linalg.inv(self.prec)
        except np.linalg.LinAlgError:
            return False
        return True

    def get_cov(self):
        """
        Get the covariance parameter.

        :return: The cov parameter.
        :rtype: numpy.ndarray
        """
        self._update_covform()
        if self.cov is not None:
            return self.cov.copy()
        return None

    def get_mean(self):
        """
        Get the mean parameter.

        :return: The mean parameter.
        :rtype: numpy.ndarray
        """
        self._update_covform()
        if self.mean is not None:
            return self.mean.copy()
        return None

    def get_log_weight(self):
        """
        Get the log weight parameter.

        :return: The log_weight parameter.
        :rtype: numpy.ndarray
        """
        self._update_covform()
        return self.log_weight

    def normalize(self):
        """
        Normalize the factor.

        :return: The normalized factor.
        :rtype: Gaussian
        """
        gaussian_copy = self.copy()
        gaussian_copy._update_covform()
        gaussian_copy.log_weight = 0.0
        gaussian_copy._destroy_canform()
        return gaussian_copy

    def _get_complex_weight(self):
        """
        Get (possibly complex) weight parameter.

        :return: The weight parameter.
        :rtype: float
        """
        return cmath.exp(self._get_complex_log_weight())

    def _get_complex_log_weight(self):
        """
        Get the log weight even in cases where the determinant of the covariance matrix is negative. In such cases the
        log_weight no longer corresponds to the integral and the log of the weight will have a imaginary component.
        Computing the complex log-weight can however still be useful: it is used, for example, in the (experimental)
        Gaussian mixture division function (_gm_division_m2).

        :return: The potentially complex log weight
        :rtype: complex
        """
        self._update_canform()
        cov = np.linalg.inv(self.prec)
        mean = cov @ self.h_vec
        ut_prec_u = (mean.T @ self.prec @ mean).astype(complex)
        log_weight = self.g_val + 0.5 * ut_prec_u + 0.5 * cmath.log(np.linalg.det(2.0 * np.pi * cov))
        return log_weight

    def _invert(self):
        """
        Invert this Gaussian (1/Gaussian). This is used in the approximate Gaussian mixture division algorithms.

        :return: The inverted Gaussian.
        """
        assert self.canform
        gaussian_copy = self.copy()
        gaussian_copy.prec = (-1.0) * self.prec
        gaussian_copy.h_vec = (-1.0) * self.h_vec
        gaussian_copy.g_val = (-1.0) * self.g_val
        gaussian_copy._destroy_covform()
        return gaussian_copy

    def _add_log_weight(self, log_weight_to_add):
        """
        Add log value to the log weight.

        :param log_weight_to_add: The log value to add to the weight.
        :type log_weight_to_add: float
        """
        if self.canform:
            self.g_val += log_weight_to_add
        if self.covform:
            self.log_weight += log_weight_to_add

    def get_weight(self):
        """
        Get the weight of the distribution - the value of the integral of the (possibly unnormalized) distribution.

        :return: The weight.
        :rtype: float
        """
        return np.exp(self.get_log_weight())

    def _canform_marginalise(self, vars_to_keep, vars_to_integrate_out):
        """
        Calculate the marginal distribution using the canonical parameters.

        :param vars_to_keep: The variables to keep.
        :param vars_to_integrate_out: The variables to integrate out/
        :return: The marginal Gaussian
        """
        xx_indices = [self.var_names.index(var_x) for var_x in vars_to_keep]
        yy_indices = [self.var_names.index(var_y) for var_y in vars_to_integrate_out]
        prec_xx = self.prec[np.ix_(xx_indices, xx_indices)]
        prec_xy = self.prec[np.ix_(xx_indices, yy_indices)]
        prec_yx = prec_xy.T
        prec_yy = self.prec[yy_indices][:, yy_indices]
        inv_prec_yy = np.linalg.inv(prec_yy)
        h_x = self.h_vec[xx_indices]
        h_y = self.h_vec[yy_indices]
        prec_xy_inv_prec_yy = prec_xy @ np.linalg.inv(prec_yy)
        prec = prec_xx - prec_xy_inv_prec_yy @ prec_yx
        h_vec = h_x - prec_xy_inv_prec_yy @ h_y
        log_det_2pi_inv_prec_yy = np.log(np.linalg.det(2.0 * np.pi * inv_prec_yy))
        g_val = self.g_val + 0.5 * (h_y.T @ inv_prec_yy @ h_y + log_det_2pi_inv_prec_yy)
        return Gaussian(prec=prec, h_vec=h_vec, g_val=g_val, var_names=vars_to_keep)

    def marginalize(self, vrs, keep=True):
        """
        Integrate out variables from this Gaussian.

        :param vrs: A subset of variables in the factor's scope.
        :type vrs: str list
        :param keep: Whether to keep or sum out vrs.
        :type keep: bool
        :return: The resulting Gaussian marginal.
        :rtype: Gaussian
        """
        vars_to_keep = super().get_marginal_vars(vrs, keep)
        vars_to_integrate_out = list(set(self.var_names) - set(vars_to_keep))
        if self._is_vacuous:
            # TODO: check this (esp log_weight)
            return Gaussian.make_vacuous(var_names=vars_to_keep)

        if self.canform:
            return self._canform_marginalise(vars_to_keep, vars_to_integrate_out)

        assert self.covform
        indices_to_keep = [self._var_names.index(variable) for variable in vars_to_keep]
        marginal_var_names = vars_to_keep.copy()

        marginal_cov = self.cov[np.ix_(indices_to_keep, indices_to_keep)]
        marginal_mean = self.mean[np.ix_(indices_to_keep, [0])]
        return Gaussian(
            cov=marginal_cov, mean=marginal_mean, log_weight=self.log_weight, var_names=marginal_var_names
        )

    def _destroy_canform(self):
        """
        Destroy the canonical form parameters.
        """
        self.prec, self.h_vec, self.h_vec = None, None, None
        self.canform = False

    def _destroy_covform(self):
        """
        Destroy the covariance form parameters.
        """
        self.cov, self.mean, self.log_weight = None, None, None
        self.covform = False

    def _update_canform(self):
        """
        Update the canonical form parameters of the Gaussian.
        """
        if self.canform:
            return
        assert self.covform
        self.prec = _factor_utils.inv_matrix(self.cov)
        self.h_vec = self.prec @ self.mean
        utku = self.mean.T @ self.prec @ self.mean

        det_2pi_cov = np.linalg.det(2.0 * np.pi * self.cov)
        updated_g_val = self.log_weight - 0.5 * utku - 0.5 * _factor_utils.log(det_2pi_cov)

        self.g_val = _factor_utils.make_scalar(updated_g_val)
        self.canform = True

    def _update_covform(self):
        """
        Update the covariance form parameters of the Gaussian.
        """
        if self._is_vacuous:
            raise Exception("cannot update covariance form for vacuous Gaussian.")
        if self.covform:
            return
        assert self.canform
        self.cov = _factor_utils.inv_matrix(self.prec)
        assert not np.isnan(np.sum(self.cov)), "Error: nan values in cov matrix after inversion."
        self.mean = self.cov @ self.h_vec
        utku = self.mean.T @ self.prec @ self.mean
        det_2_pi_cov = np.linalg.det(2.0 * np.pi * self.cov)
        log_weight_ = self.g_val + 0.5 * utku + 0.5 * np.log(det_2_pi_cov)
        self.log_weight = _factor_utils.make_scalar(log_weight_)
        self.covform = True

    def multiply(self, factor):
        """
        Multiply this Gaussian with another factor.

        :param Gaussian factor: the factor to multiply with
        :return: the resulting factor
        """
        # if isinstance(factor, NonLinearGaussian):
        #    return factor.multiply(self)
        return self._absorb_or_cancel(factor, operator.add)

    def divide(self, factor):
        """
        Divide this Gaussian by another factor.

        :param Gaussian factor: the factor to divide by
        :return: the resulting factor
        """
        return self._absorb_or_cancel(factor, operator.sub)

    def _absorb_or_cancel(self, factor, operator_function):
        """
        A general function which can either perform Gaussian multiplication or division (which are very similar).

        :param factor: the gaussian to multiply or divide by
        :param operator_function: the operator to use one the Gaussian canonical parameters
                        ('+' for multiplication and '-' for division)
        :return: the resulting Gaussian
        """
        prec_a = self.get_prec()
        prec_b = factor.get_prec()
        assert len(prec_a.shape) == 2
        assert len(prec_b.shape) == 2
        prec_c, new_vars_0 = _factor_utils.indexed_square_matrix_operation(
            prec_a, prec_b, self._var_names, factor.var_names, operator_function
        )
        g_a = self.get_g()
        g_b = factor.get_g()
        g_c = operator_function(g_a, g_b)

        h_a = self.get_h()
        h_b = factor.get_h()
        h_c, new_vars_1 = _factor_utils.indexed_column_vector_operation(
            h_a, h_b, self._var_names, factor.var_names, operator_function
        )
        assert new_vars_0 == new_vars_1
        return Gaussian(prec=prec_c, h_vec=h_c, g_val=g_c, var_names=new_vars_0)

    def sample(self, num_samples):
        """
        Draw samples from the Gaussian distribution.

        :param num_samples: The number of samples to draw.
        :type num_samples:
        :return: The samples.
        :rtype: int
        """
        std_gaussian_samples = np.random.normal(0, 1, [self.dim, num_samples])
        zero_mean_samples = std_gaussian_samples
        self._update_covform()
        chol_cov = np.linalg.cholesky(self.cov)
        samples = chol_cov @ zero_mean_samples + self.mean
        return samples

    def _get_observation_reduced_canonical_vars(self, observed_indices, unobserved_indices, observed_vec):
        """
        A helper function for reduce.

        :param observed_indices: The observed variable indices
        :type observed_indices: int list
        :param unobserved_indices: The unobserved variable indices
        :type unobserved_indices: int list
        :return: the reduced parameters prec_observed, h_observed, g_observed
        :rtype: numpy.ndarray, numpy.ndarray, float
        """
        prec = self.get_prec()
        h_vec = self.get_h()
        prec_reduced = 0
        h_reduced = 0
        if unobserved_indices:
            prec_xx = prec[np.ix_(unobserved_indices, unobserved_indices)]
            prec_reduced = prec_xx.copy()
            prec_xy = prec[np.ix_(unobserved_indices, observed_indices)]
            h_x = h_vec[np.ix_(unobserved_indices, [0])]
            h_reduced = h_x - prec_xy @ observed_vec

        prec_yy = prec[np.ix_(observed_indices, observed_indices)]
        h_y = h_vec[np.ix_(observed_indices, [0])]
        g_reduced = self.get_g() + h_y.T @ observed_vec - 0.5 * observed_vec.T @ prec_yy @ observed_vec
        return prec_reduced, h_reduced, g_reduced

    def reduce(self, vrs, values):
        """
        Observe a subset of the variables in the scope of this Gaussian and return the resulting factor.

        :param vrs: the names of the observed variable (list)
        :type vrs: str list
        :param values: the values of the observed variables
        :type values: vector-like
        :return: the resulting Gaussian
        :rtype: Gaussian
        """
        observed_vec = _factor_utils.make_column_vector(values)

        assert isinstance(vrs, list)  # just to future-proof interface
        assert set(vrs) <= set(self._var_names), "observed variables must a be subset of the gaussian variables."

        unobserved_vars = list(set(self._var_names) - set(vrs))
        unobserved_vars.sort()  # the above operations seems to return inconsistent orderings
        observed_indices = [self._var_names.index(v) for v in vrs]
        unobserved_indices = [self._var_names.index(v) for v in unobserved_vars]

        prec_reduced, h_reduced, g_reduced = self._get_observation_reduced_canonical_vars(
            observed_indices=observed_indices,
            unobserved_indices=unobserved_indices,
            observed_vec=observed_vec,
        )

        return Gaussian(prec=prec_reduced, h_vec=h_reduced, g_val=g_reduced, var_names=unobserved_vars)

    def distance_from_vacuous(self):
        """
        Get the Kullback-Leibler (KL) divergence between this factor and a uniform copy of it.

        :return: The KL divergence.
        :rtype: float
        """
        #  Note: here it does not matter if we take KL(P||Q) or KL(Q||P) the result is either 0.0 (if both are vacuous)
        #        or inf (if one is not).
        if self._is_vacuous:
            return 0.0
        return float("inf")

    def kl_divergence(self, factor, normalize_factor=True):
        """
        Get the KL-divergence D_KL(self || factor) between a normalized version of this factor and another factor.

        :param factor: The other factor
        :type factor: Gaussian
        :param normalize_factor: Whether or not to normalize the other factor before computing the KL-divergence.
        :type normalize_factor: bool
        :return: The Kullback-Leibler divergence
        :rtype: float
        """
        if self.dim != factor.dim:
            raise ValueError(
                "cannot calculate KL-divergence between Gaussians of different dimensionalities."
            )
        if self._is_vacuous and factor._is_vacuous:
            return 0.0
        if self._is_vacuous or factor._is_vacuous:
            return np.inf

        if self.equals(factor):
            return 0.0
        # TODO: can we compute the correct ('normalised') KL divergence without explicitly normalizing?
        normalized_self = self.normalize()
        factor_ = factor
        if normalize_factor:
            factor_ = factor.normalize()
        inv_cov_q = factor_.get_prec()
        inv_cov_p = normalized_self.get_prec()
        cov_p = normalized_self.get_cov()

        u_q = factor_.get_mean()
        u_p = normalized_self.get_mean()

        det_inv_cov_q = np.linalg.det(inv_cov_q)
        det_inv_cov_p = np.linalg.det(inv_cov_p)
        assert det_inv_cov_q != 0.0, "Unexpected factor covariance determinant of 0."
        det_term = 0.5 * cmath.log(det_inv_cov_p / det_inv_cov_q)
        trace_term = 0.5 * np.trace(inv_cov_q @ cov_p)
        mahalanobis_term = 0.5 * (u_p - u_q).T @ inv_cov_q @ (u_p - u_q)
        kld = det_term + trace_term + mahalanobis_term - 0.5 * normalized_self.dim
        # TODO: Add warning or error if this is negative and remove abs below
        return np.abs(kld[0][0])

    @property
    def is_vacuous(self):
        """
        Check if a Gaussian distribution contains no information. This is the case when the precision matrix is a zero
         matrix.

        :return: The result of the check.
        :rtype: Bool
        """

        if self._is_vacuous:
            return True
        if self.canform:
            if np.allclose(self.prec, 0.0):
                if not _factor_utils.is_pos_def(self.prec):
                    return True
        return False

    def copy(self):
        """
        Make a copy of this Gaussian.

        :return: The copied Gaussian.
        :rtype: Gaussian
        """

        if self.covform and self.canform:
            assert isinstance(self.g_val, (int, float))
            assert isinstance(self.log_weight, (int, float))
            gaussian_copy = Gaussian(
                cov=self.cov.copy(),
                mean=self.mean.copy(),
                log_weight=self.log_weight,
                var_names=copy.deepcopy(self._var_names),
            )
            gaussian_copy.prec = self.prec.copy()
            gaussian_copy.h_vec = self.h_vec.copy()
            gaussian_copy.g_val = self.g_val
            gaussian_copy.canform = True
            return gaussian_copy

        if self.covform:
            assert isinstance(self.log_weight, (int, float))
            return Gaussian(
                cov=self.cov.copy(),
                mean=self.mean.copy(),
                log_weight=self.log_weight,
                var_names=copy.deepcopy(self._var_names),
            )
        if self.canform:
            assert isinstance(self.g_val, (int, float))
            return Gaussian(
                prec=self.prec.copy(), h_vec=self.h_vec.copy(), g_val=self.g_val,
                var_names=copy.deepcopy(self._var_names)
            )
        raise Exception("Gaussian is neither in canonical form nor in covariance form?")

    def potential(self, x_val):
        """
        Get the value of the Gaussian potential at x_val.

        :param x_val: The vector (or vector-like object) to evaluate the Gaussian at
        :type x_val: numpy.ndarray
        :return: The value of the Gaussian potential at x_val.
        """
        return np.exp(self.log_potential(x_val))

    def log_potential(self, x_val, vrs=None):
        """
        Get the log of the value of the Gaussian potential at x_val.

        :param x_val: the vector (or vector-like object) to evaluate the Gaussian at
        :type x_val: vector-like
        :param vrs: The variables corresponding to the values in x_val.
        :type vrs: str list
        :return: The log of the value of the Gaussian potential at x_val.
        """
        if vrs is not None:
            assert set(vrs) == set(self.var_names)
            if isinstance(x_val, np.ndarray):
                x_val = x_val.ravel()
            x_val_list = list(x_val)
            assert len(x_val_list) == len(self.var_names)
            x_val = [x_val_list[vrs.index(v)] for v in self.var_names]
        x_vec = _factor_utils.make_column_vector(x_val)
        if self.covform:
            log_norm = self.log_weight - 0.5 * np.log(np.linalg.det(2.0 * np.pi * self.cov))
            prec = _factor_utils.inv_matrix(self.cov)
            exponent = -0.5 * (self.mean - x_vec).T @ prec @ (self.mean - x_vec)
            log_potx = log_norm + exponent
        if self.canform:
            log_potx = -0.5 * x_vec.T @ self.prec @ x_vec + x_vec.T @ self.h_vec + self.g_val
        return log_potx[0, 0]

    def _get_cov_repr_str(self):
        """
        Get the string representation for the covariance form parameters.

        :return: The parameter representation string.
        :rtype: str
        """
        self_copy = self.copy()
        self_copy._update_covform()
        np.set_printoptions(linewidth=np.inf)
        repr_str = (
                "cov        = \n"
                + str(self_copy.cov)
                + "\n"
                + "mean       = \n"
                + str(self_copy.mean)
                + "\n"
                + "log_weight = \n"
                + str(self_copy.log_weight)
                + "\n"
        )
        return repr_str

    def _get_can_repr_str(self):
        """
        Get the string representation for the canonical form parameters.

        :return: The parameter representation string.
        :rtype: str
        """
        self_copy = self.copy()
        self_copy._update_canform()
        np.set_printoptions(linewidth=np.inf)
        repr_str = (
                "prec = \n"
                + str(self_copy.prec)
                + "\n"
                + "h = \n"
                + str(self_copy.h_vec)
                + "\n"
                + "g = \n"
                + str(self_copy.g_val)
                + "\n"
                + "is_vacuous: "
                + str(self_copy._is_vacuous)
                + "\n"
        )
        return repr_str

    def __repr__(self):
        """
        Get the string representation of the Gaussian factor.

        :return: The factor representation string.
        :rtype: str
        """
        np.set_printoptions(edgeitems=3)
        np.set_printoptions(precision=4)
        np.core.arrayprint._line_width = 200
        repr_str = "vars = " + str(self.var_names) + "\n"
        if not self._is_vacuous:
            repr_str += self._get_can_repr_str()
        repr_str += self._get_cov_repr_str()
        return repr_str

    def show(self):
        """
        Print the parameters of the Gaussian distribution
        """
        np.set_printoptions(edgeitems=3)
        np.set_printoptions(precision=4)
        np.core.arrayprint._line_width = 200
        print("vars = ", self.var_names)
        if self.covform:
            print(self._get_cov_repr_str())
        if self.canform:
            print(self._get_can_repr_str())

    def show_vis(self, figsize=(10, 8)):
        """
        Visualize the parameters with plots.

        :param figsize: The figure size.
        :type figsize: 2 element int tuple
        """
        # TODO: find a way of making cov matrix square.
        _, [ax_cov, ax_mean] = plt.subplots(nrows=2, figsize=figsize)
        cov_df = pd.DataFrame(data=self.get_cov(), index=self.var_names, columns=self.var_names)
        mean_df = pd.DataFrame(data=self.get_mean(), index=self.var_names, columns=["var_names"])
        cbar_kws = dict(use_gridspec=False, location="top")
        sns.heatmap(cov_df, ax=ax_cov, cbar=True, cbar_kws=cbar_kws, annot=True)
        mean_df.plot.bar(ax=ax_mean, legend=False)
        plt.xticks(rotation=0)

    def _get_limits_for_2d_plot(self):
        """
        Get x and y limits which includes most of the factors mass, by considering
        the mean and variance of each Gaussian component.
        """
        self_copy = self.copy()
        self_copy._update_covform()
        x_lower = self_copy.mean[0, 0] - 3.0 * np.sqrt(self_copy.cov[0, 0])
        x_upper = self_copy.mean[0, 0] + 3.0 * np.sqrt(self_copy.cov[0, 0])
        y_lower = self_copy.mean[1, 0] - 3.0 * np.sqrt(self_copy.cov[1, 1])
        y_upper = self_copy.mean[1, 0] + 3.0 * np.sqrt(self_copy.cov[1, 1])
        return [x_lower, x_upper], [y_lower, y_upper]

    # TODO: reconcile with GaussianMixture _plot_2d
    def _plot_2d(self, log, x_lim=None, y_lim=None):
        """
        Plot a 2d Gaussian potential function

        :param log: if this is True, the log-potential will be plotted
        :param x_lim: the x limits to plot the function over (optional)
        :param y_lim: the y limits to plot the function over (optional)
        """
        xlim_default, ylim_default = self._get_limits_for_2d_plot()
        if x_lim is None:
            x_lim = xlim_default
        if y_lim is None:
            y_lim = ylim_default

        xlabel = self.var_names[0]
        ylabel = self.var_names[1]

        if not log:
            _factor_utils.plot_2d(func=self.potential, xlim=x_lim, ylim=y_lim, xlabel=xlabel, ylabel=ylabel)
        else:
            _factor_utils.plot_2d(func=self.log_potential, xlim=x_lim, ylim=y_lim, xlabel=xlabel, ylabel=ylabel)

    def plot(self, log=False, xlim=None, ylim=None):
        """
        Plot the Gaussian mixture potential function (only for 1d and 2d functions)

        :param log: if this is True, the log-potential will be plotted
        :param xlim: the x limits to plot the function over (optional)
        :type xlim: 2 element float list
        :param ylim: the y limits to plot the function over (optional and only used in 2d case)
        :type ylim: 2 element float list
        """
        # TODO: Replace with gaussian mixture plot.
        if self.dim == 1:
            if xlim is None:
                stddev = np.sqrt(self.get_cov()[0, 0])
                lower_bound = self.get_mean()[0, 0] - 3.0 * stddev
                upper_bound = self.get_mean()[0, 0] + 3.0 * stddev
                xlim = [lower_bound, upper_bound]
            if xlim is not None:
                x_lower = xlim[0]
                x_upper = xlim[1]
            num_points = 200
            x_series = np.linspace(x_lower, x_upper, num_points)
            if log:
                potx = np.array([self.log_potential(xi) for xi in x_series])
            else:
                potx = np.array([self.potential(xi) for xi in x_series])
            plt.plot(x_series, potx)
        elif self.dim == 2:
            self._plot_2d(log=log, x_lim=xlim, y_lim=ylim)
        else:
            raise NotImplementedError("Plotting not implemented for dim!=1.")

    # TODO: Generalise this to more than one dimensional cases.
    def _split_gaussian(self):
        """
        Split this factor into a three component Gaussian Mixture (with all components having different means) where the
        new mixture has the same mean and covariance as the original Gaussian.

        :return: The split Gaussian Mixture.
        :rtype: GaussianMixture
        """
        if self.dim != 1:
            raise NotImplementedError("Gaussian must be one dimensional.")
        weights = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
        full_cov = self.get_cov()
        full_mean = self.get_mean()

        covs = [weight * full_cov for weight in weights]
        means = [full_mean - np.sqrt(full_cov), full_mean, full_mean + np.sqrt(full_cov)]

        gaussians = []
        for mean, cov, weight in zip(means, covs, weights):
            gaussian = Gaussian(cov=cov, mean=mean, log_weight=np.log(weight), var_names=self.var_names)
            gaussians.append(gaussian)

        return gm.GaussianMixture(gaussians)


class GaussianTemplate(FactorTemplate):
    """
    A class for specifying Gaussian factor templates and creating categorical factors from these templates.
    """

    def __init__(self, gaussian_parameters, var_templates):
        """
        Create a Categorical factor template.

        :param gaussian_parameters: The cononical Gaussian parameters (see example below)
        :type gaussian_parameters: str to np.array/float dict
        :param var_templates: A list of formattable strings.
        :type var_templates: str list

        >>>gaussian_parameters = {'prec': np.array([[1,0],[0,1]]),
        >>>                       'h': np.array([[0],[1]]),
        >>>                       'g': 0}
        """

        super().__init__(var_templates=var_templates)
        self.prec = gaussian_parameters["prec"]
        self.h_vec = gaussian_parameters["h"]
        self.g_val = gaussian_parameters["g"]

    def make_factor(self, format_dict=None, var_names=None):
        """
        Make a factor with var_templates formatted by format_dict to create specific var names.

        :param format_dict: The dictionary to be used to format the var_templates strings.
        :type format_dict: str dict
        :param var_names: The variable names.
        :type var_names: str list
        :return: The instantiated factor.
        :rtype: Gaussian
        """
        if format_dict is not None:
            assert var_names is None
            var_names = [vt.format(**format_dict) for vt in self._var_templates]
        # TODO: remove this and find better solution
        g_val = Gaussian(prec=self.prec.copy(), h_vec=self.h_vec.copy(), g_val=self.g_val, var_names=var_names)
        g_val._is_vacuous = True
        return g_val
