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
"""Utilities for commons nodes."""
from typing import Union

import numpy as np

from qctrlcommons.exceptions import QctrlException
from qctrlcommons.node.node_data import (
    Pwc,
    Stf,
    Tensor,
)
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_integer,
    check_argument_numeric,
    check_argument_operator,
)

NumericOrFunction = Union[float, complex, np.ndarray, Tensor, Pwc, Stf]


def is_broadcastable(shape_a, shape_b) -> bool:
    """
    Checks if the shapes of two objects are broadcastable.

    Two shapes are broadcastable if, for each dimension starting from the end,
    they have the same size value, or if one of them has size 1.

    The function returns True even if some matching "dimensions" are negative.
    This can be used to compare shapes of Stf/Pwc objects by setting the size
    of their time_dimension to -1.

    Parameters
    ----------
    shape_a : tuple[int]
        Shape of one of the objects.
    shape_b : tuple[int]
        Shape of the other object.

    Returns
    -------
    bool
        True if shapes of two objects are broadcastable otherwise False
    """
    return all(
        ((dimension_a == dimension_b) or (dimension_a == 1) or (dimension_b == 1))
        for (dimension_a, dimension_b) in zip(shape_a[::-1], shape_b[::-1])
    )


def validate_broadcasted_shape(x_shape, y_shape, x_name, y_name):
    """
    Gets the resulting broadcasted shape for two input shapes.

    Parameters
    ----------
    x_shape : tuple[int]
        One of the shapes to be broadcasted.
    y_shape : tuple[int]
        The other of the shapes to be broadcasted.
    x_name : str
        The name of the variable whose shape is `x_shape`, used for the error
        message in case the shapes aren't broadcastable.
    y_name : str
        The name of the variable whose shape is `y_shape`, used for the error
        message in case the shapes aren't broadcastable.

    Returns
    -------
    tuple[int]
        The shape of the broadcasted array.

    Raises
    ------
    QctrlException
        if the two shapes aren't broadcastable.
    """

    if not is_broadcastable(x_shape, y_shape):
        raise QctrlException(
            f"The shapes {x_shape} of {x_name} and {y_shape} of {y_name}"
            " must be broadcastable."
        )

    shape_length = max(len(x_shape), len(y_shape))

    long_x_shape = (1,) * (shape_length - len(x_shape)) + tuple(x_shape)
    long_y_shape = (1,) * (shape_length - len(y_shape)) + tuple(y_shape)

    shape = (
        long_x_shape[index] if long_x_shape[index] != 1 else long_y_shape[index]
        for index in range(shape_length)
    )

    return tuple(shape)


def validate_function_output_shapes(
    x_batch_shape,
    x_value_shape,
    y_batch_shape,
    y_value_shape,
    validate_value_shape,
):
    """
    Gets the output batch and value shape for two input shapes of Pwcs/Stfs.
    The names of the variables are assumed to be x and y when reporting errors.

    Parameters
    ----------
    x_batch_shape : tuple[int]
        The batch shape of the first object.
    x_value_shape : tuple[int]
        The value shape of the first object.
    y_batch_shape : tuple[int]
        The batch shape of the second object.
    y_value_shape : tuple[int]
        The value shape of the second object.
    validate_value_shape : Callable[[tuple, tuple, str, str], tuple]
        Function that takes the value shapes of two Tensors, Pwcs,
        or Stfs (as well as their names), and returns the expected values
        shape of the output Tensor, Pwc, or Stf. The function
        shouldn't assume that the shapes are compatible, and raise an
        exception if they aren't. The names provided should be used to
        generate the error message.

    Returns
    -------
    tuple[int], tuple[int]
        The batch and value shapes of the output Pwc/Stf.

    Raises
    ------
    QctrlException
        if the two objects aren't compatible.
    """
    batch_shape = validate_broadcasted_shape(
        x_batch_shape, y_batch_shape, "x (batch)", "y (batch)"
    )
    value_shape = validate_value_shape(x_value_shape, y_value_shape, "x", "y")

    return batch_shape, value_shape


def validate_tensor_and_function_output_shapes(
    t_shape,
    f_batch_shape,
    f_value_shape,
    t_name,
    f_name,
    validate_value_shape,
    tensor_first=True,
):
    """
    Gets the output batch and value shape for an input tensor and an input Pwc/Stf.

    Parameters
    ----------
    t_shape : tuple[int]
        The shape of the tensor.
    f_batch_shape : tuple[int]
        The batch shape of the Pwc/Stf.
    f_value_shape : tuple[int]
        The value shape of the Pwc/Stf.
    t_name : str
        The name of the tensor variable, used for the error message in case the shapes aren't
        compatible.
    f_name : str
        The name of the function variable, used for the error message in case the shapes aren't
        compatible.
    validate_value_shape : Callable[[tuple, tuple, str, str], tuple]
        Function that takes the value shapes of two Tensors, Pwcs,
        or Stfs (as well as their names), and returns the expected values
        shape of the output Tensor, Pwc, or Stf. The function
        shouldn't assume that the shapes are compatible, and raise an
        exception if they aren't. The names provided should be used to
        generate the error message.
    tensor_first : bool, optional
        Whether the Tensor is the leftmost parameter. Defaults to True.

    Returns
    -------
    tuple[int], tuple[int]
        The batch and value shapes of the output Pwc/Stf.

    Raises
    ------
    QctrlException
        if the two objects aren't compatible.
    """
    if tensor_first:
        value_shape = validate_value_shape(t_shape, f_value_shape, t_name, f_name)
    else:
        value_shape = validate_value_shape(f_value_shape, t_shape, f_name, t_name)

    return f_batch_shape, value_shape


