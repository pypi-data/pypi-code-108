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
"""
Module for all the node related to PWC.
"""
from typing import (
    List,
    Union,
)

import forge
import numpy as np

from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    Pwc,
    Tensor,
)
from qctrlcommons.node.utils import (
    validate_batch_and_value_shapes,
    validate_hamiltonian,
    validate_shape,
)
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_integer,
    check_argument_iterable,
    check_argument_numeric,
    check_duration,
    check_operator,
    check_sample_times,
)


class PwcOperation(Node):
    r"""
    Creates a piecewise-constant function of time.

    Parameters
    ----------
    durations : np.ndarray (1D, real)
        The durations :math:`\{\delta t_n\}` of the :math:`N` constant
        segments.
    values : np.ndarray or Tensor
        The values :math:`\{v_n\}` of the function on the constant segments.
        The dimension corresponding to `time_dimension` must be the same
        length as `durations`. To create a batch of
        :math:`B_1 \times \ldots \times B_n` piecewise-constant tensors of
        shape :math:`D_1 \times \ldots \times D_m`, provide this `values`
        parameter as an object of shape
        :math:`B_1\times\ldots\times B_n\times N\times D_1\times\ldots\times D_m`.
    time_dimension : int, optional
        The axis along `values` corresponding to time. All dimensions that
        come before the `time_dimension` are batch dimensions: if there are
        :math:`n` batch dimensions, then `time_dimension` is also :math:`n`.
        Defaults to 0, which corresponds to no batch. Note that you can
        pass a negative value to refer to the time dimension.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant function of time :math:`v(t)`, satisfying
        :math:`v(t)=v_n` for :math:`t_{n-1}\leq t\leq t_n`, where
        :math:`t_0=0` and :math:`t_n=t_{n-1}+\delta t_n`. If you provide a
        batch of values, the returned `Pwc` represents a
        corresponding batch of :math:`B_1 \times \ldots \times B_n`
        functions :math:`v(t)`, each of shape
        :math:`D_1 \times \ldots \times D_m`.

    See Also
    --------
    pwc_operator : Create `Pwc` operators.
    pwc_signal : Create `Pwc` signals from (possibly complex) values.
    pwc_sum : Sum multiple `Pwc`\s.

    Examples
    --------
    Create a Hamiltonian from a piecewise-constant signal with non-uniform segment durations.

    >>> omega = graph.pwc(
    ...     values=np.array([1, 2, 3]), durations=np.array([0.1, 0.2, 0.3]), name="omega"
    ... )
    >>> omega
    <Pwc: name="omega", operation_name="pwc", value_shape=(), batch_shape=()>
    >>> sigma_z = np.array([[1, 0], [0, -1]])
    >>> hamiltonian = omega * sigma_z
    >>> hamiltonian.name = "hamiltonian"
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["hamiltonian"])
    >>> result.output["hamiltonian"]
    [
        {"value": array([[1.0, 0.0], [0.0, -1.0]]), "duration": 0.1},
        {"value": array([[2.0, 0.0], [0.0, -2.0]]), "duration": 0.2},
        {"value": array([[3.0, 0.0], [0.0, -3.0]]), "duration": 0.3},
    ]

    See more examples in the `How to simulate quantum dynamics subject to noise with graphs
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-
    quantum-dynamics-subject-to-noise-with-graphs>`_ user guide.

    """

    name = "pwc"
    args = [
        forge.arg("durations", type=np.ndarray),
        forge.arg("values", type=Union[np.ndarray, Tensor]),
        forge.arg("time_dimension", type=int, default=0),
    ]

    rtype = Pwc
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        durations = kwargs.get("durations")
        values = kwargs.get("values")
        time_dimension = kwargs.get("time_dimension")
        check_argument_numeric(durations, "durations")
        check_argument_numeric(values, "values")
        check_argument_integer(time_dimension, "time_dimension")
        value_shape = validate_shape(values, "values")
        durations_shape = validate_shape(durations, "durations")
        check_argument(
            len(durations_shape) == 1,
            "The shape of durations must have exactly one dimension.",
            {"durations": durations},
        )
        check_argument(
            -len(value_shape) <= time_dimension < len(value_shape),
            "The `time_dimension` must be a valid `values` dimension.",
            {"time_dimension": time_dimension, "values": values},
        )
        check_argument(
            value_shape[time_dimension] == durations_shape[0],
            "The size of the `time_dimension` of `values` must be equal to the length"
            " of `durations`.",
            {
                "time_dimension": time_dimension,
                "values": values,
                "durations": durations,
            },
        )
        for index, duration in enumerate(durations):
            check_duration(duration, f"durations[{index}]")
        if time_dimension < 0:
            time_dimension = len(value_shape) + time_dimension
        return Pwc(
            _operation,
            value_shape=value_shape[time_dimension + 1 :],
            durations=durations,
            batch_shape=value_shape[:time_dimension],
        )


