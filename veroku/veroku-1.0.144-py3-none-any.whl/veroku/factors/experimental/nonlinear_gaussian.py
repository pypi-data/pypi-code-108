"""
A module for instantiating and performing operations on Non-linear Gaussian functions.
"""

# Standard imports
import operator
import copy

# Third-party imports
import numpy as np

# Local imports
from veroku.factors import _factor_utils
from veroku.factors._sigma_points import get_sigma_points_array, sigma_points_array_to_joint_params
from veroku.factors._factor import Factor
from veroku.factors.gaussian import Gaussian
from veroku.factors.experimental.gaussian_mixture import GaussianMixture
from veroku.factors._factor_utils import (
    make_square_matrix,
    indexed_square_matrix_operation,
    format_list_elements,
)
from veroku.factors._factor_template import FactorTemplate
from veroku._constants import DEFAULT_FACTOR_RTOL, DEFAULT_FACTOR_ATOL


# TODO: see that lazy evaluation (recompute joint) is done sensibly and consistently

# pylint: disable=protected-access


class NonLinearGaussian(Factor):
    """
    A Class for instantiating and performing operations on multivariate Gaussian mixture functions.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self,
                 conditioning_vars,
                 conditional_vars,
                 transform,
                 noise_cov,
                 log_weight=0.0,
                 joint_distribution=None,
                 conditional_update_factor=None,
                 conditioning_factor=None,
                 observed_evidence=None):
        """
        The initializer.

        :param list conditioning_vars: The conditioning vars.
        :param list conditional_vars: The conditioning vars.
        :param transform: The transformation that links the conditioning to the conditional distribution
        :param noise_cov: The noise covariance matrix of the zero mean Gaussian noise.
        :param Gaussian conditional_update_factor: A factor, with same scope, subset of, the conditional vars, to be
            multiplied with the transformed (joint) distribution to form the final joint distribution.
        :param Gaussian conditioning_factor: The factor with scope less than or equals to the conditional variables to be
            transformed by the transform. If the scope is less than the conditional variables set, observed evidence
            (if available) can be used to still enable the successful transformation and calculation of the joint.
        :param dict observed_evidence: A dictionary mapping variable names ot observed values.
        """
        if len(set(conditioning_vars).intersection(conditional_vars)) != 0:
            raise ValueError("variable overlap between conditioning_vars and conditional_vars.")
        var_names = conditioning_vars + conditional_vars

        super().__init__(var_names=var_names)
        self.transform = transform
        if noise_cov.shape[0] != len(conditional_vars):
            raise ValueError(
                "noise_cov rows and columns should correspond to the number of conditional variables"
            )
        self.noise_cov = make_square_matrix(noise_cov)

        self.log_weight = log_weight
        self.conditioning_vars = conditioning_vars.copy()
        self.conditional_vars = conditional_vars.copy()

        self.conditioning_factor = None
        if conditioning_factor is not None:
            self.conditioning_factor = conditioning_factor.copy()

        self.conditional_update_factor = None
        if conditional_update_factor is not None:
            self.conditional_update_factor = conditional_update_factor.copy()

        if joint_distribution is not None:
            self._joint_distribution = joint_distribution.copy()
        else:
            self._joint_distribution = Gaussian.make_vacuous(var_names)
        if observed_evidence is None:
            self.observed_evidence = {}
        else:
            self.observed_evidence = copy.deepcopy(observed_evidence)

    def equals(self, factor, rtol=DEFAULT_FACTOR_RTOL, atol=DEFAULT_FACTOR_ATOL):
        """
        Check if this factor is the same as another factor.

        :param factor: The other factor to compare to.
        :type factor: Gaussian
        :return: The result of the comparison.
        :rtype: bool
        """
        return self._joint_distribution.equals(factor, rtol=rtol, atol=atol)

    def distance_from_vacuous(self):
        """
        NOTE: Not Implemented yet.
        Get the Kullback-Leibler (KL) divergence between the message factor and a vacuous (uniform) version of it.

        :return: The KL-divergence
        """
        raise NotImplementedError('This function has not been implemented yet.')

    def kl_divergence(self, factor):
        """
        NOTE: Not Implemented yet.
        Get the KL-divergence D_KL(self || factor) between a normalized version of this factor and another factor.

        :param factor: The other factor
        :type factor: GaussianMixture
        :return: The Kullback-Leibler divergence
        :rtype: float
        """
        raise NotImplementedError('This function has not been implemented yet.')

    def copy(self):
        """
        Make a copy of the factor.

        :return: the copy
        :rtype: NonLinearGaussian
        """
        nlg_copy = NonLinearGaussian(
            conditioning_vars=copy.deepcopy(self.conditioning_vars),
            conditional_vars=copy.deepcopy(self.conditional_vars),
            transform=copy.deepcopy(self.transform),
            noise_cov=copy.deepcopy(self.noise_cov),
            log_weight=self.log_weight,
            joint_distribution=self._joint_distribution,
            conditional_update_factor=self.conditional_update_factor,
            conditioning_factor=self.conditioning_factor,
            observed_evidence=self.observed_evidence,
        )
        return nlg_copy

    @property
    def joint_distribution(self):
        """
        The joint distribution.

        :return: the joint distribution
        """
        self_copy = self.copy()
        self_copy._recompute_joint()
        return self_copy._joint_distribution

    def get_prec(self):
        """
        Get the K matrix (after ensuring that the canonical form is updated.)

        :return: The K parameter.
        """
        self._recompute_joint()
        return self._joint_distribution.get_prec()

    def get_h(self):
        """
        Get the log h vector (after ensuring that the canonical form is updated.)

        :return: The h parameter.
        """
        self._recompute_joint()
        return self._joint_distribution.get_h()

    def get_g(self):
        """
        Get the g scalar (after ensuring that the canonical form is updated.)

        :return: The g parameter.
        """
        self._recompute_joint()
        return self._joint_distribution.get_g()

    def get_cov(self):
        """
        Get the covariance matrix (after ensuring that the covariance form is updated.)

        :return: The cov parameter.
        """
        self._recompute_joint()
        return self._joint_distribution.get_cov()

    def get_mean(self):
        """
        Get the mean vector (after ensuring that the covariance form is updated.)

        :return: The mean parameter.
        """
        self._recompute_joint()
        return self._joint_distribution.get_mean()

    def get_log_weight(self):
        """
        Get the log weight (after ensuring that the covariance form is updated.)

        :return: The log_weight parameter.
        """
        self._recompute_joint()
        return self._joint_distribution.get_log_weight()

    def add_log_weight(self, log_weight_to_add):
        """
        Add a log weight to the factor.

        :param log_weight_to_add: The log weight to add.
        """
        self.log_weight += log_weight_to_add

    def _recompute_joint(self):
        """
        Recompute the joint distribution.
        """
        # TODO: improve this function (after code coverage is completed for this class) and remove disable below.
        # pylint: disable=too-many-locals
        observed_vars = list(self.observed_evidence.keys())

        conditioning_observed_vars = [var for var in observed_vars if var in self.conditioning_vars]
        conditioning_observed_values = [
            self.observed_evidence[var] for var in observed_vars if var in self.conditioning_vars
        ]

        conditional_observed_vars = [var for var in observed_vars if var in self.conditional_vars]
        conditional_observed_values = [
            self.observed_evidence[var] for var in observed_vars if var in self.conditional_vars
        ]

        # under 3 conditions we can successfully perform the transformation:
        # 1. We have a well defined conditional distribution with the full scope of the conditional variables.
        # 2. All the conditional variables are observed.
        # 3. We have a conditional distribution over a subset of the conditional variables and the rest of the
        # conditional variables are observed.

        # Initial feasibility check
        conditioning_factor_var_names = []
        if self.conditioning_factor is not None:
            conditioning_factor_var_names = self.conditioning_factor.var_names
        vars_obs_vars_union = set(conditioning_factor_var_names).union(set(conditioning_observed_vars))
        if vars_obs_vars_union != set(self.conditioning_vars):
            # The conditioning_factor variables and observed conditional variables combined do not make up a
            # complete set - so we cannot calculate the transform.
            self._joint_distribution = Gaussian.make_vacuous(self.var_names)
            return

        # If we are still here, there we can calculate the transformation.
        conditioning_factor_sigma_points_array = np.expand_dims(np.array([]), axis=0).T  # empty dummy for generalisation
        if self.conditioning_factor is not None:
            conditioning_factor = self.conditioning_factor.copy()
            cond_factor_observed_vars = list(set(observed_vars).intersection(conditioning_factor.var_names))
            cond_factor_observed_values = [self.observed_evidence[var] for var in cond_factor_observed_vars]

            if len(cond_factor_observed_vars) > 0:
                conditioning_factor = conditioning_factor.reduce(
                    vrs=cond_factor_observed_vars, values=cond_factor_observed_values
                )

            conditioning_factor_sigma_points_array = get_sigma_points_array(conditioning_factor)

        # extend sigma points with observed variable values
        if len(conditioning_observed_vars) > 0:
            observed_vec = _factor_utils.make_column_vector(conditioning_observed_values)
            tiled_observed_vec = np.tile(observed_vec, [1, conditioning_factor_sigma_points_array.shape[1]])
            extended_sigma_points_array = np.concatenate([tiled_observed_vec, conditioning_factor_sigma_points_array])
            extended_sigma_point_vars = conditioning_observed_vars + conditioning_factor.var_names
        else:
            extended_sigma_points_array = conditioning_factor_sigma_points_array
            extended_sigma_point_vars = conditioning_factor.var_names

        # TODO: Add conditional var_names here somehow. We need to ensure that the correct variables are used
        # in the correct place in the transformation. In the past, we have simply done this by standardising
        # on the variable indices in different place, but this is probably not very safe.
        joint_cov, joint_mean = sigma_points_array_to_joint_params(sigma_points_array=extended_sigma_points_array,
                                                                   transform=self.transform,
                                                                   var_names=extended_sigma_point_vars)
        if (joint_mean.shape[0] != len(self.var_names)) or (joint_cov.shape[0] != len(self.var_names)):
            raise AssertionError("Transform resulted in incorrect number of variables.")

        # remove the observed vars again after transformation
        nov = len(conditioning_observed_vars)  # number of observed vars
        joint_cov = joint_cov[nov:, nov:]
        joint_mean = joint_mean[nov:, :]
        joint_var_names = conditioning_factor.var_names + self.conditional_vars

        joint_cov_plus_noise, joint_vars = indexed_square_matrix_operation(
            joint_cov, self.noise_cov, joint_var_names, self.conditional_vars, operator.add
        )
        joint_log_weight = self.log_weight + conditioning_factor.log_weight
        self._joint_distribution = Gaussian(cov=joint_cov_plus_noise,
                                            mean=joint_mean,
                                            log_weight=joint_log_weight,
                                            var_names=joint_vars,
        )
        if self.conditional_update_factor is not None:
            self._joint_distribution = self._joint_distribution.multiply(self.conditional_update_factor)
        if len(conditional_observed_vars) > 0:
            self._joint_distribution = self._joint_distribution.reduce(
                conditional_observed_vars, conditional_observed_values
            )

    def normalize(self):
        """
        Normalize the factor.

        :return: The normalized factor.
        :rtype: Gaussian
        """
        # TODO: make this more efficient
        return self.joint_distribution.normalize()

    def multiply(self, factor):
        """
        Multiply this factor with another factor.

        :param factor: the factor to multiply with
        :return: the resulting factor
        :rtype: NonLinearGaussian
        """

        if isinstance(factor, GaussianMixture):
            nlgs = []
            for gaussian_factor in factor.components:
                nlgs.append(self.multiply(gaussian_factor))
            return NonLinearGaussianMixture(nlgs)

        self_copy = self.copy()
        if isinstance(factor, NonLinearGaussian):
            raise NotImplementedError(
                "Multiplication of two nonlinear-Gaussian factors has not been implemented."
            )
        if factor._is_vacuous:
            # TODO: check this (esp to see what to do with)
            return self_copy
        # TODO: change to 'update conditional model and re-transform model' (if correct)
        if not isinstance(factor, Gaussian):
            raise ValueError(f"factor must be Gaussian, got {type(factor)}")

        if set(factor.var_names) <= set(self_copy.conditional_vars):
            if self_copy.conditional_update_factor is None:
                self_copy.conditional_update_factor = factor.copy()
            else:
                self_copy.conditional_update_factor = self_copy.conditional_update_factor.multiply(factor)
        elif set(factor.var_names) <= set(self_copy.conditioning_vars):
            if self_copy.conditioning_factor is None:
                self_copy.conditioning_factor = factor.copy()
            else:
                self_copy.conditioning_factor = self_copy.conditioning_factor.multiply(factor)
        else:
            raise ValueError(
                f"cannot absorb factor with scope ({factor.var_names}) \n "
                f"           which has neither conditional ({self_copy.conditioning_vars}) \n "
                f"           nor conditioning ({self_copy.conditional_vars}) scope."
            )
        return self_copy

    def divide(self, factor):
        """
        Divide this factor by another factor.

        :param factor: the factor divide by
        :return: the resulting factor
        :rtype: NonLinearGaussian
        """
        self_copy = self.copy()
        if factor._is_vacuous:
            # TODO: check this (esp to see what to do with)
            return self_copy
        # TODO: change to 'update conditional model and re-transform model' (if correct)
        if not isinstance(factor, Gaussian):
            raise ValueError("factor must be Gaussian.")

        if set(factor.var_names) <= set(self_copy.conditional_vars):
            self_copy.conditional_update_factor = self_copy.conditional_update_factor.divide(factor)
        elif set(factor.var_names) <= set(self_copy.conditioning_vars):
            if self_copy.conditioning_factor is None:
                raise NotImplementedError()
            self_copy.conditioning_factor = self_copy.conditioning_factor.divide(factor)
        else:
            raise ValueError(
                f"cannot cancel factor with scope ({factor.var_names}) \n "
                f"           which has neither conditional ({self_copy.conditioning_vars}) \n "
                f"           nor conditioning ({self_copy.conditional_vars}) scope."
            )
        self_copy._recompute_joint()
        return self_copy

    def reduce(self, vrs, values):
        """
        Observe a subset of the variables in the scope of this factor and return the resulting factor.

        :param vrs: the names of the observed variable (list)
        :param values: the values of the observed variables (list or vector-like object)
        :return: the resulting factor
        :rtype: NonLinearGaussian
        """

        self_copy = self.copy()
        evidence_dict = dict(zip(vrs, values))
        self_copy.observed_evidence.update(evidence_dict)
        return self_copy

    def marginalize(self, vrs, keep=True):
        """
        Integrate out variables from this factor.

        :param vrs: (list) a subset of variables in the factor's scope
        :param keep: Whether to keep or sum out vrs
        :return: the resulting marginal
        :rtype: Gaussian
        """

        vrs_to_keep = super().get_marginal_vars(vrs, keep=keep)
        assert set(vrs_to_keep) <= set(self.var_names), "Error: asked to keep vars not in factor."
        self_copy = self.copy()
        self_copy._recompute_joint()
        if self_copy._joint_distribution._is_vacuous:
            if set(vrs_to_keep) <= set(self_copy.conditioning_vars):
                if self_copy.conditioning_factor is not None:
                    if set(vrs_to_keep) <= set(self_copy.conditioning_factor.var_names):
                        marginal = self_copy.conditioning_factor.marginalize(vrs_to_keep, keep=True)
                        return marginal
            if set(vrs_to_keep) <= set(self_copy.conditional_vars):
                if self_copy.conditional_update_factor is not None:
                    if set(vrs_to_keep) <= set(self_copy.conditional_update_factor.var_names):
                        marginal = self_copy.conditional_update_factor.marginalize(vrs_to_keep, keep=True)
                        marginal._add_log_weight(self.log_weight)
                        return marginal
            else:
                return Gaussian.make_vacuous(vrs_to_keep)
        return self_copy._joint_distribution.marginalize(vrs_to_keep, keep=True)

    def sample(self, num_samples):
        """
        Draw samples from the Gaussian joint distribution defined by the non-linear Gaussian and the factors that have
        (potentially) been multiplied with it.

        :param num_samples: The number of samples to draw.
        :type num_samples:
        :return: The samples.
        :rtype: int
        """
        self._recompute_joint()
        return self._joint_distribution.sample(num_samples=num_samples)

    def show(self):
        """
        Print the parameters of the nonlinear Gaussian distribution.
        """
        # TODO: add __repr__ function and use here.
        print("Non-linear Gaussian")
        print("conditioning variables:", self.conditioning_vars)
        print("conditional variables:", self.conditional_vars)
        print("transform: ", self.transform)
        print("noise covariance = \n", self.noise_cov)
        print("joint_distribution = \n")
        if self._joint_distribution is not None:
            self._recompute_joint()
            self._joint_distribution.show()

        print("conditional update distribution = \n")
        if self.conditional_update_factor is not None:
            self.conditional_update_factor.show()
        else:
            print("vacuous")

        print("conditioning distribution = \n")
        if self.conditioning_factor is not None:
            self.conditioning_factor.show()
        else:
            print("vacuous")

    def plot(self):
        """
        Plot the joint distribution.
        """
        self_copy = self.copy()
        self_copy._recompute_joint()
        self._joint_distribution.plot()


class NonLinearGaussianMixture(Factor):
    """
    A Class for instantiating and performing operations on multivariate Gaussian mixture functions.
    """

    def __init__(self, factors, split_singles_before_absorb=True):
        """
        The initializer.

        :param factors: The list of factors.
        :type factors: NonLinearGaussian factor list
        :param bool split_singles_before_absorb: Whether or not to split a Gaussian (or single component
            GaussianMixture) before it is multiplied in. This can result in a better approximation of non-linear
            Gaussian transformations.
        """
        self.nlgs = []
        if len(factors) == 0:
            raise ValueError("received empty list of factors.")
        super().__init__(var_names=factors[0].var_names)
        for factor in factors:
            if not isinstance(factor, NonLinearGaussian):
                raise TypeError(f"expected NonLinearGaussian type, received {type(factor)}.")
            if not set(self.var_names) == set(factor.var_names):
                raise ValueError(
                    f"Inconsistent variable names. First factor has var_names = {self.var_names},"
                    f" another has var_names = {factor.var_names}"
                )
            self.nlgs.append(factor.copy())
        self.split_singles_before_absorb = split_singles_before_absorb

    def normalize(self):
        """
        Normalise the factor (not yet implemented).
        """
        raise NotImplementedError()

    def copy(self):
        """
        Make a copy of this factor.

        :return: the factor
        :rtype: NonLinearGaussianMixture
        """
        return NonLinearGaussianMixture(self.nlgs)

    @property
    def joint_distribution(self):
        gaussian_joints = []
        for nlg in self.nlgs:
            gaussian_joints.append(nlg.joint_distribution)
        return GaussianMixture(gaussian_joints)

    def multiply(self, factor):
        """
        Multiply this factor with another factor.

        :param factor: the factor to multiply with
        :return: the resulting factor
        :rtype: NonLinearGaussianMixture
        """
        if isinstance(factor, GaussianMixture):
            gm_factor = factor
        elif isinstance(factor, Gaussian):
            gm_factor = GaussianMixture([Gaussian])
        else:
            raise NotImplementedError()

        # TODO: Generalise the Gaussian.split_gaussian function to more than one dimensional cases and remove the
        #  limitation here
        if self.split_singles_before_absorb and len(gm_factor.var_names) == 1:
            if len(gm_factor.components) == 1:
                gm_factor = gm_factor.components[0]._split_gaussian()

        new_nlgs = []
        for gauss in gm_factor.components:
            for nlg in self.nlgs:
                new_nlgs.append(nlg.multiply(gauss))
        return NonLinearGaussianMixture(new_nlgs)

    def divide(self, factor):
        """
        Divide this factor by another factor.

        :param factor: the factor divide by
        :return: the resulting factor
        :rtype: NonLinearGaussianMixture
        """
        if isinstance(factor, Gaussian):
            gaussian_factor = factor
        elif isinstance(factor, GaussianMixture):
            # TODO: Add better Gaussian mixture division approximation
            gaussian_factor = factor.moment_match_to_single_gaussian()
        else:
            raise NotImplementedError("cannot divide NonLinearGaussianMixture by {type(factor)}.")
        new_nlgs = []
        for nlg in self.nlgs:
            new_nlgs.append(nlg.divide(gaussian_factor))
        return NonLinearGaussianMixture(new_nlgs)

    def reduce(self, vrs, values):
        """
        Observe a subset of the variables in the scope of this factor and return the resulting factor.

        :param vrs: the names of the observed variable (list)
        :param values: the values of the observed variables (list or vector-like object)
        :return: the resulting factor
        :rtype: NonLinearGaussianMixture
        """
        new_nlgs = []
        for nlg in self.nlgs:
            new_nlgs.append(nlg.reduce(vrs, values))
        return NonLinearGaussianMixture(new_nlgs)

    def marginalize(self, vrs, keep=True):
        """
        Integrate out variables from this factor.

        :param vrs: (list) a subset of variables in the factor's scope
        :param keep: Whether to keep or sum out vrs
        :return: the resulting marginal
        :rtype: NonLinearGaussianMixture
        """
        new_nlgs = []
        for nlg in self.nlgs:
            new_nlgs.append(nlg.marginalize(vrs, keep))
        return NonLinearGaussianMixture(new_nlgs)

    def sample(self, num_samples):
        """
        Draw samples from the Gaussian mixture joint distribution defined by the non-linear Gaussians and the factors
        that have (potentially) been multiplied with them.

        :param num_samples: The number of samples to draw.
        :type num_samples:
        :return: The samples.
        :rtype: int
        """

        # TODO: fix incorrect num samples issue
        sample_sets = []
        for nlg in self.nlgs:
            samples = nlg.sample(num_samples)
            sample_sets.append(samples)
        return np.concatenate(sample_sets)

    def plot(self):
        """
        Plot the joint Gaussian Mixture distribution.
        """
        gaussian_components = [nlg.joint_distribution for nlg in self.nlgs]
        gaussian_mixture = GaussianMixture(gaussian_components)
        gaussian_mixture.plot()

    def show(self):
        """
        Print the parameters of the nonlinear Gaussian distribution.
        """
        for i, nlg in enumerate(self.nlgs):
            print(f"######### NLG {i} #############################")
            nlg.show()


class NonLinearGaussianTemplate(FactorTemplate):
    """
    A template class for NonLinearGaussian factors.
    """

    def __init__(self, conditioning_var_templates, conditional_var_templates, transition_function, noise_cov):
        """
        The initializer.

        :param conditioning_var_templates: The list of formattable strings for the conditioning variables (i.e: ['var_a{i}_{t}', 'var_b{i}_{t}'])
        :param conditional_var_templates: The list of formattable strings for the conditional variables (i.e: ['var_c{i}_{t}', 'var_d{i}_{t}'])
        :param conditioning_var_templates: The formattable strings for the conditioning variables.
        :type conditioning_var_templates: str list
        :param conditional_var_templates: The formattable strings for the conditioning variables.
        :type conditional_var_templates: str list
        :param callable transition_function: The function that specifies the non-linear transform. This function takes
            2 parameters, a vector-like value to be transformed and the variable names list specifying the names of the
            variable elements of the value vector (i.e transition_function = lamda x, var_names: np.square(x)).
            The variable names do not need to be used, but can be useful in certain cases where functions need to be
            applied to specific variables.
        :param noise_cov: The noise covariance matrix of the additive noise random variable.
        """

        super().__init__(
            conditioning_var_templates=conditioning_var_templates,
            conditional_var_templates=conditional_var_templates,
        )
        self.transition_function = transition_function
        self.noise_cov = noise_cov

    def make_factor(self, format_dict=None, conditioning_vars=None, conditional_vars=None):
        """
        Make a factor with var_templates formatted by format_dict to create specific var names.

        :param format_dict: The dictionary to be used to format the var_templates strings.
        :type format_dict: str dict
        :param conditioning_vars: The conditioning variables strings.
        :type conditioning_vars: str list
        :param conditional_vars: The conditioning variables strings.
        :type conditional_vars: str list
        :return: The instantiated factor.
        :rtype: NonLinearGaussianMixture
        """
        if format_dict is not None:
            assert conditioning_vars is None
            assert conditioning_vars is None

            conditioning_vars = format_list_elements(self._conditioning_var_templates, format_dict)
            conditional_vars = format_list_elements(self._conditional_var_templates, format_dict)

        return NonLinearGaussian(
            conditioning_vars,
            conditional_vars,
            self.transition_function,
            self.noise_cov,
            log_weight=0.0,
            joint_distribution=None,
        )