def validate_shape(tensor_like, tensor_like_name):
    """
    Returns the shape of a scalar, np.ndarray, scipy.sparse.coo_matrix, or Tensor node.

    Parameters
    ----------
    tensor_like : number or np.ndarray or scipy.sparse.coo_matrix or Tensor
        The object whose shape you want to obtain.
    tensor_like_name : str
        The name of the `tensor_like`, used for error message in case the
        input object is not valid.

    Returns
    -------
    tuple[int]
        The tuple with the size of each dimension of `tensor_like`.

    Raises
    ------
    QctrlException
        if the input is neither a scalar, a NumPy array, nor a Tensor.
    """

    if hasattr(tensor_like, "shape"):
        return tuple(tensor_like.shape)

    if np.isscalar(tensor_like):
        return ()

    raise QctrlException(f"The type of {tensor_like_name}={tensor_like} is not valid.")


def validate_batch_and_value_shapes(tensor, tensor_name):
    """
    Returns the batch and value shapes of Pwc or Stf.

    Parameters
    ----------
    tensor : Pwc or Stf
        The NodeData for the Pwc or Stf whose batch and value shapes
        you want to obtain.
    tensor_name : str
        The name of the Pwc or Stf, used for the error message in
        case `tensor` doesn't have a value shape.

    Returns
    -------
    tuple[tuple[int]]
        A tuple with a tuple that represents the batch shape, and a tuple
        that represents the value shape, in this sequence.

    Raises
    ------
    QctrlException
        if the input is neither a scalar, a Pwc, nor an Stf
    """

    if hasattr(tensor, "value_shape") and hasattr(tensor, "batch_shape"):
        return tuple(tensor.batch_shape), tuple(tensor.value_shape)

    if hasattr(tensor, "value_shape"):
        return (), tuple(tensor.value_shape)

    raise QctrlException(f"The type of {tensor_name}={tensor} must be Pwc or Stf.")


def validate_hamiltonian(hamiltonian, hamiltonian_name):
    """
    Checks whether a Pwc, Stf or SparsePwc contains values that are Hamiltonians.

    Hamiltonians are two-dimensional and square.

    Parameters
    ----------
    hamiltonian : Pwc or Stf or SparsePwc
        The Hamiltonian to be tested.
    hamiltonian_name : str
        The name of the Hamiltonian, used in the error message.
    """
    value_shape = getattr(hamiltonian, "value_shape", ())

    check_argument(
        len(value_shape) == 2,
        "The shape of the Hamiltonian must have 2 dimensions.",
        {hamiltonian_name: hamiltonian},
        extras={f"{hamiltonian_name}.value_shape": value_shape},
    )
    check_argument(
        value_shape[-1] == value_shape[-2],
        "The dimensions of the Hamiltonian must have equal sizes.",
        {hamiltonian_name: hamiltonian},
        extras={f"{hamiltonian_name}.value_shape": value_shape},
    )


def validate_ms_shapes(ion_count, ld_values, ld_name, rd_values, rd_name):
    """
    Checks if the shapes of the Mølmer–Sørensen parameters are correct.

    The correct shapes for the input parameters of Mølmer–Sørensen gate are
    ``(3, ion_count, ion_count)`` for the Lamb–Dicke parameters and
    ``(3, ion_count)`` for the relative detunings.

    Parameters
    ----------
    ion_count : int
        The number of ions in the chain.
    ld_values : np.ndarray
        The input values of the Lamb–Dicke parameters.
    ld_name : str
        The name of the argument that holds the Lamb–Dicke parameters.
    rd_values : np.ndarray
        The input values of the relative detunings.
    rd_name : str
        The name of the argument that holds the relative detunings.
    """
    check_argument_numeric(ld_values, ld_name)
    check_argument_numeric(rd_values, rd_name)

    ld_shape = validate_shape(ld_values, ld_name)
    rd_shape = validate_shape(rd_values, rd_name)

    check_argument(
        ld_shape == (3, ion_count, ion_count),
        "The Lamb–Dicke parameters must have shape (3, ion_count, ion_count).",
        {ld_name: ld_values},
        extras={"ion_count": ion_count, f"{ld_name}.shape": ld_shape},
    )
    check_argument(
        rd_shape == (3, ion_count),
        "The relative detunings must have shape (3, ion_count).",
        {rd_name: rd_values},
        extras={"ion_count": ion_count, f"{rd_name}.shape": rd_shape},
    )