class PwcSignal(Node):
    r"""
    Creates a piecewise-constant signal (scalar-valued function of time).

    Use this function to create a piecewise-constant signal in which the
    constant segments all have the same duration.

    Parameters
    ----------
    values : np.ndarray or Tensor
        The values :math:`\{\alpha_n\}` of the :math:`N` constant segments.
        These can represent either a single sequence of segment values or a
        batch of them. To create a batch of
        :math:`B_1 \times \ldots \times B_n` signals, represent these
        `values` as a tensor of shape
        :math:`B_1 \times \ldots \times B_n \times N`.
    duration : float
        The total duration :math:`\tau` of the signal.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant function of time :math:`\alpha(t)`, satisfying
        :math:`\alpha(t)=\alpha_n` for :math:`t_{n-1}\leq t\leq t_n`, where
        :math:`t_n=n\tau/N` (where :math:`N` is the number of values
        in :math:`\{\alpha_n\}`). If you provide a batch of values, the
        returned `Pwc` represents a corresponding batch of
        :math:`B_1 \times \ldots \times B_n` functions :math:`\alpha(t)`.

    See Also
    --------
    complex_pwc_signal : Create complex `Pwc` signals from their moduli and phases.
    pwc : Corresponding operation with support for segments of different durations.
    pwc_operator : Create `Pwc` operators.
    pwc_sum : Sum multiple `Pwc`\s.
    symmetrize_pwc : Symmetrize `Pwc`\s.

    Examples
    --------
    Create a piecewise-constant signal with uniform segment duration.

    >>> graph.pwc_signal(duration=0.1, values=np.array([2, 3]), name="signal")
    <Pwc: name="signal", operation_name="pwc_signal", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["signal"])
    >>> result.output["signal"]
    [{'value': 2.0, 'duration': 0.05}, {'value': 3.0, 'duration': 0.05}]

    See more examples in the `Get familiar with graphs <https://docs.q-ctrl.com/
    boulder-opal/tutorials/get-familiar-with-graphs>`_ tutorial.
    """

    name = "pwc_signal"
    args = [
        forge.arg("values", type=Union[np.ndarray, Tensor]),
        forge.arg("duration", type=float),
    ]
    rtype = Pwc
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        values = kwargs.get("values")
        duration = kwargs.get("duration")
        check_argument_numeric(values, "values")
        check_duration(duration, "duration")
        shape = validate_shape(values, "values")
        check_argument(
            len(shape) > 0,
            "The shape of values must have at least one dimension.",
            {"values": values},
        )
        durations = duration / shape[-1] * np.ones(shape[-1])
        return Pwc(
            _operation,
            value_shape=(),
            durations=durations,
            batch_shape=shape[:-1],
        )


