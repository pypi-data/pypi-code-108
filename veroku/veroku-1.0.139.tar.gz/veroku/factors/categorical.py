"""
A module for instantiating sparse tables with log probabilities.
"""

# Standard imports
import copy
import operator
import warnings
import matplotlib.pyplot as plt

# Third-party imports
import numpy as np
from numpy import unravel_index
from scipy import special
import pandas as pd

# Local imports
from veroku.factors._factor import Factor
from veroku.factors._factor_template import FactorTemplate
from veroku.factors import _factor_utils
from veroku._constants import DEFAULT_FACTOR_RTOL, DEFAULT_FACTOR_ATOL

# special operator rules
LOG_SUBTRACT_CANCEL_RULES = {(-np.inf, operator.sub, -np.inf): -np.inf}
LOG_SUBTRACT_KL_RULES = {(-np.inf, operator.sub, -np.inf): 0.0}

# TODO: consider removing some unused functions

# TODO: Currently variable values should be the same as numpy indices and therefore start at 0 with increments of 1.
#       We probably want to relax this requirement.


# pylint: disable=W0107
class InconsistentAssignmentNamesError(Exception):
    """
    Inconsistent Assignment Names Error
    """
    pass
# pylint: enable=W0107


def _check_consistent_assignment_names(variables_assignment_names_dict_a, variables_assignment_names_dict_b):
    vars_set_a = set(variables_assignment_names_dict_a.keys())
    vars_set_b = set(variables_assignment_names_dict_b.keys())
    vars_union = set(vars_set_a).union(vars_set_b)
    for var_name in vars_union:
        if var_name in vars_set_a and var_name in vars_set_b:
            assignment_names_a = variables_assignment_names_dict_a[var_name]
            assignment_names_b = variables_assignment_names_dict_b[var_name]

            if assignment_names_a != assignment_names_b:
                raise InconsistentAssignmentNamesError(f"assignment names for variable {var_name} are not equal ({assignment_names_a} != {assignment_names_b})")


