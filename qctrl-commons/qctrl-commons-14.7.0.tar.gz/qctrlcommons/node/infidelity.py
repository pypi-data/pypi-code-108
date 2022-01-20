# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#      https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""Module for InfidelityNode."""
from typing import (
    List,
    Optional,
    Union,
)

import forge
import numpy as np
from scipy.sparse import spmatrix

from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    Pwc,
    Stf,
    Target,
    Tensor,
)
from qctrlcommons.node.utils import (
    is_broadcastable,
    validate_batch_and_value_shapes,
    validate_broadcasted_shape,
    validate_shape,
)
from qctrlcommons.preconditions import (
    check_argument,
    check_operator,
    check_sample_times,
    check_square_pwc_or_stf,
)


class InfidelityPwc(Node):
    r"""
    Creates the total infidelity of the given piecewise-constant system.

    Use this function to compute the sum of the operational infidelity (which
    measures how effectively the system achieves a target gate) and filter
    function values (which measure how robust the system evolution is to
    various perturbative noise processes). This total infidelity value
    provides a cost that measures how effectively and robustly a set of
    controls achieves a target operation.

    Note that the total infidelity returned by this function is at least zero,
    but might be larger than one (for example if the system is highly
    sensitive to one of the noise processes).

    Parameters
    ----------
    hamiltonian : Pwc
        The control Hamiltonian :math:`H_{\mathrm c}(t)`. You can provide
        either a single Hamiltonian or a batch of them.
    target : Target
        The object describing the target gate :math:`U_\mathrm{target}` and
        (optionally) the filter function projector :math:`P`. If you
        provide a batch of Hamiltonians, the function uses the same target
        for all the elements in the batch.
    noise_operators : list[np.ndarray or Tensor or Pwc], optional
        The perturbative noise operators :math:`\{N_j(t)\}`. The operators
        in the list can either be single operators or batches of them. If
        any of the noise operators or the Hamiltonian are batches, the batch
        shapes must all be broadcastable. You can omit this list if there are
        no noises.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The total infidelity (operational infidelity plus filter function
        values) of the given system, with respect to the given target gate.
        If you provide a batch of Hamiltonians or noise operators, the
        function returns a batch of infidelities containing one infidelity
        for each Hamiltonian and list of noise operators in the input batches.

    Warnings
    --------
    The Hessian matrix cannot currently be calculated for a graph which includes
    an `infidelity_pwc` node if the `hamiltonian` has degenerate eigenvalues at
    any segment.

    See Also
    --------
    infidelity_stf : Corresponding operation for `Stf` Hamiltonians.
    target : Define the target operation of the time evolution.
    time_evolution_operators_pwc : Unitary time evolution operators for quantum systems with
        `Pwc` Hamiltonians.

    Notes
    -----
    The total system Hamiltonian is

    .. math:: H_{\mathrm c}(t) + \sum_j \beta_j(t) N_j(t),

    where :math:`\{\beta_j(t)\}` are small, dimensionless, stochastic
    variables.

    The total infidelity, as represented by this node, is the sum of the
    operational infidelity :math:`\mathcal{I}` and the filter functions
    :math:`\{F_j(0)\}` of each noise operator evaluated at zero frequency.

    The operational infidelity is

    .. math::
      \mathcal{I} = 1-\left|
        \frac{\mathrm{Tr} \left(U_\mathrm{target}^\dagger U(t)\right)}
        {\mathrm{Tr} \left(U_\mathrm{target}^\dagger U_\mathrm{target}\right)}
        \right|^2,

    where :math:`U(t)` is the unitary time evolution operator due to
    :math:`H_{\mathrm c}(t)`.

    The filter function for the noise operator :math:`N_j(t)` is a measure of
    robustness, defined at frequency :math:`f` as

    .. math::
      F_j(f) = \frac{1}{\mathrm{Tr}(P)} \mathrm{Tr} \left( P
        \mathcal{F} \left\{ \tilde N_j^\prime(t) \right\} \left[ \mathcal{F}
        \left\{ \tilde N^\prime (t) \right\} \right]^\dagger P \right),

    where :math:`\mathcal{F}` is the Fourier transform,
    :math:`\tilde N_j(t) \equiv U_c^\dagger(t) N_j(t) U_c(t)` is the
    toggling-frame noise operator, and
    :math:`\tilde N_j^\prime(t)\equiv
    \tilde N_j(t)-
    \frac{\mathrm{Tr}(P\tilde N_j(t)P)}{\mathrm{Tr}(P)} \mathbb{I}`
    differs from :math:`\tilde N_j(t)` only by a multiple of the identity but
    is trace-free on the subspace of interest. The filter function value at
    zero frequency quantifies the sensitivity of the controls to quasi-static
    noise applied via the corresponding noise operator.

    Examples
    --------
    Calculate infidelity of the identity gate for a noiseless single qubit.

    >>> sigma_z = np.array([[1, 0], [0, -1]])
    >>> hamiltonian = graph.pwc(
    ...     durations=np.array([0.1, 0.1]), values=np.array([sigma_z, -sigma_z])
    ... )
    >>> target = graph.target(np.eye(2))
    >>> infidelity = graph.infidelity_pwc(
    ...     hamiltonian=hamiltonian, target=target, name="infidelity"
    ... )
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["infidelity"])
    >>> result.output["infidelity"]["value"]
    0.0

    See more examples in the `How to optimize controls with non-linear dependencies
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-
    with-nonlinear-dependences>`_ user guide.
    """

    name = "infidelity_pwc"
    args = [
        forge.arg("hamiltonian", type=Pwc),
        forge.arg("target", type=Target),
        forge.arg(
            "noise_operators",
            type=Optional[List[Union[np.ndarray, Tensor, Pwc]]],
            default=None,
        ),
    ]
    rtype = Tensor
    categories = [Category.OPTIMAL_AND_ROBUST_CONTROL]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        hamiltonian = kwargs.get("hamiltonian")
        target = kwargs.get("target")
        noise_operators = kwargs.get("noise_operators")
        check_argument(
            isinstance(hamiltonian, Pwc),
            "The Hamiltonian must be a Pwc.",
            {"hamiltonian": hamiltonian},
        )
        check_argument(
            isinstance(target, Target),
            "The target must be a Target.",
            {"target": target},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            hamiltonian, "hamiltonian"
        )
        check_square_pwc_or_stf(hamiltonian, "hamiltonian")
        check_argument(
            value_shape == target.value_shape,
            "The Hamiltonian and the target must have the same value shape.",
            {"hamiltonian": hamiltonian, "target": target},
        )
        for noise_operator in noise_operators or []:
            if isinstance(noise_operator, Pwc):
                (
                    noise_operator_batch_shape,
                    noise_operator_value_shape,
                ) = validate_batch_and_value_shapes(noise_operator, "noise_operators")
            else:
                check_argument(
                    not isinstance(noise_operator, (spmatrix, Stf)),
                    "Noise operator must not be sparse or an Stf.",
                    {"noise_operators": noise_operators},
                )
                check_operator(noise_operator, "noise_operators")
                noise_operator_shape = validate_shape(noise_operator, "noise_operators")
                noise_operator_batch_shape = noise_operator_shape[:-2]
                noise_operator_value_shape = noise_operator_shape[-2:]
            check_argument(
                noise_operator_value_shape == value_shape,
                "The Hamiltonian and the noise operators must have the same value shape.",
                {"hamiltonian": hamiltonian, "noise_operators": noise_operators},
            )
            check_argument(
                is_broadcastable(batch_shape, noise_operator_batch_shape),
                "The batch shapes of the Hamiltonian and noise_operators must be broadcastable.",
                {"hamiltonian": hamiltonian, "noise_operators": noise_operators},
            )

            # Update the overall batch shape to take into account this noise operator (note that
            # the check can't fail, since we already ensured the shapes were broadcastable, so we
            # can pass dummy names).
            batch_shape = validate_broadcasted_shape(
                batch_shape, noise_operator_batch_shape, "", ""
            )

        return Tensor(_operation, shape=batch_shape)