class ComplexPwcSignal(Node):
    r"""
    Creates a complex piecewise-constant signal from moduli and phases.

    Use this function to create a complex piecewise-constant signal from
    moduli and phases defined for each segment, in which the constant segments
    all have the same duration.

    Parameters
    ----------
    moduli : np.ndarray(real) or Tensor(real)
        The moduli :math:`\{\Omega_n\}` of the values of :math:`N` constant
        segments. These can represent either the moduli of a single
        sequence of segment values or of a batch of them. To provide a
        batch of sequences of segment values of shape
        :math:`B_1 \times \ldots \times B_n`, represent these moduli as a
        tensor of shape :math:`B_1 \times \ldots \times B_n \times N`.
    phases : np.ndarray(real) or Tensor(real)
        The phases :math:`\{\phi_n\}` of the complex segment values. Must
        have the same length as `moduli` (or same shape, if you're
        providing a batch).
    duration : float
        The total duration :math:`\tau` of the signal.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc(complex)
        The piecewise-constant function of time :math:`v(t)`, satisfying
        :math:`v(t)=\Omega_n e^{i\phi_n}` for :math:`t_{n-1}\leq t\leq t_n`,
        where :math:`t_n=n\tau/N` (where :math:`N` is the number of
        values in :math:`\{\Omega_n\}` and :math:`\{\phi_n\}`). If you
        provide a batch of `moduli` and `phases`, the returned `Pwc`
        represents a corresponding batch of
        :math:`B_1 \times \ldots \times B_n` functions :math:`v(t)`.

    See Also
    --------
    pwc_signal : Create `Pwc` signals from (possibly complex) values.

    Examples
    --------
    Create a complex piecewise-constant signal with batched moduli and phases.

    >>> moduli = np.array([[1, 2], [3, 4]])
    >>> phases = np.array([[0.1, 0.2], [0.5, 0.7]])
    >>> graph.complex_pwc_signal(moduli=moduli, phases=phases, duration=0.2, name="signal")
    <Pwc: name="signal", operation_name="complex_pwc_signal", value_shape=(), batch_shape=(2,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["signal"])
    >>> result.output["signal"]
    [
        [
            {"value": (0.9950041652780258 + 0.09983341664682815j), "duration": 0.1},
            {"value": (1.9601331556824833 + 0.39733866159012243j), "duration": 0.1},
        ],
        [
            {"value": (2.6327476856711183 + 1.438276615812609j), "duration": 0.1},
            {"value": (3.059368749137954 + 2.576870748950764j), "duration": 0.1},
        ],
    ]

    See more examples in the `Design robust single-qubit gates using computational graphs
    <https://docs.q-ctrl.com/boulder-opal/tutorials/design-robust-single-qubit-gates-
    using-computational-graphs>`_ tutorial.
    """

    name = "complex_pwc_signal"
    args = [
        forge.arg("moduli", type=Union[np.ndarray, Tensor]),
        forge.arg("phases", type=Union[np.ndarray, Tensor]),
        forge.arg("duration", type=float),
    ]
    rtype = Pwc
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        moduli = kwargs.get("moduli")
        phases = kwargs.get("phases")
        duration = kwargs.get("duration")
        check_argument_numeric(moduli, "moduli")
        check_argument_numeric(phases, "phases")
        check_duration(duration, "duration")
        moduli_shape = validate_shape(moduli, "moduli")
        phases_shape = validate_shape(phases, "phases")
        check_argument(
            len(moduli_shape) > 0,
            "The shape of moduli must have at least one dimension.",
            {"moduli": moduli},
        )
        check_argument(
            moduli_shape == phases_shape,
            "The shape of moduli and phases must be equal.",
            {"moduli": moduli, "phases": phases},
        )
        durations = duration / moduli_shape[-1] * np.ones(moduli_shape[-1])
        return Pwc(
            _operation,
            value_shape=(),
            durations=durations,
            batch_shape=moduli_shape[:-1],
        )