class Categorical(Factor):
    """
    A class for instantiating sparse tables with log probabilities.
    """

    def __init__(self, var_names, cardinalities=None, probs_table=None, log_probs_tensor=None, variables_assignment_names=None):
        """
        Construct a SparseLogTable. Either log_probs_table or probs_table should be supplied.

        :param var_names: The variable names.
        :type var_names: str list
        :param cardinalities: The cardinalities of the variables (i.e, for three binrary variables: [2,2,2]). This is
            only required if the probs_table param is supplied instead of the log_probs_tensor.
        :type cardinalities: int list
        :param probs_table: A dictionary with assignments (tuples) as keys and probabilities as values.
            Missing assignments are assumed to have zero probability. This parameter is not required if log_probs_tensor
            is given.
        :type probs_table: dict
        :param log_probs_tensor: A dense tensor representation of the log distribution (not required if probs_table is given)
        :type log_probs_tensor: numpy.ndarray

        :Example:

        .. code-block:: python

            >>> # Using the probs_table parameter:
            >>> var_names = ['a','b']
            >>> probs_table = {(0,0):0.8,
            ...                (0,1):0.2,
            ...                (1,0):0.4,
            ...                (1,1):0.6}
            >>> var_cardinalities = [2,2]
            >>> table = Categorical(probs_table=probs_table,
            ...                    var_names=var_names,
            ...                    cardinalities=var_cardinalities)
            >>> # or, equivalently, using the log_probs_tensor parameter:
            >>> var_names = ['a','b']
            >>> log_probs_tensor = np.array([[np.log(0.8), np.log(0.2)],
            ...                             [np.log(0.4), np.log(0.6)]])
            >>> var_cardinalities = [2,2]
            >>> table = Categorical(log_probs_tensor=log_probs_tensor,
            ...                    var_names=var_names,

        """
        # TODO: add check that assignment lengths are consistent with var_names
        # TODO: add check that cardinalities are consistent with assignments
        super().__init__(var_names=var_names)

        if cardinalities is None:
            if log_probs_tensor is None:
                msg = (
                    "numpy array type log_probs_tensor is expected cardinalities are not supplied.\n"
                    + "Alternatively, provide cardinalities with dict type probs_table."
                )
                raise ValueError(msg)
            cardinalities = log_probs_tensor.shape
        elif len(cardinalities) != len(var_names):
            raise ValueError("The cardinalities and var_names lists should be the same length.")
        if (log_probs_tensor is None) and (probs_table is None):
            raise ValueError("Either log_probs_tensor or probs_table must be specified")
        if log_probs_tensor is None:
            probs_tensor = np.zeros(shape=cardinalities)
            for assignment, prob in probs_table.items():
                try:
                    probs_tensor[assignment] = prob
                except IndexError as index_error:
                    error_message = f"assignment {assignment} is not consistent with the cardinalities ({cardinalities}) provided"
                    raise IndexError(error_message) from index_error
            with warnings.catch_warnings():
                # prevents 'divide by zero encountered in log' from displaying
                warnings.simplefilter("ignore")
                self.log_probs_tensor = np.log(probs_tensor)
        else:
            if len(log_probs_tensor.shape) != len(var_names):
                raise ValueError("log_probs_tensor should have dimension equal to the number of variables.")
            self.log_probs_tensor = log_probs_tensor.copy()
        # TODO: remove this
        self.var_cards = dict(zip(var_names, cardinalities))
        self.cardinalities = cardinalities
        if variables_assignment_names is not None:
            assrt_error_msg = f"variables_assignment_names should have same length as var_names" \
                              f" (received {variables_assignment_names} and {var_names})"
            assert len(variables_assignment_names) == len(var_names), assrt_error_msg
            var_assignment_names_dict = dict()
            for var_name, assignments_names, cardinality in zip(var_names, variables_assignment_names, cardinalities):
                assert_error_msg = \
                    f"Incorrect number of unique assignment names provided for variable {var_name} (should equal variable card ({cardinality})) "
                assert cardinality == len(set(assignments_names)), assert_error_msg
                var_assignment_names_dict[var_name] = tuple(copy.deepcopy(assignments_names))
        else:
            var_assignment_names_dict = {var_name: tuple(range(var_card)) for var_name, var_card in zip(var_names, cardinalities)}
        self.vars_assignments_names_dict = var_assignment_names_dict

    def reorder(self, new_var_names_order):
        """
        Reorder categorical table variables to a new order and reorder the associated probabilities
        accordingly.

        :param new_var_names_order: The new variable order.
        :type new_var_names_order: str list
        :return: The factor with new order.

        Example:

        .. code-block:: python

            >>> var_names = ['a','b']
            >>> probs_table = {(0,0):0.1,
            ...                (0,1):0.2,
            ...                (1,0):0.3,
            ...                (1,1):0.4}
            >>> var_cardinalities = [2,2]
            >>> table = Categorical(probs_table=probs_table,
            >>>                    var_names=var_names,
            >>>                    cardinalities=var_cardinalities)
            >>> table.reorder(new_var_names_order=['b', 'a'])
            b	a	prob
            0	0	0.1000
            0	1	0.3000
            1	0	0.2000
            1	1	0.4000
        """
        if new_var_names_order == self.var_names:
            return self.copy()
        if set(new_var_names_order) != set(self.var_names):
            raise ValueError("The new_var_names_order set must be the same as the factor variables.")
        vars_new_order_indices = [self.var_names.index(v) for v in new_var_names_order]
        log_probs_tensor = self.log_probs_tensor.transpose(vars_new_order_indices)
        variables_assignment_names = [self.vars_assignments_names_dict[var_name] for var_name in new_var_names_order]
        return Categorical(var_names=new_var_names_order, log_probs_tensor=log_probs_tensor, variables_assignment_names=variables_assignment_names)

    def equals(self, factor, rtol=DEFAULT_FACTOR_RTOL, atol=DEFAULT_FACTOR_ATOL):
        """
        Check if this factor is the same as another factor.

        :param factor: The other factor to compare to.
        :type factor: Categorical
        :param float rtol: The relative tolerance to use for factor equality check.
        :param float atol: The absolute tolerance to use for factor equality check.
        :return: The result of the comparison.
        :rtype: bool
        """
        if not isinstance(factor, Categorical):
            raise TypeError(f"factor must be of Categorical type but has type {type(factor)}")
        if set(self.var_names) != set(factor.var_names):
            return False
        factor_copy = factor.reorder(self.var_names)
        if not np.allclose(self.log_probs_tensor, factor_copy.log_probs_tensor, rtol=rtol, atol=atol):
            return False
        return True

    def copy(self):
        """
        Make a copy of this factor.

        :return: The copy of this factor.
        :rtype: Categorical
        """
        variables_assignment_names = [self.vars_assignments_names_dict[var_name] for var_name in
                                      self.var_names]
        self_copy = Categorical(var_names=self.var_names.copy(),
                                log_probs_tensor=self.log_probs_tensor.copy(),
                                variables_assignment_names=variables_assignment_names)
        return self_copy

    @staticmethod
    def tensor_operation(tensor_a, tensor_b, tensor_a_var_names, tensor_b_var_names, func):
        """
        Apply a element wise function to two tensors with named indices.

        :param numpy.ndarray tensor_a: The first tensor.
        :param numpy.ndarray tensor_b: The second tensor.
        :param tensor_a_var_names: The first tensor's variable names corresponding to the indices.
        :type tensor_a_var_names: string list
        :param tensor_b_var_names: The second tensor's variable names corresponding to the indices.
        :type tensor_b_var_names: string list
        :param func: The function to apply elementwise to the two tensors (func(a,b))
        :return: The resulting tensor and corresponding variable names
        :rtype: string list
        """
        if tensor_a_var_names == tensor_b_var_names:
            result_tensor = func(tensor_a, tensor_b)
            return result_tensor, tensor_a_var_names
        common_vars = set(tensor_a_var_names).intersection(tensor_b_var_names)

        remaining_f1_vars = [var for var in tensor_a_var_names if var not in common_vars]
        remaining_f2_vars = [var for var in tensor_b_var_names if var not in common_vars]
        # sort according to f1_vars so that only f2_tensor can be transposed if sets are the same
        common_vars = [v for v in tensor_a_var_names if v in common_vars]
        f1_vars_new_order = [tensor_a_var_names.index(v) for v in remaining_f1_vars]
        f1_vars_new_order += [tensor_a_var_names.index(v) for v in common_vars]

        f1_tensor_new_shape = tensor_a.transpose(f1_vars_new_order)
        f1_dim_expansion_axis = list(range(len(remaining_f2_vars)))
        f1_tensor_std_shape = np.expand_dims(f1_tensor_new_shape, axis=f1_dim_expansion_axis)
        #  now f1 has var order / dim order: [[1]*num_f2_vars, rest_f1_vars_dims, common_vars]

        f2_vars_new_order = [tensor_b_var_names.index(var) for var in remaining_f2_vars]
        f2_vars_new_order += [tensor_b_var_names.index(var) for var in common_vars]
        f2_tensor_new_shape = tensor_b.transpose(f2_vars_new_order)
        # now f2 has var order / dim order:  [common_vars_dim, [1]*num_f2_vars]

        f2_dim_expansion_axis = list(
            range(len(remaining_f2_vars), len(remaining_f2_vars) + len(remaining_f1_vars))
        )
        f2_tensor_std_shape = np.expand_dims(f2_tensor_new_shape, axis=f2_dim_expansion_axis)
        # now f1 has var order / dim order: [f1_vars_dims, [1]*num_f1_vars] =
        # [common_vars, rest_f1_vars_dims, [1]*num_f2_vars]
        result_vars = remaining_f2_vars + remaining_f1_vars + common_vars
        result_tensor = func(f1_tensor_std_shape, f2_tensor_std_shape)
        return result_tensor, result_vars

    def marginalize(self, vrs, keep=True):
        """
        Sum out variables from this factor.

        :param vrs: (list) a subset of variables in the factor's scope
        :param keep: Whether to keep or sum out vrs
        :return: The resulting factor.
        :rtype: Categorical
        """

        vars_to_keep = super().get_marginal_vars(vrs, keep)
        vars_to_sum_out = [v for v in self.var_names if v not in vars_to_keep]
        indices_to_sum_out = [self.var_names.index(v) for v in vars_to_sum_out]
        result_tensor = np.apply_over_axes(special.logsumexp, self.log_probs_tensor, axes=indices_to_sum_out)
        vars_to_keep_assignment_values = [self.vars_assignments_names_dict[var] for var in vars_to_keep]
        return Categorical(var_names=vars_to_keep, log_probs_tensor=np.squeeze(result_tensor),
                           variables_assignment_names=vars_to_keep_assignment_values)

    def reduce(self, vrs, values):
        """
        Observe variables to have certain values and return reduced table.

        :param vrs: (list) The variables.
        :param values: (tuple or list) Their values
        :return: The resulting factor.
        :rtype: Categorical
        """

        vars_unobserved = [v for v in self.var_names if v not in vrs]
        obs_dict = dict(zip(vrs, values))

        reduced_tensor_indexing = tuple(
            [obs_dict[v] if v in obs_dict else slice(None) for v in self.var_names]
        )
        result_table = self.log_probs_tensor[reduced_tensor_indexing]
        vars_to_keep_assignment_values = [self.vars_assignments_names_dict[var] for var in
                                          vars_unobserved]
        return Categorical(var_names=vars_unobserved, log_probs_tensor=result_table,
                           variables_assignment_names=vars_to_keep_assignment_values)

    def _assert_consistent_cardinalities(self, factor):
        """
        Assert that the variable cardinalities are consistent between two factors.

        :param Categorical factor: The factor to compare with.
        """
        for var in self.var_names:
            if var in factor.var_cards:
                error_msg = (
                    f"Error: inconsistent variable cardinalities: {factor.var_cards}, {self.var_cards}"
                )
                assert self.var_cards[var] == factor.var_cards[var], error_msg

    def multiply(self, factor):
        """
        Multiply this factor with another factor and return the result.

        :param factor: The factor to multiply with.
        :type factor: Categorical
        :return: The factor product.
        :rtype: Categorical
        """
        if not isinstance(factor, Categorical):
            raise TypeError(f"factor must be of Categorical type but has type {type(factor)}")
        self._assert_consistent_cardinalities(factor)

        result_tensor, result_vars = self.tensor_operation(
            self.log_probs_tensor, factor.log_probs_tensor, self.var_names, factor.var_names, operator.add
        )
        _check_consistent_assignment_names(self.vars_assignments_names_dict,
                                           factor.vars_assignments_names_dict)
        vars_assignments_names_union_dict = copy.deepcopy(self.vars_assignments_names_dict)
        vars_assignments_names_union_dict.update(factor.vars_assignments_names_dict)

        vars_to_keep_assignment_values = [vars_assignments_names_union_dict[var] for var in result_vars]

        return Categorical(var_names=result_vars, log_probs_tensor=result_tensor,
                           variables_assignment_names=vars_to_keep_assignment_values)

    def cancel(self, factor):
        """
        Almost like divide, but with a special rule that ensures that division of zeros by zeros results in zeros. When
        categorical message factors with zero probabilities are used in Belief Update algorithms, multiplication by the
        zero probabilities cause zeros in the cluster potentials, when these messages need to be divided out again, this
        results in 0/0 operations. Since, in such cases, we know (from the information in the message) that the
        probability value should be zero, it makes sense to set the result of 0/0 operations to 0 in these cases.

        :param factor: The factor to divide by.
        :type factor: Categorical
        :return: The factor quotient.
        :rtype: Categorical
        """
        augmented_factor_tensor = factor.log_probs_tensor.copy()
        special_case_indices = np.where(
            (augmented_factor_tensor == -np.inf) & (self.log_probs_tensor == -np.inf)
        )

        indices_are_empty = [a.size == 0 for a in special_case_indices]

        if not all(indices_are_empty):
            augmented_factor_tensor[special_case_indices] = np.float(0.0)
        result_tensor, result_vars = self.tensor_operation(
            self.log_probs_tensor, augmented_factor_tensor, self.var_names, factor.var_names, operator.sub
        )
        _check_consistent_assignment_names(self.vars_assignments_names_dict,
                                           factor.vars_assignments_names_dict)
        vars_assignment_names = [self.vars_assignments_names_dict[var] for var in
                                  result_vars]
        return Categorical(var_names=result_vars, log_probs_tensor=result_tensor,
                           variables_assignment_names=vars_assignment_names)

    def divide(self, factor):
        """
        Divide this factor by another factor and return the result.

        :param factor: The factor to divide by.
        :type factor: Categorical
        :return: The factor quotient.
        :rtype: Categorical
        """
        if not isinstance(factor, Categorical):
            raise TypeError(f"factor must be of Categorical type but has type {type(factor)}")
        self._assert_consistent_cardinalities(factor)
        result_tensor, result_vars = self.tensor_operation(
            self.log_probs_tensor, factor.log_probs_tensor, self.var_names, factor.var_names, operator.sub
        )
        _check_consistent_assignment_names(self.vars_assignments_names_dict,
                                           factor.vars_assignments_names_dict)
        vars_assignment_names = [self.vars_assignments_names_dict[var] for var in
                                  result_vars]
        return Categorical(var_names=result_vars, log_probs_tensor=result_tensor,
                           variables_assignment_names=vars_assignment_names)

    def argmax(self):
        """
        Get the first assignment (vector value) that maximises the factor potential.

        :return: The argmax assignment.
        :rtype: int list
        """
        # TODO: add functionality to deal with more that one instance of the maximum value.
        argmax_assignment = unravel_index(self.log_probs_tensor.argmax(), self.log_probs_tensor.shape)
        return argmax_assignment

    def argmax_assignment_names(self):
        """
        Get the first assignment values that maximises the factor potential.

        :return: The argmax assignment.
        :rtype: int list
        """
        # TODO: add functionality to deal with more that one instance of the maximum value.
        argmax_assignment = unravel_index(self.log_probs_tensor.argmax(), self.log_probs_tensor.shape)
        argmax_assignment_names = [self.vars_assignments_names_dict[var_name][var_assignment_value] for var_name, var_assignment_value in
                                   zip(self.var_names, argmax_assignment)]
        return argmax_assignment_names

    def normalize(self):
        """
        Normalize the factor.

        :return: The normalized factor.
        :rtype: Categorical
        """
        factor_copy = self.copy()
        logz = special.logsumexp(self.log_probs_tensor)
        factor_copy.log_probs_tensor -= logz
        return factor_copy

    @staticmethod
    def _raw_kld(log_p, log_q):
        """
        Get the raw numerically calculated kld (which could result in numerical errors causing negative KLDs).

        :param log_p: The log_p tensor
        :param log_q:
        :return: The KL-divergence
        :rtype: float
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kl_array = np.where(log_p != -np.inf, np.exp(log_p) * (log_p - log_q), 0.0)
        kld = np.sum(kl_array)
        return kld

    def kl_divergence(self, factor, normalize_factor=True):
        """
        Get the KL-divergence D_KL(P || Q) = D_KL(self || factor) between a normalized version of this factor and
        another factor.

        :param factor: The other factor
        :type factor: Categorical
        :param normalize_factor: Whether or not to normalize the other factor before computing the KL-divergence.
        :type normalize_factor: bool
        :return: The Kullback-Leibler divergence
        :rtype: float
        """
        _check_consistent_assignment_names(self.vars_assignments_names_dict,
                                           factor.vars_assignments_names_dict)
        normalized_self = self.normalize()
        normalized_self = normalized_self.reorder(factor.var_names)
        log_p = normalized_self.log_probs_tensor
        factor_ = factor
        if normalize_factor:
            factor_ = factor.normalize()
        log_q = factor_.log_probs_tensor
        kld = self._raw_kld(log_p, log_q)
        if kld < 0.0:
            if np.isclose(kld, 0.0, atol=1e-4):
                #  this is fine (numerical error)
                return 0.0
            kld_msg_details = "Categorical:\n" + normalized_self.__repr__() + "\nfactor:" + factor_.__repr__()
            raise ValueError(f"Negative KLD: {kld}. Details:\n{kld_msg_details}")
        return kld

    def distance_from_vacuous(self):
        """
        Get the Kullback-Leibler (KL) divergence between this factor and a uniform copy of it.

        :return: The KL divergence.
        :rtype: float
        """
        # make uniform copy
        uniform_log_prob = -np.log(np.product(self.log_probs_tensor.shape))
        uniform_log_tensor = np.ones(self.log_probs_tensor.shape) * uniform_log_prob
        vars_assignment_names = [self.vars_assignments_names_dict[var] for var in
                                 self.var_names]
        uniform_factor = Categorical(var_names=self.var_names, log_probs_tensor=uniform_log_tensor,
                                     variables_assignment_names=vars_assignment_names)
        kld = self.kl_divergence(uniform_factor, normalize_factor=False)
        return kld

    def potential(self, vrs, assignment):
        """
        Get the value of the factor for a specific assignment.

        :param assignment: The assignment
        :return: The value
        """
        assert set(vrs) == set(self.var_names), "variables (vrs) do not match factor variables."
        obs_dict = dict(zip(vrs, assignment))
        obs_tensor_indexing = tuple([obs_dict[v] if v in obs_dict else slice(None) for v in self.var_names])
        return np.exp(self.log_probs_tensor[obs_tensor_indexing])

    def show(self):
        """
        Print the factor's string representation.
        """
        print(self.__repr__())

    @property
    def dense_distribution_array(self):
        """
        An array containing all the discrete assignments and the corresponding probabilities.
        """
        distribution_list = []

        for assignment in np.ndindex(self.log_probs_tensor.shape):
            log_prob = self.log_probs_tensor[assignment]
            prob = np.exp(log_prob)
            distribution_list.append(list(assignment) + [prob])
        distribution_array = np.array(distribution_list)
        return distribution_array

    def __repr__(self):
        """
        Get the string representation for the factor.

        :return: The representation string
        :rtype: str
        """
        tabbed_spaced_var_names = "\t".join(self.var_names) + "\tprob\n"
        repr_str = tabbed_spaced_var_names
        spacings = ['\t' * _factor_utils.tabs_to_cover_string(var) for var in self.var_names] + ['\n']
        for assignment in np.ndindex(self.log_probs_tensor.shape):
            prob = self.log_probs_tensor[assignment]
            prob = np.exp(prob)
            line = _factor_utils.space_assignments_and_probs(assignment, prob, spacings)
            repr_str += line

        #repr_str += "\n".join([f"{var_name}: {assignment_names}" for var_name,assignment_names in self.vars_assignments_names_dict.items()])
        #repr_str += "\n"
        return repr_str

    def get_df(self, named_assignments=False):
        """
        Get a dataframe representation of the factor.

        :param named_assignments: Whether to use assignment names (instead of indices).
        :type named_assignments: bool
        :return: The dataframe
        :rtype: pandas.DataFrame
        """
        data_list = []
        for row in self.dense_distribution_array:
            assignments_array = row[:-1]
            prob = row[-1]
            if not named_assignments:
                data_list.append(list(assignments_array) + [prob])
            else:
                named_assignments = [self.vars_assignments_names_dict[var_name][int(val)] for
                                     var_name, val in zip(self.var_names, assignments_array)]
                data_list.append(named_assignments + [prob])

        column_names = self.var_names + ["prob"]
        factor_df = pd.DataFrame(data=data_list, columns=column_names)
        return factor_df

    def plot(self, figsize=None):
        """
        Plot the distribution as a bar plot.

        :param figsize: The figure size.
        :type figsize: tuple
        """
        def assignment_names_to_x_label(row):
            processed_assignment_value_names = []
            for elem in row:
                if isinstance(elem, float):
                    processed_assignment_value_name = f"{elem:.2f}"
                else:
                    processed_assignment_value_name = elem
                processed_assignment_value_names.append(processed_assignment_value_name)
            x_label = ", ".join(processed_assignment_value_names)
            return x_label

        num_assignments = self.dense_distribution_array.shape[0]
        color_list = ["b"]*num_assignments
        factor_df = self.get_df(named_assignments=True)
        factor_df["assignment"] = factor_df[self.var_names].apply(assignment_names_to_x_label, axis=1)

        if figsize is not None:
            factor_df.plot.barh(x="assignment", y="prob", color=color_list, figsize=figsize)
        else:
            factor_df.plot.barh(x="assignment", y="prob", color=color_list)
        plt.gca().invert_yaxis()


class CategoricalTemplate(FactorTemplate):

    """
    A class for specifying categorical factor templates and creating categorical factors from these templates.
    """

    def __init__(self, var_templates=None, cardinalities=None, probs_table=None, log_probs_tensor=None):
        """
        Create a Categorical factor template.

        :param cardinalities: The cardinalities of the variables (i.e, for three binrary variables: [2,2,2]). This is
            only required if the probs_table param is supplied instead of the log_probs_tensor.
        :type cardinalities: int list
        :param probs_table: A dictionary with assignments (tuples) as keys and probabilities as values.
            Missing assignments are assumed to have zero probability. This parameter is not required if log_probs_tensor
            is given.
        :type probs_table: dict
        :param log_probs_tensor: A dense tensor representation of the log distribution (not required if probs_table is given)
        :type log_probs_tensor: numpy.ndarray

        :Example:

        .. code-block:: python

            >>> var_templates = ['a_{i}','b_{i}']
            >>> probs_table = {(0,0):0.8,
            ...                (0,1):0.2,
            ...                (1,0):0.4,
            ...                (1,1):0.6}
            >>> cardinalities = [2,2]
            >>> categorical_template = CategoricalTemplate(probs_table=probs_table,
            ...                                            var_names=var_names,
            ...                                            cardinalities=cardinalities)
            >>> categorical_template.make_factor(format_dict={'i':0})

        """
        super().__init__(var_templates=var_templates)
        self.log_probs_tensor = copy.deepcopy(log_probs_tensor)
        self.cardinalities = cardinalities
        self.probs_table = probs_table

    def make_factor(self, format_dict=None, var_names=None):
        """
        Make a factor with var_templates formatted by format_dict to create specific var names.

        :param format_dict: The dictionary to be used to format the var_templates strings.
        :type format_dict: str dict
        :return: The instantiated factor.
        :rtype: Categorical
        """
        if format_dict is not None:
            assert var_names is None
            var_names = [vt.format(**format_dict) for vt in self._var_templates]
        return Categorical(
            var_names=var_names,
            probs_table=self.probs_table,
            cardinalities=self.cardinalities,
            log_probs_tensor=self.log_probs_tensor,
        )
