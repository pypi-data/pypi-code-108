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
"""Module for sparse."""
from typing import (
    List,
    Optional,
    Union,
)

import forge
import numpy as np
from scipy.sparse import coo_matrix

from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    Pwc,
    SparsePwc,
    Tensor,
)
from qctrlcommons.node.utils import (
    validate_hamiltonian,
    validate_shape,
)
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_hermitian,
    check_argument_integer,
    check_argument_numeric,
    check_duration,
    check_operator,
    check_sample_times,
)


class SparsePwcOperator(Node):
    r"""
    Creates a sparse piecewise-constant operator (sparse-matrix-valued function of time).

    Each of the piecewise-constant segments (time periods) is a scalar multiple
    of the operator.

    Parameters
    ----------
    signal : Pwc
        The scalar-valued piecewise-constant function of time :math:`a(t)`.
    operator : numpy.ndarray or scipy.sparse.coo_matrix
        The sparse operator :math:`A` to be scaled over time. If you pass a NumPy array
        then it will be internally converted into a sparse array.

    Returns
    -------
    SparsePwc
        The piecewise-constant sparse operator :math:`a(t)A`.

    See Also
    --------
    constant_sparse_pwc_operator : Create constant `SparsePwc`\s.
    density_matrix_evolution_pwc : Evolve a quantum state in an open system.
    pwc_operator : Corresponding operation for `Pwc`\s.
    sparse_pwc_hermitian_part : Create the Hermitian part of a `SparsePwc` operator.
    sparse_pwc_sum : Sum multiple `SparsePwc`\s.
    state_evolution_pwc : Evolve a quantum state.

    Examples
    --------
    Create a sparse PWC operator.

    >>> from scipy.sparse import coo_matrix
    >>> sigma_x = np.array([[0, 1], [1, 0]])
    >>> signal = graph.pwc_signal(values=np.array([1, 2, 3]), duration=0.1)
    >>> graph.sparse_pwc_operator(signal=signal, operator=coo_matrix(sigma_x))
    <SparsePwc: operation_name="sparse_pwc_operator", value_shape=(2, 2)>

    See more examples in the `How to simulate large open system dynamics
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-system-dynamics>`_
    user guide.
    """

    name = "sparse_pwc_operator"
    args = [
        forge.arg("signal", type=Pwc),
        forge.arg("operator", type=Union[np.ndarray, coo_matrix]),
    ]
    kwargs = {}  # SparsePwc doesn't accept `name` as an argument.
    rtype = SparsePwc
    categories = [Category.LARGE_SYSTEMS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        signal = kwargs.get("signal")
        operator = kwargs.get("operator")
        check_argument(
            signal.value_shape == (),
            "The signal must be scalar-valued.",
            {"signal": signal},
            {"signal.value_shape": signal.value_shape},
        )
        batch_shape = signal.batch_shape
        check_argument(
            batch_shape == (),
            "Batching is not supported for sparse_pwc.",
            {"signal": signal},
            {"signal.batch_shape": batch_shape},
        )
        operator_shape = validate_shape(operator, "operator")
        check_argument(
            len(operator_shape) == 2 and operator_shape[0] == operator_shape[1],
            "Operator must be a 2D square matrix.",
            {"operator": operator},
            {"operator.shape": operator_shape},
        )
        return SparsePwc(_operation, value_shape=operator_shape)


class ConstantSparsePwcOperator(Node):
    r"""
    Creates a constant sparse piecewise-constant operator over a specified duration.

    Parameters
    ----------
    duration : float
        The duration :math:`\tau` for the resulting piecewise-constant operator.
    operator : numpy.ndarray or scipy.sparse.coo_matrix
        The sparse operator :math:`A`. If you pass a NumPy array then it will be
        internally converted into a sparse array.

    Returns
    -------
    SparsePwc
        The constant operator :math:`t\mapsto A` (for :math:`0\leq t\leq\tau`).

    See Also
    --------
    constant_pwc_operator : Corresponding operation for `Pwc`\s.
    sparse_pwc_hermitian_part : Create the Hermitian part of a `SparsePwc` operator.
    sparse_pwc_operator : Create `SparsePwc` operators.
    sparse_pwc_sum : Sum multiple `SparsePwc`\s.

    Examples
    --------
    Create a constant sparse PWC operator.

    >>> from scipy.sparse import coo_matrix
    >>> sigma_x = np.array([[0, 1], [1, 0]])
    >>> graph.constant_sparse_pwc_operator(duration=0.1, operator=coo_matrix(sigma_x))
    <SparsePwc: operation_name="constant_sparse_pwc_operator", value_shape=(2, 2)>

    See more examples in the `How to simulate large open system dynamics
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-system-dynamics>`_
    user guide.
    """

    name = "constant_sparse_pwc_operator"
    args = [
        forge.arg("duration", type=float),
        forge.arg("operator", type=Union[np.ndarray, coo_matrix]),
    ]
    kwargs = {}  # SparsePwc doesn't accept `name` as an argument.
    rtype = SparsePwc
    categories = [Category.LARGE_SYSTEMS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        duration = kwargs.get("duration")
        operator = kwargs.get("operator")
        check_duration(duration, "duration")
        operator_shape = validate_shape(operator, "operator")
        check_argument(
            len(operator_shape) == 2 and operator_shape[0] == operator_shape[1],
            "Operator must be a 2D square matrix.",
            {"operator": operator},
            {"operator.shape": operator_shape},
        )
        return SparsePwc(_operation, value_shape=operator_shape)


class SparsePwcSum(Node):
    r"""
    Creates the sum of multiple sparse-matrix-valued piecewise-constant functions.

    Parameters
    ----------
    terms : list[SparsePwc]
        The individual piecewise-constant terms :math:`\{v_j(t)\}` to sum.
        All terms must be sparse, have values of the same shape,
        and have the same total duration
        but may have different numbers of segments of different durations.

    Returns
    -------
    SparsePwc
        The piecewise-constant function of time :math:`\sum_j v_j(t)`. It
        has the same shape as each of the `terms` that you provided.

    See Also
    --------
    constant_sparse_pwc_operator : Create constant `SparsePwc`\s.
    pwc_sum : Corresponding operation for `Pwc`\s.
    sparse_pwc_operator : Create `SparsePwc` operators.

    Examples
    --------
    Sum two sparse PWC operators.

    >>> from scipy.sparse import coo_matrix
    >>> sigma_x = np.array([[0, 1], [1, 0]])
    >>> sigma_y = np.array([[0, -1j], [1j, 0]])
    >>> sp_x = graph.constant_sparse_pwc_operator(duration=0.1, operator=coo_matrix(sigma_x))
    >>> sp_y = graph.constant_sparse_pwc_operator(duration=0.1, operator=coo_matrix(sigma_y))
    >>> graph.sparse_pwc_sum([sp_x, sp_y])
    <SparsePwc: operation_name="sparse_pwc_sum", value_shape=(2, 2)>

    See more examples in the `How to simulate large open system dynamics
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-system-dynamics>`_
    user guide.
    """

    name = "sparse_pwc_sum"
    args = [forge.arg("terms", type=List[SparsePwc])]
    kwargs = {}  # SparsePwcSum doesn't accept `name` as an argument.
    rtype = SparsePwc
    categories = [Category.LARGE_SYSTEMS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        terms = kwargs.get("terms")
        shape_0 = terms[0].value_shape
        for i in range(1, len(terms)):
            shape = terms[i].value_shape
            check_argument(
                shape == shape_0,
                "All the terms must have the same shape.",
                {"terms": terms},
                {
                    f"terms[{0}].value_shape": shape_0,
                    f"terms[{i}].value_shape": shape,
                },
            )
        return SparsePwc(_operation, value_shape=shape_0)


class SparsePwcHermitianPart(Node):
    r"""
    Creates the Hermitian part of a piecewise-constant operator.

    Parameters
    ----------
    operator : SparsePwc
        The operator :math:`A(t)`.

    Returns
    -------
    SparsePwc
        The Hermitian part :math:`\frac{1}{2}(A(t)+A^\dagger(t))`.

    See Also
    --------
    pwc_operator_hermitian_part : Create the Hermitian part of a `Pwc` operator.
    sparse_pwc_operator : Create `SparsePwc`\s.

    Examples
    --------
    Create a Hermitian sparse PWC operator.

    >>> from scipy.sparse import coo_matrix
    >>> sigma_m = np.array([[0, 1], [0, 0]])
    >>> sp_m = graph.constant_sparse_pwc_operator(duration=0.1, operator=coo_matrix(sigma_m))
    >>> graph.sparse_pwc_hermitian_part(sp_m)
    <SparsePwc: operation_name="sparse_pwc_hermitian_part", value_shape=(2, 2)>
    """

    name = "sparse_pwc_hermitian_part"
    args = [forge.arg("operator", type=SparsePwc)]
    kwargs = {}  # SparsePwc is not fetchable.
    rtype = SparsePwc
    categories = [Category.LARGE_SYSTEMS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operator = kwargs.get("operator")
        check_argument(
            isinstance(operator, SparsePwc),
            "The operator must be a SparsePwc.",
            {"operator": operator},
        )
        return SparsePwc(_operation, value_shape=operator.value_shape)


class StateEvolutionPwc(Node):
    r"""
    Calculates the time evolution of a state generated by a piecewise-constant
    Hamiltonian by using the Lanczos method.

    Parameters
    ----------
    initial_state : Tensor or np.ndarray
        The initial state as a Tensor or np.ndarray of shape ``[D]``.
    hamiltonian : Pwc or SparsePwc
        The control Hamiltonian. Uses sparse matrix multiplication if of type
        `SparsePwc`, which can be more efficient for large operators that are
        relatively sparse (contain mostly zeros).
    krylov_subspace_dimension : Tensor or int
        The dimension of the Krylov subspace `k` for the Lanczos method.
    sample_times :  np.ndarray(1D, real), optional
        The N times at which you want to sample the state. Elements must be non-negative
        and strictly increasing, with a supremum that is the duration of the `hamiltonian`.
        If omitted only the evolved state at the final time of the control Hamiltonian
        is returned.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        Tensor of shape ``[N, D]`` or ``[D]`` if `sample_times` is omitted
        representing the state evolution. The n-th element (along the first
        dimension) represents the state at ``sample_times[n]`` evolved from
        the initial state.

    Warnings
    --------
    This calculation can be relatively inefficient for small systems (very roughly
    speaking, when the dimension of your Hilbert space is less than around 100; the
    exact cutoff depends on the specifics of your problem though). You should generally
    first try using `time_evolution_operators_pwc` to get the full time evolution
    operators (and evolve your state using those), and only switch to this method
    if that approach proves too slow or memory intensive. See the
    `How to simulate quantum dynamics for noiseless systems using graphs`_ user guide
    for an example of calculating state evolution with `time_evolution_operators_pwc`.

    .. _How to simulate quantum dynamics for noiseless systems using graphs:
        https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-quantum-
        dynamics-for-noiseless-systems-using-graphs

    See Also
    --------
    density_matrix_evolution_pwc : Corresponding operation for open systems.
    discretize_stf : Discretize an `Stf` into a `Pwc`.
    estimated_krylov_subspace_dimension_lanczos : Obtain a Krylov subspace dimension to use
        with this integrator.
    sparse_pwc_operator : Create `SparsePwc` operators.
    time_evolution_operators_pwc : Unitary time evolution operators for quantum systems with
        `Pwc` Hamiltonians.

    Notes
    -----
    The Lanczos algorithm calculates the unitary evolution of a state in the Krylov
    subspace. This subspace is spanned by the states resulting from applying the first
    `k` powers of the Hamiltonian on the input state, with `k` being the subspace dimension,
    much smaller that the full Hilbert space dimension. This allows for an efficient
    state propagation in high-dimensional systems compared to calculating the full
    unitary operator.

    Moreover, this function uses sparse matrix multiplication when the Hamiltonian is passed as a
    `SparsePwc`. This can lead to more efficient calculations when they involve large operators that
    are relatively sparse (contain mostly zeros). In this case, the initial state is still a densely
    represented array or tensor.

    Note that increasing the density of `sample_times` does not affect the accuracy of the
    integration. However, increasing the Krylov subspace dimension or subdividing the Hamiltonian
    into shorter piecewise-constant segments can reduce the integration error, at the expense of
    longer computation times.

    Examples
    --------
    See example in the `How to optimize controls on large sparse Hamiltonians
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-on-
    large-sparse-hamiltonians>`_ user guide.
    """

    name = "state_evolution_pwc"
    args = [
        forge.arg("initial_state", type=Union[Tensor, np.ndarray]),
        forge.arg("hamiltonian", type=Union[Pwc, SparsePwc]),
        forge.arg("krylov_subspace_dimension", type=Union[int, Tensor]),
        forge.arg("sample_times", type=Optional[np.ndarray], default=None),
    ]
    rtype = Tensor
    categories = [Category.LARGE_SYSTEMS, Category.TIME_EVOLUTION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        initial_state = kwargs.get("initial_state")
        state_shape = validate_shape(initial_state, "initial_state")
        check_argument(
            len(state_shape) == 1,
            "The initial state must be 1D.",
            {"initial_state": initial_state},
            extras={"initial_state.shape": state_shape},
        )
        hamiltonian = kwargs.get("hamiltonian")
        sample_times = kwargs.get("sample_times")
        check_argument_numeric(initial_state, "initial_state")
        if sample_times is not None:
            check_sample_times(sample_times, "sample_times")
        check_argument(
            isinstance(hamiltonian, (SparsePwc, Pwc)),
            "The Hamiltonian must be a SparsePwc or a Pwc.",
            {"hamiltonian": hamiltonian},
        )
        if isinstance(hamiltonian, Pwc):
            check_argument(
                hamiltonian.batch_shape == (),
                "Hamiltonian cannot contain a batch.",
                {"hamiltonian": hamiltonian},
                extras={"hamiltonian.batch_shape": hamiltonian.batch_shape},
            )
        hamiltonian_value_shape = hamiltonian.value_shape
        validate_hamiltonian(hamiltonian, "hamiltonian")
        check_argument(
            state_shape[0] == hamiltonian_value_shape[-1],
            "The Hilbert space dimensions of the state and the Hamiltonian must be equal.",
            {"initial_state": initial_state, "hamiltonian": hamiltonian},
            extras={
                "initial_state.shape": state_shape,
                "hamiltonian.value_shape": hamiltonian_value_shape,
            },
        )
        if sample_times is None:
            shape = state_shape
        else:
            shape = (len(sample_times),) + state_shape
        return Tensor(_operation, shape=shape)


class EstimatedKrylovSubspaceDimensionLanczos(Node):
    r"""
    Calculates an appropriate Krylov subspace dimension (:math:`k`) to use in the Lanczos
    integrator while keeping the total error in the evolution below a given error tolerance.

    Note that you can provide your own estimation of the Hamiltonian spectral range or use the
    `spectral_range` operation to perform that calculation.

    Parameters
    ----------
    spectral_range : Tensor or float
        Estimated order of magnitude of Hamiltonian spectral range (difference
        between largest and smallest eigenvalues).
    duration : float
        The total evolution time.
    maximum_segment_duration : float
        The maximum duration of the piecewise-constant Hamiltonian segments.
    error_tolerance : float, optional
        Tolerance for the error in the integration, defined as the Frobenius norm of
        the vectorial difference between the exact state and the estimated state.
        Defaults to 1e-6.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        Recommended value of :math:`k` to use in a Lanczos integration with a Hamiltonian with a
        similar spectral range to the one passed.

    See Also
    --------
    spectral_range : Range of the eigenvalues of a Hermitian operator.
    state_evolution_pwc : Evolve a quantum state.

    Notes
    -----
    To provide the recommended :math:`k` parameter, this function uses the bound in the error for
    the Lanczos algorithm [1]_ [2]_ as an estimate for the error. For a single time step this gives

    .. math::
        \mathrm{error} \leq 12 \exp \left( - \frac{(w\tau)^2}{16 k} \right)
        \left (\frac{e w \tau}{ 4 k}  \right )^{k}

    where :math:`\tau` is the time step and :math:`w` is the spectral range of the Hamiltonian.

    As this bound overestimates the error, the actual resulting errors with the recommended
    parameter are expected to be (a few orders of magnitude) smaller than the requested tolerance.

    References
    ----------
    .. [1] `N. Del Buono and L. Lopez,
           Lecture Notes in Computer Science 2658, 111 (2003).
           <https://doi.org/10.1007/3-540-44862-4_13>`_

    .. [2] `M. Hochbruck and C. Lubich,
           SIAM Journal on Numerical Analysis 34, 1911 (1997).
           <https://doi.org/10.1137/S0036142995280572>`_

    Examples
    --------
    >>> graph.estimated_krylov_subspace_dimension_lanczos(
    ...     spectral_range=30.0,
    ...     duration=5e-7,
    ...     maximum_segment_duration=2.5e-8,
    ...     error_tolerance=1e-5,
    ...     name="dim",
    ... )
    <Tensor: name="dim", operation_name="estimated_krylov_subspace_dimension_lanczos", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["dim"])
    >>> result.output["dim"]["value"]
    2

    See more examples in the `How to optimize controls on large sparse Hamiltonians
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-on-
    large-sparse-hamiltonians>`_ user guide.
    """

    name = "estimated_krylov_subspace_dimension_lanczos"
    args = [
        forge.arg("spectral_range", type=Union[Tensor, float]),
        forge.arg("duration", type=float),
        forge.arg("maximum_segment_duration", type=float),
        forge.arg("error_tolerance", type=float, default=1e-6),
    ]
    rtype = Tensor
    categories = [Category.LARGE_SYSTEMS, Category.TIME_EVOLUTION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        duration = kwargs.get("duration")
        maximum_segment_duration = kwargs.get("maximum_segment_duration")
        error_tolerance = kwargs.get("error_tolerance")
        check_argument(
            maximum_segment_duration > 0,
            "The maximum segment duration must be positive.",
            {"maximum_segment_duration": maximum_segment_duration},
        )
        check_argument(
            duration > 0, "The duration must be positive.", {"duration": duration}
        )
        check_argument(
            maximum_segment_duration <= duration,
            "The maximum segment duration must be less than or equal to duration.",
            {
                "maximum_segment_duration": maximum_segment_duration,
                "duration": duration,
            },
        )
        check_argument(
            error_tolerance > 0,
            "The error tolerance must be positive.",
            {"error_tolerance": error_tolerance},
        )

        return Tensor(_operation, shape=())


class SpectralRange(Node):
    r"""
    Obtains the range of the eigenvalues of a Hermitian operator.

    This function provides an estimate of the difference between the
    highest and the lowest eigenvalues of the operator. You can adjust its
    precision by modifying its default parameters.

    Parameters
    ----------
    operator : np.ndarray or scipy.sparse.coo_matrix or Tensor
        The Hermitian operator :math:`M` whose range of eigenvalues you
        want to determine.
    iteration_count : int, optional
        The number of iterations :math:`N` in the calculation. Defaults to
        3000. Choose a higher number to improve the precision, or a smaller
        number to make the estimation run faster.
    seed : int, optional
        The random seed that the function uses to choose the initial random
        vector :math:`\left| r \right\rangle`. Defaults to ``None``, which
        means that the function uses a different seed in each run.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor (scalar, real)
        The difference between the largest and the smallest eigenvalues of
        the operator.

    Warnings
    --------
    This calculation can be expensive, so we recommend that you run it
    before the optimization, if possible. You can do this by using a
    representative or a worst-case operator.

    Notes
    -----
    This function repeatedly multiplies the operator :math:`M` with a
    random vector :math:`\left| r \right\rangle`. In terms of the operator's
    eigenvalues :math:`\{ v_i \}` and eigenvectors
    :math:`\{\left|v_i \right\rangle\}`, the result of :math:`N` matrix
    multiplications is:

    .. math::
        M^N \left|r\right\rangle = \sum_i v_i^N \left|v_i\right\rangle
        \left\langle v_i \right. \left| r \right\rangle.

    For large :math:`N`, the term corresponding to the eigenvalue with
    largest absolute value :math:`V` will dominate the sum, as long as
    :math:`\left|r\right\rangle` has a non-zero overlap with its
    eigenvector. The function then retrieves the eigenvalue :math:`V` via:

    .. math::
        V \approx \frac{\left\langle r \right| M^{2N+1} \left| r
        \right\rangle}{\left\| M^N \left| r \right\rangle \right\|^2}.

    The same procedure applied to the matrix :math:`M-V` allows the function
    to find the eigenvalue at the opposite end of the spectral range.

    Examples
    --------
    >>> operator = np.diag([10, 40])
    >>> graph.spectral_range(operator, name="spectral_range")
    <Tensor: name="spectral_range", operation_name="spectral_range", shape=()>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["spectral_range"]
    ... )
    >>> result.output["spectral_range"]["value"]
    30.0

    See more examples in the `How to optimize controls on large sparse Hamiltonians
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-on
    -large-sparse-hamiltonians>`_ user guide.
    """

    name = "spectral_range"
    args = [
        forge.arg("operator", type=Union[Tensor, np.ndarray, coo_matrix]),
        forge.arg("iteration_count", type=int, default=3000),
        forge.arg("seed", type=Optional[int], default=None),
    ]
    rtype = Tensor
    categories = [Category.LARGE_SYSTEMS, Category.TIME_EVOLUTION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operator = kwargs.get("operator")
        iteration_count = kwargs.get("iteration_count")
        check_operator(operator, "operator")
        operator_shape = validate_shape(operator, "operator")
        check_argument(
            len(operator_shape) == 2,
            "Batches of operators are not supported.",
            {"operator": operator},
            extras={"operator.shape": operator_shape},
        )
        check_argument_integer(iteration_count, "iteration_count")
        check_argument(
            iteration_count > 0,
            "The number of iterations must be greater than zero.",
            {"iteration_count": iteration_count},
        )
        if not isinstance(operator, Tensor):
            check_argument_hermitian(operator, "operator")
        return Tensor(_operation, shape=())