class PwcOperator(Node):
    r"""
    Creates a constant operator multiplied by a piecewise-constant signal.

    Parameters
    ----------
    signal : Pwc
        The piecewise-constant signal :math:`a(t)`, or a batch of
        piecewise-constant signals.
    operator : np.ndarray or Tensor
        The operator :math:`A`. It must have two equal dimensions.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant operator :math:`a(t)A` (or a batch of
        piecewise-constant operators, if you provide a batch of
        piecewise-constant signals).

    See Also
    --------
    complex_pwc_signal : Create complex `Pwc` signals from their moduli and phases.
    constant_pwc_operator : Create constant `Pwc`\s.
    pwc : Create piecewise-constant functions.
    pwc_operator_hermitian_part : Hermitian part of a piecewise-constant operator.
    pwc_signal : Create `Pwc` signals from (possibly complex) values.
    pwc_sum : Sum multiple `Pwc`\s.
    stf_operator : Corresponding operation for `Stf`\s.
    stf_operator_hermitian_part : Corresponding operation for `Stf`\s.

    Examples
    --------
    Create a piecewise-constant operator with non-uniform segment durations.

    >>> sigma_z = np.array([[1.0, 0.0],[0.0, -1.0]])
    >>> graph.pwc_operator(
    ...     signal=graph.pwc(durations=np.array([0.1, 0.2]), values=np.array([1, 2])),
    ...     operator=sigma_z,
    ...     name="operator",
    ... )
    <Pwc: name="operator", operation_name="pwc_operator", value_shape=(2, 2), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["operator"])
    >>> result.operator["operator"]
    [
        {"value": array([[1.0, 0.0], [0.0, -1.0]]), "duration": 0.1},
        {"value": array([[2.0, 0.0], [0.0, -2.0]]), "duration": 0.2},
    ]

    See more examples in the `How to represent quantum systems using graphs
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-represent-quantum-
    systems-using-graphs>`_ user guide.
    """

    name = "pwc_operator"
    args = [
        forge.arg("signal", type=Pwc),
        forge.arg("operator", type=Union[np.ndarray, Tensor]),
    ]
    rtype = Pwc
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        signal = kwargs.get("signal")
        operator = kwargs.get("operator")
        check_argument(
            isinstance(signal, Pwc),
            "The signal must be a Pwc.",
            {"signal": signal},
        )
        batch_shape, signal_value_shape = validate_batch_and_value_shapes(
            signal, "signal"
        )
        check_argument(
            signal_value_shape == (),
            "The signal must be scalar-valued.",
            {"signal": signal},
        )

        value_shape = validate_shape(operator, "operator")
        check_operator(operator, "operator")
        check_argument(
            len(value_shape) == 2,
            "The operator must be a matrix, not a batch.",
            {"operator": operator},
            extras={"operator.shape": value_shape},
        )
        return Pwc(
            _operation,
            value_shape=value_shape,
            durations=signal.durations,
            batch_shape=batch_shape,
        )


class ConstantPwcOperator(Node):
    r"""
    Creates a constant piecewise-constant operator over a specified duration.

    Parameters
    ----------
    duration : float
        The duration :math:`\tau` for the resulting piecewise-constant
        operator.
    operator : np.ndarray or Tensor
        The operator :math:`A`, or a batch of operators. It must have at
        least two dimensions, and its last two dimensions must be equal.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The constant operator :math:`t\mapsto A` (for :math:`0\leq t\leq\tau`)
        (or a batch of constant operators, if you provide a batch of operators).

    See Also
    --------
    constant_stf_operator : Corresponding operation for `Stf`\s.
    pwc_operator : Create `Pwc` operators.
    pwc_operator_hermitian_part : Hermitian part of a piecewise-constant operator.

    Examples
    --------
    Create a Hamiltonian from a batched constant operator.

    >>> sigma_x = np.array([[0.0, 1.0], [1.0, 0.0]])
    >>> sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]])
    >>> batched_operators = np.asarray([sigma_x, sigma_z])
    >>> graph.constant_pwc_operator(duration=0.1, operator=batched_operators,  name="op")
    <Pwc: name="op", operation_name="constant_pwc_operator", value_shape=(2, 2), batch_shape=(2,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["op"])
    >>> result.output["op"]
    [
        [{"value": array([[0.0, 1.0], [1.0, 0.0]]), "duration": 0.1}],
        [{"value": array([[1.0, 0.0], [0.0, -1.0]]), "duration": 0.1}],
    ]

    See more examples in the `How to represent quantum systems using graphs
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-represent-quantum-
    systems-using-graphs>`_ user guide.
    """

    name = "constant_pwc_operator"
    args = [
        forge.arg("duration", type=float),
        forge.arg("operator", type=Union[np.ndarray, Tensor]),
    ]
    rtype = Pwc
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        duration = kwargs.get("duration")
        operator = kwargs.get("operator")
        check_duration(duration, "duration")
        shape = validate_shape(operator, "operator")
        check_operator(operator, "operator")
        return Pwc(
            _operation,
            value_shape=shape[-2:],
            durations=np.array([duration]),
            batch_shape=shape[:-2],
        )


