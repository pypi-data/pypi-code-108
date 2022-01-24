"""
A module for factorised factor functionality
"""

from veroku.factors._factor import Factor
from veroku.factors._factor_utils import get_subset_evidence
from veroku._constants import DEFAULT_FACTOR_RTOL, DEFAULT_FACTOR_ATOL

# TODO: This class in very much a work in progress. This needs to be completed. We must think especially carefully about
#   how we multiply factors when we have special factors such as nonlinear Gaussian factors in the factorised factor.
#   Currently this class is mostly focussed on factorised Gaussians.

# pylint: disable=protected-access


class FactorizedFactor(Factor):
    """
    A factorised factor class that allows factors to be used in factorised form - a product of other factors.
    This is useful for improving efficiency between factor multiplication and marginalisation. It also allows the
    for a efficient and intuitive representation of independent factors (especially factors with disjoint scopes).
    """

    # TODO: see how this is used in practice and investigate what the best way is to treat the variable name parameters.
    def __init__(self, factors):
        """
        The initializer.

        :param factors: The list of factors that will be implicitly multiplied.
        """
        assert all([not isinstance(factor, FactorizedFactor) for factor in factors])
        factors_var_name_lists = [factor.var_names for factor in factors]
        factors_var_name = list({var_name for sublist in factors_var_name_lists for var_name in sublist})
        super().__init__(var_names=factors_var_name)
        self.factors = []
        for factor in factors:
            if isinstance(factor, FactorizedFactor):
                self.factors += [f.copy() for f in factor.factors]
            else:
                self.factors.append(factor.copy())

    @property
    def joint_distribution(self):
        """
        The joint distribution.
        """
        if len(self.factors) == 0:
            raise ValueError("FactorisedFactor has no factors.")
        joint_distribution = self.factors[0].copy()
        for factor in self.factors[1:]:
            joint_distribution = joint_distribution.multiply(factor)
        return joint_distribution

    def copy(self):
        """
        Copy this factorised factor.

        :return: the copied factor
        :rtype: FactorizedFactor
        """
        factor_copies = []
        for factor in self.factors:
            factor_copies.append(factor.copy())
        return FactorizedFactor(factor_copies)

    def multiply(self, factor):
        """
        Multiply by another factor.

        :param factor: any type of factor.
        :return: the resulting factor
        :rtype: FactorizedFactor
        """
        # TODO: add preference for factors with conditioning scope? Not sure if practically necessary,
        #  but would be best.
        factorised_factor_copy = self.copy()
        index = factorised_factor_copy._first_factor_with_vars_index(factor.var_names)
        if index is not None:
            factorised_factor_copy.factors[index] = factorised_factor_copy.factors[index].multiply(factor)
        else:
            factorised_factor_copy.factors.append(factor)
        return factorised_factor_copy

    def divide(self, factor):
        """
        Divide out a general factor.

        :param factor: any type of factor.
        :return: the resulting factor
        :rtype: FactorizedFactor
        """
        factorised_factor_copy = self.copy()
        index = factorised_factor_copy._first_factor_with_vars_index(factor.var_names)

        for i, factorised_comp in enumerate(self.factors):
            if factorised_comp.equals(factor):
                if len(self.factors) > 1:
                    del factorised_factor_copy.factors[i]
                    return factorised_factor_copy
                # TODO: add else to make general vacuous factor (wont necessarily be Gaussian)
        if index is not None:
            factorised_factor_copy.factors[index] = factorised_factor_copy.factors[index].divide(factor)
        else:
            raise Exception("Error: Cannot divide factor with disjoint scope.")
        return factorised_factor_copy

    @property
    def is_vacuous(self):
        """
        Check if the factor is vacuous (i.e uniform).

        :return: The result of the check.
        :rtype: Bool
        """
        all_vacuous = all([factor._is_vacuous for factor in self.factors])
        if all_vacuous:
            return True
        none_vacuous = all([not factor._is_vacuous for factor in self.factors])
        if none_vacuous:
            return False
        # TODO: implement this
        raise NotImplementedError()

    def distance_from_vacuous(self):
        """
        Get the Kullback-Leibler (KL) divergence between this factor and a uniform copy of it.

        :return: The KL divergence.
        :rtype: float
        """
        # TODO: improve this
        return self.joint_distribution.distance_from_vacuous()

    def kl_divergence(self, factor):
        """
        Get the KL-divergence D_KL(self || factor) between a normalized version of this factor and another factor.

        :param factor: The other factor
        :type factor: Factor
        :return: The Kullback-Leibler divergence
        :rtype: float
        """
        # TODO: Make this more efficient.
        return self.joint_distribution.kl_divergence(factor)

    @property
    def num_factors(self):
        """
        Get the number of factors in the factorised factor.

        :return: The number of factors.
        :rtype: int
        """
        return len(self.factors)

    def normalize(self):
        """
        Normalize the factor.

        :return: The normalized factor.
        """
        factor_copy = self.copy()
        factor_copy._merge_dependent_factors()
        for i, factor_i in enumerate(factor_copy.factors):
            factor_copy.factors[i] = factor_i.normalize()
        return factor_copy

    def marginalize(self, vrs, keep=True):
        """
        Marginalize out a subset of the variables in this factor's scope.

        :param list vrs: the variable names
        :param bool keep: whether to keep or sum (or integrate) out these variables.
        :return: the resulting marginal
        :rtype: FactorisedFactor
        """
        # TODO: resolve this: Non-linear Gaussian factors can cause a problem here when there is enough information
        #   that they all should be well defined, but the information resides in only one of them for instance. This
        #   information takes the form of the observed evidence and the conditioning factors.

        vars_to_keep = super().get_marginal_vars(vrs, keep)
        vars_to_integrate_out_set = set(self.var_names) - set(vars_to_keep)
        factors_in_keep_scope_indices = self._all_intersecting_factors_indices(vars_to_keep)
        if not factors_in_keep_scope_indices:
            raise Exception("cannot marginalize out all variables from FactorisedFactor.")

        factor_marginals = []
        self_copy = self.copy()
        additional_log_weight = 0.0
        self_copy._merge_factors_with_shared_scope(vars_to_integrate_out_set)
        for factor in self_copy.factors:
            factor_vars_to_integrate_out_set = set(factor.var_names).intersection(vars_to_integrate_out_set)
            if factor_vars_to_integrate_out_set == set(factor.var_names):
                additional_log_weight += factor.get_log_weight()
            else:
                factor_vars_to_integrate_out = list(factor_vars_to_integrate_out_set)
                factor_marginal = factor.marginalize(factor_vars_to_integrate_out, keep=False)
                factor_marginals.append(factor_marginal)
        factor_marginals[0]._add_log_weight(additional_log_weight)
        if len(factor_marginals) == 1:
            return factor_marginals[0]
        marginal_factor = FactorizedFactor(factor_marginals)
        return marginal_factor

    # TODO: make these more efficient by storing joint_distribution
    # TODO: Consider removing or changing this since it will not generalise to cases where the join distribution is not
    #  Gaussian
    def get_cov(self):
        """
        Get the covariance matrix of the joint distribution (if Gaussian).

        :return: The cov parameter.
        :rtype: numpy.ndarray
        """
        return self.joint_distribution.get_cov()

    def get_mean(self):
        """
        Get the mean vector of the joint distribution (if Gaussian).

        :return: The mean parameter.
        :rtype: numpy.ndarray
        """
        return self.joint_distribution.get_mean()

    def _merge_dependent_factors(self):
        """
        Merge all factors (by multiplying) that have overlapping scopes.

        :return: The factor containing the reduced set of factors.
        :rtype: FactorizedFactor
        """
        # TODO: Add tests for this function
        merged_factors = []
        already_merged_factor_indices = []
        for i, factor_i in enumerate(self.factors):
            factor_i_merged = factor_i.copy()
            for j in range(i + 1, len(self.factors)):
                factor_j = self.factors[j]
                if j not in already_merged_factor_indices:
                    if set(factor_i.var_names).intersection(set(factor_j.varnames)) > 0:
                        factor_i_merged = factor_i_merged.multiply(factor_j)
                        already_merged_factor_indices.append(j)
            merged_factors.append(factor_i_merged)
        return FactorizedFactor(merged_factors)

    def _merge_factors_with_shared_scope(self, vrs_set):
        """
        Merge all factors in groups that all contain variables in vrs and have overlap within these subsets. This
        function will typically be used to ensure that all factors containing variables that need to be marginalised out
        are merged together into disjoint (in terms of the integrand variables) factors, so that these larger factors
        can be marginalised independently.

        :param vrs_set: The common scope variables to be considered to determine 'dependent' factors.
        :type vrs_set: str list
        """
        observed_factor_vars_list = []

        for factor in self.factors:
            observed_factor_vars = set(factor.var_names).intersection(vrs_set)
            observed_factor_vars_list.append(observed_factor_vars)

        merged_factors = []
        merged_factors_indices = []
        for i, observed_factor_i_vars in enumerate(observed_factor_vars_list):
            if i not in merged_factors_indices:
                merged_factor = self.factors[i]
                for j in range(i + 1, len(observed_factor_vars_list)):
                    observed_factor_j_vars = observed_factor_vars_list[j]
                    if j not in merged_factors_indices:
                        if len(observed_factor_i_vars.intersection(observed_factor_j_vars)) > 0:
                            merged_factor = merged_factor.multiply(self.factors[j])
                            merged_factors_indices.append(j)
                merged_factors.append(merged_factor)
        self.factors = merged_factors

    def reduce(self, vrs, values):
        """
        Observe a subset of the variables in the scope of this Gaussian and return the resulting factor.

        :param vrs: the names of the observed variable (list)
        :type vrs: str list
        :param values: the values of the observed variables
        :type values: vector-like
        :return: the resulting Gaussian
        :rtype: FactorizedFactor
        """
        all_evidence_dict = dict(zip(vrs, values))
        reduced_factors = []
        additional_log_weight = 0.0
        for factor in self.factors:
            factor_var_names = factor.var_names
            if set(vrs) == set(factor_var_names):
                additional_log_weight += factor.log_potential(x_val=values, vrs=vrs)
            elif len(set(vrs).intersection(set(factor_var_names))) > 0:
                subset_vrs, subset_values = get_subset_evidence(
                    all_evidence_dict=all_evidence_dict, subset_vars=factor.var_names
                )
                reduced_factor = factor.reduce(subset_vrs, subset_values)
                reduced_factors.append(reduced_factor)
            else:
                reduced_factors.append(factor.copy())
        adjusted_weight_factor_0 = reduced_factors[0]
        adjusted_weight_factor_0._add_log_weight(additional_log_weight)
        reduced_factors[0] = adjusted_weight_factor_0
        return FactorizedFactor(reduced_factors)

    def _first_factor_with_vars_index(self, var_names):
        """
        Get the index of the first factor in self_factors with var_names in its scope.

        :param var_names: The variables names to check for.
        :return: The matching factor.
        :rtype: Factor subclass
        """
        # TODO: add check for equals variable names - will be faster for multiplication
        for i, factor in enumerate(self.factors):
            if set(var_names).issubset(set(factor.var_names)):
                return i
        return None

    def _all_intersecting_factors_indices(self, var_names):
        """
        Get the indices of factors in self_factors which has overlap with a set of variable names.

        :param var_names: The variable names
        :type var_names: str list
        :return: The indices
        :rtype: int list
        """
        indices = []
        # TODO: add check for equals variable names - will be faster for multiplication
        for i, factor in enumerate(self.factors):
            if len(set(var_names).intersection(set(factor.var_names))) > 0:
                indices.append(i)
        return indices

    def equals(self, factor, rtol=DEFAULT_FACTOR_RTOL, atol=DEFAULT_FACTOR_ATOL):
        """
        Check if this factor is the same as another factor.

        :param factor: The other factor to compare to.
        :type factor: FactorizedFactor
        :param float rtol: The relative tolerance to use for factor equality check.
        :param float atol: The absolute tolerance to use for factor equality check.
        :return: The result of the comparison.
        :rtype: bool
        """
        if not isinstance(factor, FactorizedFactor):
            # TODO: find a better solution here
            return self.equals(FactorizedFactor([factor]))
        if set(factor.var_names) != set(self.var_names):
            return False
        if len(self.factors) != len(factor.factors):
            return self.joint_distribution.equals(factor.joint_distribution)

        self_comps_with_cpoies_in_factor = []
        for i, self_factor_i in enumerate(self.factors):
            if i not in self_comps_with_cpoies_in_factor:
                for other_factor_j in factor.factors:
                    if self_factor_i.equals(other_factor_j):
                        self_comps_with_cpoies_in_factor.append(i)
        if len(self_comps_with_cpoies_in_factor) == len(self.factors):
            return True
        return False

    def show(self):
        """
        Print this factorised factor.
        """
        for i, factor in self.factors:
            print(f"\n factor {i}/{len(self.factors)}:")
            factor.show()