def check_density_matrix_shape(density_matrix, name):
    """
    Checks the shape of the input density matrix.

    Parameters
    ----------
    density_matrix : Tensor or np.ndarray
        A density matrix.
    name : str
        Name of the density matrix.
    """
    check_argument_numeric(density_matrix, name)
    density_matrix_shape = validate_shape(density_matrix, name)
    check_argument(
        len(density_matrix_shape) in [2, 3],
        f"The {name} must be 2D or 3D with the first axis as the batch dimension.",
        {name: density_matrix},
        extras={"density matrix shape": density_matrix_shape},
    )
    check_argument(
        density_matrix_shape[-1] == density_matrix_shape[-2],
        f"The {name} must be a square in the last two dimensions.",
        {name: density_matrix},
        extras={"density matrix shape": density_matrix_shape},
    )


def check_oqs_hamiltonian(hamiltonian, initial_density_matrix):
    """
    Check whether open quantum system (OQS) Hamiltonian is valid.

    Parameters
    ----------
    hamiltonian : Pwc or SparsePwc
        Effective system Hamiltonian.
    initial_density_matrix : np.ndarray or Tensor
        Initial density matrix of the system.
    """
    system_dimension = initial_density_matrix.shape[-1]
    check_argument_integer(system_dimension, "system dimension")
    check_argument(
        hamiltonian.value_shape == (system_dimension, system_dimension),
        "The dimension of the Hamiltonian must be compatible with the dimension "
        "of the initial density matrix.",
        {
            "hamiltonian": hamiltonian,
            "initial_density_matrix": initial_density_matrix,
        },
        extras={
            "hamiltonian dimension": hamiltonian.value_shape,
            "initial density matrix dimension": initial_density_matrix.shape,
        },
    )


def check_lindblad_terms(
    lindblad_terms, hilbert_space_object, hilbert_space_object_name
):
    """
    Check whether Lindblad terms are valid.

    Parameters
    ----------
    lindblad_terms : list[tuple[float, np.ndarray or coo_matrix]]
        Effective system Hamiltonian.
    hilbert_space_object : np.ndarray or Tensor or scipy.sparse.spmatrix
        Object whose last element of its shape is the system's Hilbert space dimension.
    hilbert_space_object_name : str
        The name of the `hilbert_space_object`, used in an error message in case the
        inputs dimensions don't match.
    """

    system_dimension = hilbert_space_object.shape[-1]

    for index, (rate, operator) in enumerate(lindblad_terms):
        check_argument(
            rate > 0,
            ("The decay rate must be positive."),
            {"lindblad_terms": lindblad_terms},
        )
        check_argument_numeric(operator, f"lindblad_terms[{index}][1]")
        _ = validate_shape(operator, f"lindblad_terms[{index}][1]")
        check_argument_operator(operator, f"lindblad_terms[{index}][1]")
        check_argument(
            operator.shape[0] == system_dimension,
            "The dimension of Lindblad operator must be compatible with the dimension "
            f"of {hilbert_space_object_name}.",
            {"lindblad_terms": lindblad_terms},
            extras={
                "Lindblad operator shape": operator.shape,
                f"{hilbert_space_object_name} shape": hilbert_space_object.shape,
            },
        )


def validate_inputs_real_fourier_signal(
    fixed_frequencies, optimizable_frequency_count, randomized_frequency_count
):
    """
    Check if the inputs of real_fourier_pwc/stf_signal function are valid.
    """
    check_argument(
        (fixed_frequencies is not None)
        + (optimizable_frequency_count is not None)
        + (randomized_frequency_count is not None)
        == 1,
        "Exactly one of `fixed_frequencies`, `optimizable_frequency_count` and "
        "`randomized_frequency_count` must be provided.",
        {
            "fixed_frequencies": fixed_frequencies,
            "optimizable_frequency_count": optimizable_frequency_count,
            "randomized_frequency_count": randomized_frequency_count,
        },
    )
    if optimizable_frequency_count is not None:
        check_argument_integer(
            optimizable_frequency_count, "optimizable_frequency_count"
        )
        check_argument(
            optimizable_frequency_count > 0,
            "The number of optimizable frequencies (if provided) must be greater than zero.",
            {"optimizable_frequency_count": optimizable_frequency_count},
        )
    if randomized_frequency_count is not None:
        check_argument_integer(randomized_frequency_count, "randomized_frequency_count")
        check_argument(
            randomized_frequency_count > 0,
            "The number of randomized frequencies (if provided) must be greater than zero.",
            {"randomized_frequency_count": randomized_frequency_count},
        )