class ConstantPwc(Node):
    r"""
    Creates a piecewise-constant function of time that is constant over a specified duration.

    Parameters
    ----------
    constant : number or np.ndarray or Tensor
        The value :math:`c` of the function on the constant segment.
        To create a batch of :math:`B_1 \times \ldots \times B_n` piecewise-constant
        functions of shape :math:`D_1 \times \ldots \times D_m`, provide this `constant`
        parameter as an object of shape
        :math:`B_1\times\ldots\times B_n\times D_1\times\ldots\times D_m`.
    duration : float
        The duration :math:`\tau` for the resulting piecewise-constant function.
    batch_dimension_count : int, optional
        The number of batch dimensions, :math:`n` in `constant`.
        If provided, the first :math:`n` dimensions of `constant` are considered batch dimensions.
        Defaults to 0, which corresponds to no batch.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The constant function :math:`f(t) = c` (for :math:`0\leq t\leq\tau`)
        (or a batch of constant functions, if you provide `batch_dimension_count`).

    See Also
    --------
    constant_pwc_operator : Create constant `Pwc` operators.
    constant_stf : Corresponding operation for `Stf`\s.
    pwc : Create piecewise-constant functions.

    Examples
    --------
    Create a batched piecewise-constant function.

    >>> constant = np.arange(12).reshape((2, 2, 3))
    >>> graph.constant_pwc(
    ...     constant=constant, duration=0.1, batch_dimension_count=1, name="constant"
    ... )
    <Pwc: name="constant", operation_name="constant_pwc", value_shape=(2, 3), batch_shape=(2,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["constant"])
    >>> result.output["constant"]
    [
        [{"value": array([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]]), "duration": 0.1}],
        [{"value": array([[6.0, 7.0, 8.0], [9.0, 10.0, 11.0]]), "duration": 0.1}],
    ]

    See more examples in the `Simulate the dynamics of a single qubit using computational graphs
    <https://docs.q-ctrl.com/boulder-opal/tutorials/simulate-the-dynamics-of-a-single-qubit-
    using-computational-graphs>`_ tutorial.
    """

    name = "constant_pwc"
    args = [
        forge.arg("constant", type=Union[float, complex, np.ndarray, Tensor]),
        forge.arg("duration", type=float),
        forge.arg("batch_dimension_count", type=int, default=0),
    ]
    rtype = Pwc
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        constant = kwargs.get("constant")
        duration = kwargs.get("duration")
        batch_dimension_count = kwargs.get("batch_dimension_count")

        check_argument_numeric(constant, "constant")
        check_duration(duration, "duration")
        check_argument_integer(batch_dimension_count, "batch_dimension_count")

        shape = validate_shape(constant, "constant")
        check_argument(
            len(shape) >= batch_dimension_count,
            "The number of batch dimensions must not be larger than the number "
            "of dimensions of the input constant.",
            {"constant": constant, "batch_dimension_count": batch_dimension_count},
            {"Number of value dimensions": len(shape)},
        )
        check_argument(
            batch_dimension_count >= 0,
            "The number of batch dimensions must not be negative.",
            {"batch_dimension_count": batch_dimension_count},
        )

        return Pwc(
            _operation,
            value_shape=shape[batch_dimension_count:],
            durations=np.array([duration]),
            batch_shape=shape[:batch_dimension_count],
        )