class InfidelityStf(Node):
    r"""
    Creates the total infidelity of a given system with a sampleable Hamiltonian.

    See :obj:`infidelity_pwc` for information about the total infidelity
    created by this function.

    Parameters
    ----------
    sample_times : np.ndarray(1D, real)
        The times at which the Hamiltonian and noise operators (if present) should be sampled for
        the integration. Must start with 0, be ordered, and contain at least one element.
    hamiltonian : Stf
        The control Hamiltonian :math:`H_{\mathrm c}(t)`. You can provide
        either a single Hamiltonian or a batch of them.
    target : Target
        The object describing the target gate :math:`U_\mathrm{target}` and
        (optionally) the filter function projector :math:`P`. If you
        provide a batch of Hamiltonians, the function uses the same target
        for all the elements in the batch.
    noise_operators : list[np.ndarray or Tensor or Stf], optional
        The perturbative noise operators :math:`\{N_j(t)\}`. The operators
        in the list can either be single operators or batches of them. If
        any of the noise operators or the Hamiltonian are batches, the batch
        shapes must all be broadcastable. You can omit this list if there are
        no noises.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The total infidelity (operational infidelity plus filter function
        values) of the given system, with respect to the given target gate,
        at the last time in `sample_times`.
        If you provide a batch of Hamiltonians or noise operators, the
        function returns a batch of infidelities containing one infidelity
        for each Hamiltonian and list of noise operators in the input batches.

    See Also
    --------
    infidelity_pwc : Corresponding operation for `Pwc` Hamiltonians.
    target : Define the target operation of the time evolution.
    time_evolution_operators_stf : Unitary time evolution operators for quantum systems with
        `Stf` Hamiltonians.

    Examples
    --------
    Calculate the infidelity of the Pauli :math:`X` gate for a noiseless qubit.

    >>> sigma_x = np.array([[0, 1], [1, 0]])
    >>> hamiltonian = graph.constant_stf_operator(np.pi * sigma_x / 2)
    >>> target = graph.target(sigma_x)
    >>> infidelity = graph.infidelity_stf(
    ...     sample_times=np.linspace(0, 0.5, 100),
    ...     hamiltonian=hamiltonian,
    ...     target=target,
    ...     name="infidelity",
    ... )
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["infidelity"])
    >>> result.output["infidelity"]["value"]
    0.5000000000260991

    See more examples in the `How to perform model-based optimization with user-defined
    basis functions <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-perform-model-
    based-optimization-with-user-defined-basis-functions>`_ user guide.
    """

    name = "infidelity_stf"
    args = [
        forge.arg("sample_times", type=np.ndarray),
        forge.arg("hamiltonian", type=Stf),
        forge.arg("target", type=Target),
        forge.arg(
            "noise_operators",
            type=Optional[List[Union[np.ndarray, Tensor, Stf]]],
            default=None,
        ),
    ]
    rtype = Tensor
    categories = [Category.OPTIMAL_AND_ROBUST_CONTROL]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        sample_times = kwargs.get("sample_times")
        hamiltonian = kwargs.get("hamiltonian")
        target = kwargs.get("target")
        noise_operators = kwargs.get("noise_operators")
        check_sample_times(sample_times, "sample_times")
        check_argument(
            sample_times[0] == 0,
            "The first of the sample times must be zero.",
            {"sample_times": sample_times},
        )
        check_argument(
            isinstance(hamiltonian, Stf),
            "The Hamiltonian must be an Stf.",
            {"hamiltonian": hamiltonian},
        )
        check_argument(
            isinstance(target, Target),
            "The target must be a Target.",
            {"target": target},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            hamiltonian, "hamiltonian"
        )
        check_square_pwc_or_stf(hamiltonian, "hamiltonian")
        check_argument(
            value_shape == target.value_shape,
            "The Hamiltonian and the target must have the same value shape.",
            {"hamiltonian": hamiltonian, "target": target},
        )
        for noise_operator in noise_operators or []:
            if isinstance(noise_operator, Stf):
                (
                    noise_operator_batch_shape,
                    noise_operator_value_shape,
                ) = validate_batch_and_value_shapes(noise_operator, "noise_operators")
            else:
                check_argument(
                    not isinstance(noise_operator, (spmatrix, Pwc)),
                    "Noise operator must not be sparse or a Pwc.",
                    {"noise_operators": noise_operators},
                )
                check_operator(noise_operator, "noise_operators")
                noise_operator_shape = validate_shape(noise_operator, "noise_operators")
                noise_operator_batch_shape = noise_operator_shape[:-2]
                noise_operator_value_shape = noise_operator_shape[-2:]
            check_argument(
                noise_operator_value_shape == value_shape,
                "The Hamiltonian and the noise operators must have the same value shape.",
                {"hamiltonian": hamiltonian, "noise_operators": noise_operators},
            )
            check_argument(
                is_broadcastable(batch_shape, noise_operator_batch_shape),
                "The batch shapes of the Hamiltonian and noise_operators must be broadcastable.",
                {"hamiltonian": hamiltonian, "noise_operators": noise_operators},
            )

            # Update the overall batch shape to take into account this noise operator (note that
            # the check can't fail, since we already ensured the shapes were broadcastable, so we
            # can pass dummy names).
            batch_shape = validate_broadcasted_shape(
                batch_shape, noise_operator_batch_shape, "", ""
            )

        return Tensor(_operation, shape=batch_shape)
