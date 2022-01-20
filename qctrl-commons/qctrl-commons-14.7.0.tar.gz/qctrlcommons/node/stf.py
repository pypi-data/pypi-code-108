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
Module for all the node related to stf.
"""
from typing import (
    List,
    Optional,
    Union,
)

import forge
import numpy as np

from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    ConvolutionKernel,
    Pwc,
    Stf,
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
    check_operator,
    check_sample_times,
)


class StfOperator(Node):
    r"""
    Creates a constant operator multiplied by a sampleable signal.

    Parameters
    ----------
    signal : Stf
        A sampleable function representing the signal :math:`a(t)`
        or a batch of sampleable functions.
    operator : np.ndarray or Tensor
        The operator :math:`A`. It must have two equal dimensions.

    Returns
    -------
    Stf
        The sampleable operator :math:`a(t)A` (or batch of sampleable operators, if
        you provide a batch of signals).

    See Also
    --------
    constant_stf_operator : Create a constant `Stf` operator.
    pwc_operator : Corresponding operation for `Pwc`\s.
    stf_sum : Sum multiple `Stf`\s.
    """

    name = "stf_operator"
    args = [
        forge.arg("signal", type=Stf),
        forge.arg("operator", type=Union[np.ndarray, Tensor]),
    ]
    kwargs = {}  # Stfs don't accept name as an argument.
    rtype = Stf
    categories = [Category.BUILDING_SMOOTH_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        signal = kwargs.get("signal")
        operator = kwargs.get("operator")
        check_argument(
            isinstance(signal, Stf),
            "The signal must be an Stf.",
            {"signal": signal},
        )
        batch_shape, _ = validate_batch_and_value_shapes(signal, "signal")
        value_shape = validate_shape(operator, "operator")
        check_operator(operator, "operator")
        check_argument(
            len(value_shape) == 2,
            "The operator must be a matrix, not a batch.",
            {"operator": operator},
            extras={"operator.shape": value_shape},
        )
        return Stf(
            _operation,
            value_shape=value_shape,
            batch_shape=batch_shape,
        )


class ConstantStfOperator(Node):
    r"""
    Creates a constant operator.

    Parameters
    ----------
    operator : np.ndarray or Tensor
        The operator :math:`A`, or a batch of operators. It must have at
        least two dimensions, and its last two dimensions must be equal.

    Returns
    -------
    Stf(3D)
        The operator :math:`t\mapsto A` (or batch of
        operators, if you provide a batch of operators).

    See Also
    --------
    constant_pwc_operator : Corresponding operation for `Pwc`\s.
    constant_stf : Create a batch of constant `Stf`\s.
    stf_operator : Create an `Stf` operator.
    """

    name = "constant_stf_operator"
    args = [forge.arg("operator", type=Union[np.ndarray, Tensor])]
    kwargs = {}  # Stfs don't accept name as an argument.
    rtype = Stf
    categories = [Category.BUILDING_SMOOTH_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operator = kwargs.get("operator")
        shape = validate_shape(operator, "operator")
        check_operator(operator, "operator")
        return Stf(
            _operation,
            value_shape=shape[-2:],
            batch_shape=shape[:-2],
        )


class ConstantStf(Node):
    r"""
    Create a constant sampleable tensor-valued function of time.

    Parameters
    ----------
    constant : number or np.ndarray or Tensor
        The constant value :math:`c` of the function.
        To create a batch of :math:`B_1 \times \ldots \times B_n` constant
        functions of shape :math:`D_1 \times \ldots \times D_m`, provide this `constant`
        parameter as an object of shape
        :math:`B_1\times\ldots\times B_n\times D_1\times\ldots\times D_m`.
    batch_dimension_count : int, optional
        The number of batch dimensions, :math:`n`, in `constant`.
        If provided, the first :math:`n` dimensions of `constant` are considered batch dimensions.
        Defaults to 0, which corresponds to no batch.

    Returns
    -------
    Stf
       An Stf representing the constant function :math:`f(t) = c` for all time
       :math:`t` (or a batch of functions, if you provide `batch_dimension_count`).

    See Also
    --------
    constant_pwc : Corresponding operation for `Pwc`\s.
    constant_stf_operator : Create a constant sampleable function from operators.
    identity_stf : Create an `Stf` representing the identity function.
    """

    name = "constant_stf"
    args = [
        forge.arg("constant", type=Union[float, complex, np.ndarray, Tensor]),
        forge.arg("batch_dimension_count", type=int, default=0),
    ]
    kwargs = {}  # Stfs don't accept name as an argument.
    rtype = Stf
    categories = [Category.BUILDING_SMOOTH_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        constant = kwargs.get("constant")
        batch_dimension_count = kwargs.get("batch_dimension_count")

        check_argument_numeric(constant, "constant")
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

        return Stf(
            operation=_operation,
            value_shape=shape[batch_dimension_count:],
            batch_shape=shape[:batch_dimension_count],
        )


class StfSum(Node):
    r"""
    Creates the sum of multiple sampleable functions.

    Parameters
    ----------
    terms : list[Stf]
        The individual sampleable function :math:`\{v_j(t)\}` to sum.

    Returns
    -------
    Stf
        The sampleable function of time :math:`\sum_j v_j(t)`. It has the same
        shape as each of the `terms` that you provide.

    See Also
    --------
    pwc_sum : Corresponding operation for `Pwc`\s.
    stf_operator : Create an `Stf` operator.
    stf_operator_hermitian_part : Hermitian part of an `Stf` operator.
    stf_sum : Sum multiple `Stf`\s.
    """

    name = "stf_sum"
    args = [forge.arg("terms", type=List[Stf])]
    kwargs = {}  # Stfs don't accept name as an argument.
    rtype = Stf
    categories = [Category.BUILDING_SMOOTH_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        terms = kwargs.get("terms")
        check_argument_iterable(terms, "terms")
        check_argument(
            all(isinstance(term, Stf) for term in terms),
            "Each of the terms must be an Stf.",
            {"terms": terms},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            terms[0],
            "terms[0]",
        )
        check_argument(
            all(
                (
                    (value_shape == term.value_shape)
                    and (batch_shape == term.batch_shape)
                )
                for term in terms[1:]
            ),
            "All the terms must have the same shape.",
            {"terms": terms},
        )
        return Stf(
            _operation,
            value_shape=value_shape,
            batch_shape=batch_shape,
        )


class StfOperatorHermitianPart(Node):
    r"""
    Creates the Hermitian part of an operator-valued sampleable function.

    Parameters
    ----------
    operator : Stf
        The operator-valued sampleable function :math:`A(t)`.

    Returns
    -------
    Stf
        The Hermitian part of the Stf operator :math:`\frac{1}{2}(A(t) + A^\dagger(t))`.

    See Also
    --------
    pwc_operator_hermitian_part : Corresponding operation for `Pwc`\s.
    stf_operator : Create an `Stf` operator.

    Examples
    --------
    >>> operator = stf_signal * np.array([[0, 1, 0], [0, 0, np.sqrt(2)], [0, 0, 0]])
    >>> operator
    <Stf: operation_name="multiply", value_shape=(3, 3), batch_shape=()>
    >>> hamiltonian = graph.stf_operator_hermitian_part(operator)

    Refer to the `How to perform model-based optimization with user-defined basis functions
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-perform-model-based-optimization-with-user-defined-basis-functions>`_
    user guide to find the example in context.
    """

    name = "stf_operator_hermitian_part"
    args = [forge.arg("operator", type=Stf)]
    kwargs = {}  # Stfs don't accept name as an argument.
    rtype = Stf
    categories = [Category.BUILDING_SMOOTH_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operator = kwargs.get("operator")
        check_argument(
            isinstance(operator, Stf),
            "The operator must be an Stf.",
            {"operator": operator},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(operator, "operator")
        return Stf(
            _operation,
            value_shape=value_shape,
            batch_shape=batch_shape,
        )


class DiscretizeStf(Node):
    r"""
    Creates a piecewise-constant function by discretizing a sampleable function.

    Use this function to create a piecewise-constant approximation to a sampleable
    function (obtained, for example, by filtering an initial
    piecewise-constant function).

    Parameters
    ----------
    stf : Stf
        The sampleable function :math:`v(t)` to discretize. The values of the
        function can have any shape. You can also provide a batch of
        functions, in which case the discretization is applied to each
        element of the batch.
    duration : float
        The duration :math:`\tau` over which discretization should be
        performed. The resulting piecewise-constant function has this
        duration.
    segment_count : int
        The number of segments :math:`N` in the resulting piecewise-constant
        function.
    sample_count_per_segment : int, optional
        The number of samples :math:`M` of the sampleable function to take when
        calculating the value of each segment in the discretization. Defaults
        to 1.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant function :math:`w(t)` obtained by discretizing
        the sampleable function (or batch of piecewise-constant functions, if
        you provided a batch of sampleable functions).

    Notes
    -----
    The resulting function :math:`w(t)` is piecewise-constant with :math:`N`
    segments, meaning it has segment values :math:`\{w_n\}` such that
    :math:`w(t)=w_n` for :math:`t_{n-1}\leq t\leq t_n`, where :math:`t_n= n \tau/N`.

    Each segment value :math:`w_n` is the average of samples of :math:`v(t)`
    at the midpoints of :math:`M` equally sized subsegments between
    :math:`t_{n-1}` and :math:`t_n`:

    .. math::
        w_n = \frac{1}{M}
        \sum_{m=1}^M v\left(t_{n-1} + \left(m-\tfrac{1}{2}\right) \frac{\tau}{MN} \right).

    See Also
    --------
    convolve_pwc : Create an `Stf` by convolving a `Pwc` with a kernel.
    identity_stf : Create an `Stf` representing the identity function.
    sample_stf : Sample an `Stf` at given times.

    Examples
    --------
    Create discretized Gaussian signal.

    >>> times = graph.identity_stf()
    >>> gaussian_signal = graph.exp(- (times - 5e-6) ** 2 / 2e-6 ** 2) / 2e-6
    >>> discretized_gamma_signal = graph.discretize_stf(
    ...     stf=gaussian_signal, duration=10e-6, segment_count=256, name="gamma"
    ... )
    >>> discretized_gamma_signal
    <Pwc: name="gamma", operation_name="discretize_stf", value_shape=(), batch_shape=()>

    Refer to the `How to create dephasing and amplitude robust single-qubit gates
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-create-dephasing-and-amplitude-robust-single-qubit-gates>`_
    user guide to find the example in context.
    """

    name = "discretize_stf"
    args = [
        forge.arg("stf", type=Stf),
        forge.arg("duration", type=float),
        forge.arg("segment_count", type=int),
        forge.arg("sample_count_per_segment", type=int, default=1),
    ]
    rtype = Pwc
    categories = [Category.FILTERING_AND_DISCRETIZING]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        stf = kwargs.get("stf")
        duration = kwargs.get("duration")
        segment_count = kwargs.get("segment_count")
        batch_shape, value_shape = validate_batch_and_value_shapes(
            stf,
            "stf",
        )
        check_argument_integer(segment_count, "segment_count")
        check_argument(
            segment_count > 0,
            "The number of segments must be greater than zero.",
            {"segment_count": segment_count},
        )
        durations = duration / segment_count * np.ones(segment_count)
        sample_count_per_segment = kwargs.get("sample_count_per_segment")
        check_argument_integer(sample_count_per_segment, "sample_count_per_segment")
        check_argument(
            sample_count_per_segment > 0,
            "The number of samples per segment to take must be greater than zero.",
            {"sample_count_per_segment": sample_count_per_segment},
        )
        return Pwc(
            _operation,
            value_shape=value_shape,
            durations=durations,
            batch_shape=batch_shape,
        )


class TimeEvolutionOperatorsStf(Node):
    """
    Calculates the time-evolution operators for a system defined by an STF Hamiltonian by using a
    4th order Runge–Kutta method.

    Parameters
    ----------
    hamiltonian : Stf
        The control Hamiltonian, or batch of control Hamiltonians.
    sample_times : np.ndarray(1D, real)
        The N times at which you want to sample the unitaries. Must be ordered and contain
        at least one element. If you don't provide `evolution_times`, `sample_times` must
        start with 0.
    evolution_times : np.ndarray(1D, real), optional
        The times at which the Hamiltonian should be sampled for the Runge–Kutta integration.
        If you provide it, must start with 0 and be ordered.
        If you don't provide it, the `sample_times` are used for the integration.
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
    time_evolution_operators_pwc : Corresponding operation for `Pwc` Hamiltonians.

    Examples
    --------
    Simulate the dynamics of a qubit, where a simple Gaussian drive rotate the qubit
    along the x-axis.

    >>> duration = np.pi
    >>> initial_state = np.array([1, 0])
    >>> sigma_x = np.array([[0, 1], [1, 0]])
    >>> time = graph.identity_stf()
    >>> gaussian_drive = graph.exp(-(time ** 2))
    >>> hamiltonian = gaussian_drive * sigma_x * np.sqrt(np.pi) / 2
    >>> graph.time_evolution_operators_stf(
    ...     hamiltonian=hamiltonian,
    ...     sample_times=np.array([duration]),
    ...     evolution_times=np.linspace(0, duration, 200),
    ...     name="unitaries",
    ... )
    <Tensor: name="unitaries", operation_name="time_evolution_operators_stf", shape=(1, 2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["unitaries"])
    >>> result.output["unitaries"]["value"].dot(initial_state)
    array([[0.70711169 + 0.0j, 0.0 - 0.70710187j]])
    """

    name = "time_evolution_operators_stf"
    args = [
        forge.arg("hamiltonian", type=Stf),
        forge.arg("sample_times", type=np.ndarray),
        forge.arg("evolution_times", type=Optional[np.ndarray], default=None),
    ]
    rtype = Tensor
    categories = [Category.TIME_EVOLUTION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        hamiltonian = kwargs.get("hamiltonian")
        sample_times = kwargs.get("sample_times")
        evolution_times = kwargs.get("evolution_times")
        check_argument(
            isinstance(hamiltonian, Stf),
            "The Hamiltonian must be an Stf.",
            {"hamiltonian": hamiltonian},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            hamiltonian,
            "hamiltonian",
        )
        check_sample_times(sample_times, "sample_times")
        validate_hamiltonian(hamiltonian, "hamiltonian")
        time_count = len(sample_times)
        if evolution_times is not None:
            check_sample_times(evolution_times, "evolution_times")
            check_argument(
                evolution_times[0] == 0,
                "The first of the evolution times must be zero.",
                {"evolution_times": evolution_times},
            )
        else:
            check_argument(
                sample_times[0] == 0,
                "If you don't provide evolution times, the first of the sample"
                " times must be zero.",
                {"sample_times": sample_times},
            )
        shape = batch_shape + (time_count,) + value_shape
        return Tensor(_operation, shape=shape)


class ConvolvePwc(Node):
    r"""
    Creates the convolution of a piecewise-constant function with a kernel.

    Parameters
    ----------
    pwc : Pwc
        The piecewise-constant function :math:`\alpha(t)` to convolve. You
        can provide a batch of functions, in which case the convolution is
        applied to each element of the batch.
    kernel : ConvolutionKernel
        The node representing the kernel :math:`K(t)`.

    Returns
    -------
    Stf
        The sampleable function representing the signal :math:`(\alpha * K)(t)`
        (or batch of signals, if you provide a batch of functions).

    Notes
    -----
    The convolution is

    .. math::
        (\alpha * K)(t) \equiv
        \int_{-\infty}^\infty \alpha(\tau) K(t-\tau) d\tau.

    Convolution in the time domain is equivalent to multiplication in the
    frequency domain, so this function can be viewed as applying a linear
    time-invariant filter (specified via its time domain kernel :math:`K(t)`)
    to :math:`\alpha(t)`.

    See Also
    --------
    discretize_stf : Discretize an `Stf` into a `Pwc`.
    gaussian_convolution_kernel : Create a convolution kernel representing a normalized Gaussian.
    pwc : Create piecewise-constant functions.
    sample_stf : Sample an `Stf` at given times.
    sinc_convolution_kernel : Create a convolution kernel representing the sinc function.

    Examples
    --------
    Filter a piecewise-constant signal using a Gaussian convolution kernel.

    >>> gaussian_kernel = graph.gaussian_convolution_kernel(std=1.0, offset=3.0)
    >>> gaussian_kernel
    <ConvolutionKernel: operation_name="gaussian_convolution_kernel">
    >>> pwc_signal
    <Pwc: name="alpha", operation_name="pwc_signal", value_shape=(), batch_shape=()>
    >>> filtered_signal = graph.convolve_pwc(pwc=pwc_signal, kernel=gaussian_kernel)
    >>> filtered_signal
    <Stf: operation_name="convolve_pwc", value_shape=(), batch_shape=()>

    Refer to the `How to add smoothing and band-limits to optimized controls
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-add-smoothing-and-band-limits-to-optimized-controls>`_
    user guide to find the example in context.
    """

    name = "convolve_pwc"
    args = [
        forge.arg("pwc", type=Pwc),
        forge.arg("kernel", type=ConvolutionKernel),
    ]
    kwargs = {}  # Stfs don't accept name as an argument.
    rtype = Stf
    categories = [Category.FILTERING_AND_DISCRETIZING]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        pwc = kwargs.get("pwc")
        batch_shape, value_shape = validate_batch_and_value_shapes(pwc, "pwc")
        return Stf(
            _operation,
            value_shape=value_shape,
            batch_shape=batch_shape,
        )


class SincConvolutionKernel(Node):
    r"""
    Creates a convolution kernel representing the sinc function.

    Use this kernel to eliminate frequencies above a certain cut-off.

    Parameters
    ----------
    cut_off_frequency : float or Tensor
        Upper limit :math:`\omega_c` of the range of frequencies that you want
        to preserve. The filter eliminates components of the signal that have
        higher frequencies.

    Returns
    -------
    ConvolutionKernel
        A node representing the sinc function to use in a convolution.

    Notes
    -----
    The range of frequencies that this kernel lets pass is
    :math:`[-\omega_c, \omega_c]`. After a Fourier transform to convert from
    frequency domain to time domain, this becomes:

    .. math::
        \frac{1}{2\pi} \int_{-\omega_c}^{\omega_c} \mathrm{d}\omega
        e^{i \omega t} = \frac{\sin(\omega_c t)}{\pi t}.

    The function on the right side of the equation is the sinc function.
    Its integral is the sine integral function (Si).

    See Also
    --------
    convolve_pwc : Create an `Stf` by convolving a `Pwc` with a kernel.
    gaussian_convolution_kernel : Create a convolution kernel representing a normalized Gaussian.

    Examples
    --------
    Filter a signal by convolving it with a sinc kernel.

    >>> sinc_kernel = graph.sinc_convolution_kernel(cut_off_frequency=300e6)
    >>> sinc_kernel
    <ConvolutionKernel: operation_name="sinc_convolution_kernel">
    >>> pwc_signal
    <Pwc: name="pwc_signal_#1", operation_name="pwc_signal", value_shape=(), batch_shape=()>
    >>> filtered_signal = graph.convolve_pwc(pwc=pwc_signal, kernel=sinc_kernel)
    >>> filtered_signal
    <Stf: operation_name="convolve_pwc", value_shape=(), batch_shape=()>

    Refer to the `How to create leakage-robust single-qubit gates
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-create-leakage-robust-single-qubit-gates>`_
    user guide to find the example in context.
    """

    name = "sinc_convolution_kernel"
    args = [
        forge.arg("cut_off_frequency", type=Union[float, Tensor]),
    ]
    kwargs = {}  # ConvolutionKernels don't accept name as an argument.
    rtype = ConvolutionKernel
    categories = [Category.FILTERING_AND_DISCRETIZING]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return ConvolutionKernel(_operation)


class GaussianConvolutionKernel(Node):
    r"""
    Creates a convolution kernel representing a normalized Gaussian.

    Use this kernel to allow frequencies in the range roughly determined by
    its width, and progressively suppress components outside that range.

    Parameters
    ----------
    std : float or Tensor
        Standard deviation :math:`\sigma` of the Gaussian in the time domain.
        The standard deviation in the frequency domain is its inverse, so that
        a high value of this parameter lets fewer frequencies pass.
    offset : float or Tensor, optional
        Center :math:`\mu` of the Gaussian distribution in the time domain.
        Use this to offset the signal in time. Defaults to 0.

    Returns
    -------
    ConvolutionKernel
        A node representing a Gaussian function to use in a convolution.

    Notes
    -----
    The Gaussian that this node represents is normalized in the time domain:

    .. math::
        \frac{e^{-(t-\mu)^2/(2\sigma^2)}}{\sqrt{2\pi\sigma^2}}.

    In the frequency domain, this Gaussian has standard deviation
    :math:`\omega_c= \sigma^{-1}`. The filter it represents therefore
    passes frequencies roughly in the range :math:`[-\omega_c, \omega_c]`.

    See Also
    --------
    convolve_pwc : Create an `Stf` by convolving a `Pwc` with a kernel.
    sinc_convolution_kernel : Create a convolution kernel representing the sinc function.

    Examples
    --------
    Filter a signal by convolving it with a Gaussian kernel.

    >>> gaussian_kernel = graph.gaussian_convolution_kernel(std=1.0, offset=3.0)
    >>> gaussian_kernel
    <ConvolutionKernel: operation_name="gaussian_convolution_kernel">
    >>> signal
    <Pwc: name="alpha", operation_name="pwc_signal", value_shape=(), batch_shape=()>
    >>> filtered_signal = graph.convolve_pwc(pwc=signal, kernel=gaussian_kernel)
    >>> filtered_signal
    <Stf: operation_name="convolve_pwc", value_shape=(), batch_shape=()>

    Refer to the `How to characterize the bandwidth of a transmission line using a qubit as a probe
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-characterize-the-bandwidth-of-a-transmission-line-using-a-qubit-as-a-probe>`_
    user guide to find the example in context.
    """

    name = "gaussian_convolution_kernel"
    args = [
        forge.arg("std", type=Union[float, Tensor]),
        forge.arg("offset", type=Optional[Union[float, Tensor]], default=0),
    ]
    kwargs = {}  # ConvolutionKernels don't accept name as an argument.
    rtype = ConvolutionKernel
    categories = [Category.FILTERING_AND_DISCRETIZING]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return ConvolutionKernel(_operation)


class SampleStf(Node):
    """
    Samples an Stf at the given times.

    Parameters
    ----------
    stf : Stf
        The Stf to sample.
    sample_times : np.ndarray(1D, real)
        The times at which you want to sample the Stf. Must be ordered and contain
        at least one element.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The values of the Stf at the given times.

    See Also
    --------
    constant_stf_operator : Create a constant `Stf` operator.
    discretize_stf : Discretize an `Stf` into a `Pwc`.
    identity_stf : Create an `Stf` representing the identity function.
    sample_pwc : Sample a `Pwc` at given times.
    """

    name = "sample_stf"
    args = [
        forge.arg("stf", type=Stf),
        forge.arg("sample_times", type=np.ndarray),
    ]
    rtype = Tensor
    categories = [Category.BUILDING_SMOOTH_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        stf = kwargs.get("stf")
        check_argument(isinstance(stf, Stf), "The stf must be an Stf.", {"stf": stf})
        batch_shape, value_shape = validate_batch_and_value_shapes(stf, "stf")
        sample_times = kwargs.get("sample_times")
        check_sample_times(sample_times, "sample_times")
        time_count = len(sample_times)
        shape = batch_shape + (time_count,) + value_shape
        return Tensor(_operation, shape=shape)


class IdentityStf(Node):
    r"""
    Creates an Stf representing the identity function, f(t) = t.

    Returns
    -------
    Stf
        An Stf representing the identity function.

    See Also
    --------
    constant_stf: Create a batch of constant `Stf`\s.
    discretize_stf : Discretize an `Stf` into a `Pwc`.
    sample_stf : Sample an `Stf` at given times.

    Examples
    --------
    Create Gaussian pulse.

    >>> time = graph.identity_stf()
    >>> time
    <Stf: operation_name="identity_stf", value_shape=(), batch_shape=()>
    >>> gaussian = graph.exp(- time ** 2)
    >>> gaussian
    <Stf: operation_name="exp", value_shape=(), batch_shape=()>

    Refer to the `How to perform model-based optimization with user-defined basis functions
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-perform-model-based-optimization-with-user-defined-basis-functions>`_
    user guide to find the example in context.
    """

    name = "identity_stf"
    args = []
    kwargs = {}  # Stfs don't accept name as an argument.
    rtype = Stf
    categories = [Category.BUILDING_SMOOTH_HAMILTONIANS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return Stf(
            _operation,
            value_shape=(),
            batch_shape=(),
        )