class PwcOperatorHermitianPart(Node):
    # pylint:disable=line-too-long
    r"""
    Creates the Hermitian part of a piecewise-constant operator.

    Parameters
    ----------
    operator : Pwc
        The operator :math:`A(t)`, or a batch of operators.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The Hermitian part :math:`\frac{1}{2}(A(t)+A^\dagger(t))`
        (or a batch of Hermitian parts, if you provide a batch of operators).

    See Also
    --------
    constant_pwc_operator : Create constant `Pwc`\s.
    pwc_operator : Create `Pwc` operators.
    sparse_pwc_hermitian_part : Create the Hermitian part of a `SparsePwc` operator.

    Examples
    --------
    Creates a Hamiltonian from a non-Hermitian operator.

    >>> omega = graph.pwc(durations=np.array([0.1, 0.2]), values=np.array([0.2, 0.4]))
    >>> sigma_m = np.array([[0, 1], [0, 0]])
    >>> operator = omega * sigma_m
    >>> graph.pwc_operator_hermitian_part(operator=operator, name="hamiltonian")
    <Pwc: name="hamiltonian", operation_name="pwc_operator_hermitian_part", value_shape=(2, 2), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["hamiltonian"])
    >>> result.output["hamiltonian"]
    [
        {"value": array([[0.0, 0.1], [0.1, 0.0]]), "duration": 0.1},
        {"value": array([[0.0, 0.2], [0.2, 0.0]]), "duration": 0.2},
    ]

    See more examples in the `Simulate the dynamics of a single qubit using computational graphs
    <https://docs.q-ctrl.com/boulder-opal/tutorials/simulate-the-dynamics-of-a-single-qubit-
    using-computational-graphs>`_ tutorial.
    """

    # pylint:enable=line-too-long
    name = "pwc_operator_hermitian_part"
    args = [
        forge.arg("operator", type=Pwc),
    ]
    rtype = Pwc
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operator = kwargs.get("operator")
        check_argument(
            isinstance(operator, Pwc),
            "The operator must be a Pwc.",
            {"operator": operator},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            operator,
            "operator",
        )
        return Pwc(
            _operation,
            value_shape=value_shape,
            durations=operator.durations,
            batch_shape=batch_shape,
        )


class PwcSum(Node):
    r"""
    Creates the sum of multiple piecewise-constant terms.

    Parameters
    ----------
    terms : list[Pwc]
        The individual piecewise-constant terms :math:`\{v_j(t)\}` to sum. All
        terms must have the same duration, values of the same shape, and the
        same batch shape, but may have different segmentations (different
        numbers of segments of different durations) and different dtypes of
        segment values.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant function (or batch of functions) of time
        :math:`\sum_j v_j(t)`. Its values have the same shape as the values of
        each of the `terms` that you provided. If each of the `terms` represents
        a batch of functions, this result represents a batch of functions with
        the same batch shape. If any `term` has complex-valued segments, the
        value of the returned Pwc is complex, otherwise is float.

    See Also
    --------
    discretize_stf : Discretize an `Stf` into a `Pwc`.
    pwc : Create piecewise-constant functions.
    pwc_operator : Create `Pwc` operators.
    pwc_signal : Create `Pwc` signals from (possibly complex) values.
    stf_sum : Corresponding operation for `Stf`\s.

    Examples
    --------
    Sum a list of piecewise constant terms of different durations.

    >>> x = graph.pwc(durations=np.array([0.1, 0.3]), values=np.array([1, 2]))
    >>> y = graph.pwc(durations=np.array([0.2, 0.2]), values=np.array([3, 1]))
    >>> graph.pwc_sum([x, y], name="sum")
    <Pwc: name="sum", operation_name="pwc_sum", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum"])
    >>> result.output["sum"]
    [
        {"value": 4.0, "duration": 0.1},
        {"value": 5.0, "duration": 0.1},
        {"value": 3.0, "duration": 0.2},
    ]

    See more examples in the `How to optimize controls robust to strong noise sources
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-robust-to-
    strong-noise-sources>`_ user guide.
    """

    name = "pwc_sum"
    args = [forge.arg("terms", type=List[Pwc])]
    rtype = Pwc
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        terms = kwargs.get("terms")
        check_argument_iterable(terms, "terms")
        check_argument(
            all(isinstance(term, Pwc) for term in terms),
            "Each of the terms must be a Pwc.",
            {"terms": terms},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            terms[0],
            "terms[0]",
        )
        check_argument(
            all(
                (
                    (term.value_shape == value_shape)
                    and (term.batch_shape == batch_shape)
                )
                for term in terms[1:]
            ),
            "All the terms must have the same shape.",
            {"terms": terms},
        )
        check_argument(
            all(
                np.allclose(np.sum(terms[0].durations), np.sum(term.durations))
                for term in terms
            ),
            "All the terms must have the same total duration.",
            {"terms": terms},
            extras={
                "total duration of each term": [
                    np.sum(term.durations) for term in terms
                ]
            },
        )
        upsampled_durations = np.diff(
            np.insert(
                np.unique(
                    np.concatenate([np.cumsum(term.durations) for term in terms])
                ),
                0,
                0,
            )
        )
        return Pwc(
            _operation,
            value_shape=value_shape,
            durations=upsampled_durations,
            batch_shape=batch_shape,
        )


class SymmetrizePwc(Node):
    r"""
    Creates the symmetrization of a piecewise-constant function.

    Parameters
    ----------
    pwc : Pwc
        The piecewise-constant function :math:`v(t)` to symmetrize.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant function :math:`w(t)` defined by
        :math:`w(t)=v(t)` for :math:`0\leq t\leq \tau` and
        :math:`w(t)=v(2\tau-t)` for :math:`\tau\leq t\leq 2\tau`, where
        :math:`\tau` is the duration of :math:`v(t)`.

    See Also
    --------
    pwc_signal : Create `Pwc` signals from (possibly complex) values.

    Examples
    --------

    Create a symmetric piecewise constant function.

    >>> x = graph.pwc(durations=np.array([0.1, 0.3]), values=np.array([1, 2]))
    >>> graph.symmetrize_pwc(x, name="symmetrize")
    <Pwc: name="symmetrize", operation_name="symmetrize_pwc", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["symmetrize"])
    >>> result.output["symmetrize"]
    [
        {"value": 1.0, "duration": 0.1},
        {"value": 2.0, "duration": 0.3},
        {"value": 2.0, "duration": 0.3},
        {"value": 1.0, "duration": 0.1},
    ]

    See more examples in the `How to optimize controls with time symmetrization
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-with-
    time-symmetrization>`_ user guide.
    """

    name = "symmetrize_pwc"
    args = [forge.arg("pwc", type=Pwc)]
    rtype = Pwc
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        pwc = kwargs.get("pwc")
        check_argument(
            isinstance(pwc, Pwc),
            "The pwc parameter must be a Pwc.",
            {"pwc": pwc},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            pwc,
            "pwc",
        )
        symmetrized_durations = np.concatenate((pwc.durations, pwc.durations[::-1]))
        return Pwc(
            _operation,
            value_shape=value_shape,
            durations=symmetrized_durations,
            batch_shape=batch_shape,
        )


class TimeEvolutionOperatorsPwc(Node):
    """
    Calculates the unitary time-evolution operators for a system defined by a piecewise-constant
    Hamiltonian.

    Parameters
    ----------
    hamiltonian : Pwc
        The control Hamiltonian, or batch of control Hamiltonians.
    sample_times : np.ndarray(1D, real)
        The N times at which you want to sample the unitaries. Must be ordered and contain
        at least one element.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        Tensor of shape [..., N, D, D], representing the unitary time evolution.
        The n-th element (along the -3 dimension) represents the unitary (or batch of unitaries)
        from t = 0 to ``sample_times[n]``.

    See Also
    --------
    state_evolution_pwc : Evolve a quantum state.
    time_evolution_operators_stf : Corresponding operation for `Stf` Hamiltonians.

    Examples
    --------
    Simulate the dynamics of a single qubit, where a constant drive rotates the
    qubit along the x-axis.

    >>> initial_state = np.array([1, 0])
    >>> sigma_x = np.array([[0, 1], [1, 0]])
    >>> duration = np.pi
    >>> hamiltonian = graph.constant_pwc_operator(duration=duration, operator=sigma_x / 2)
    >>> graph.time_evolution_operators_pwc(
    ...     hamiltonian=hamiltonian, sample_times=np.array([duration]), name="unitaries"
    ... )
    <Tensor: name="unitaries", operation_name="time_evolution_operators_pwc", shape=(1, 2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["unitaries"])
    >>> result.output["unitaries"]["value"].dot(initial_state)
    array([[5.0532155e-16+0.j, 0.0000000e+00-1.j]])

    See more examples in the `How to simulate quantum dynamics for noiseless systems using graphs
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-quantum-dynamics-for-
    noiseless-systems-using-graphs>`_ user guide.
    """

    name = "time_evolution_operators_pwc"
    args = [
        forge.arg("hamiltonian", type=Pwc),
        forge.arg("sample_times", type=np.ndarray),
    ]
    rtype = Tensor
    categories = [Category.TIME_EVOLUTION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        hamiltonian = kwargs.get("hamiltonian")
        sample_times = kwargs.get("sample_times")
        check_argument(
            isinstance(hamiltonian, Pwc),
            "The Hamiltonian must be a Pwc.",
            {"hamiltonian": hamiltonian},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            hamiltonian,
            "hamiltonian",
        )
        check_sample_times(sample_times, "sample_times")
        validate_hamiltonian(hamiltonian, "hamiltonian")
        time_count = len(sample_times)
        shape = batch_shape + (time_count,) + value_shape
        return Tensor(_operation, shape=shape)


class SamplePwc(Node):
    r"""
    Samples a Pwc at the given times.

    Parameters
    ----------
    pwc : Pwc
        The Pwc to sample.
    sample_times : np.ndarray(1D, real)
        The times at which you want to sample the Pwc. Must be ordered, contain
        at least one element, and lie between 0 and the duration of the Pwc.
        For a sample time :math:`t` the returned value
        lies in the half open interval :math:`t_{j-1} < t \leq t_j`, where
        :math:`t_j` indicates the boundary of a segment.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The values of the Pwc at the given times.

    See Also
    --------
    sample_stf : Sample an `Stf` at given times.
    """

    name = "sample_pwc"
    args = [
        forge.arg("pwc", type=Pwc),
        forge.arg("sample_times", type=np.ndarray),
    ]
    rtype = Tensor
    categories = [Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        pwc = kwargs.get("pwc")
        check_argument(isinstance(pwc, Pwc), "The pwc must be a Pwc.", {"pwc": pwc})
        batch_shape, value_shape = validate_batch_and_value_shapes(pwc, "pwc")
        sample_times = kwargs.get("sample_times")
        check_sample_times(sample_times, "sample_times")
        check_argument(
            sample_times[0] >= 0,
            "The first sample time can't be smaller than zero.",
            {"sample_times": sample_times},
        )
        check_argument(
            sample_times[-1] <= np.sum(pwc.durations),
            "The last sample time can't be larger than the duration of the Pwc.",
            {"sample_times": sample_times},
            extras={"Pwc durations": pwc.durations},
        )
        time_count = len(sample_times)
        shape = batch_shape + (time_count,) + value_shape
        return Tensor(_operation, shape=shape)
