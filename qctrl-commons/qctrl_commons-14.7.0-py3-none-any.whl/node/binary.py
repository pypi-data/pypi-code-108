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

# pylint: disable=too-many-lines
"""Module for binary operation nodes."""

from typing import Union

import forge
import numpy as np

from qctrlcommons.exceptions import QctrlException
from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    Pwc,
    Stf,
    Tensor,
)
from qctrlcommons.node.utils import (
    NumericOrFunction,
    is_broadcastable,
    validate_batch_and_value_shapes,
    validate_broadcasted_shape,
    validate_function_output_shapes,
    validate_shape,
    validate_tensor_and_function_output_shapes,
)
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_numeric,
)


def _create_flexible_binary_node_data(
    _operation,
    op_name,
    x,
    y,
    name,
    validate_value_shape=validate_broadcasted_shape,
):
    """
    Common implementation of `create_node_data` for nodes acting on Tensors, Pwcs, and Stfs
    implementing binary functions.

    Parameters
    ----------
    _operation : Operation
        The operation to implement.
    op_name : str
        The name of the operation.
    x : number or np.ndarray or Tensor or Pwc or Stf
        The left operand.
    y : number or np.ndarray or Tensor or Pwc or Stf
        The right operand.
    name : str
        The name of the node.
    validate_value_shape : Callable[[tuple, tuple, str, str], tuple], optional
        Function that takes the value shapes of two Tensors, Pwcs,
        or Stfs (as well as their names), and returns the expected values
        shape of the output Tensor, Pwc, or Stf. The function
        shouldn't assume that the shapes are compatible, and raise an
        exception if they aren't. The names provided should be used to
        generate the error message.

    Returns
    -------
    Tensor or Pwc or Stf
        The operation acting on the object.
    """
    # operation(Pwc, Stf) or operation(Stf, Pwc)
    check_argument(
        not (isinstance(x, Pwc) and isinstance(y, Stf))
        and not (isinstance(x, Stf) and isinstance(y, Pwc)),
        f"You can't apply the {op_name} operation between a Pwc and an Stf.",
        {"x": x, "y": y},
    )

    # operation(Stf, Stf)
    if isinstance(x, Stf) and isinstance(y, Stf):

        check_argument(
            name is None, "You can't assign a name to an Stf node.", {"name": name}
        )

        x_batch_shape, x_value_shape = validate_batch_and_value_shapes(x, "x")
        y_batch_shape, y_value_shape = validate_batch_and_value_shapes(y, "y")

        batch_shape, value_shape = validate_function_output_shapes(
            x_batch_shape,
            x_value_shape,
            y_batch_shape,
            y_value_shape,
            validate_value_shape=validate_value_shape,
        )
        return Stf(_operation, value_shape=value_shape, batch_shape=batch_shape)

    # operation(Pwc, Pwc)
    if isinstance(x, Pwc) and isinstance(y, Pwc):

        check_argument(
            np.isclose(np.sum(x.durations), np.sum(y.durations)),
            "Both Pwc terms must have the same total duration.",
            {"x": x, "y": y},
        )

        x_batch_shape, x_value_shape = validate_batch_and_value_shapes(x, "x")
        y_batch_shape, y_value_shape = validate_batch_and_value_shapes(y, "y")

        batch_shape, value_shape = validate_function_output_shapes(
            x_batch_shape,
            x_value_shape,
            y_batch_shape,
            y_value_shape,
            validate_value_shape=validate_value_shape,
        )

        upsampled_durations = np.diff(
            np.insert(
                np.unique(
                    np.concatenate([np.cumsum(x.durations), np.cumsum(y.durations)])
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

    # operation(Stf, Tensor) or operation(Tensor, Stf)
    if isinstance(x, Stf) or isinstance(y, Stf):

        check_argument(
            name is None, "You can't assign a name to an Stf node.", {"name": name}
        )

        if isinstance(x, Stf):
            f_batch_shape, f_value_shape = validate_batch_and_value_shapes(x, "x")
            f_name = "x"
            check_argument_numeric(y, "y")
            t_shape = validate_shape(y, "y")
            t_name = "y"
            tensor_first = False
        else:
            check_argument_numeric(x, "x")
            t_shape = validate_shape(x, "x")
            t_name = "x"
            f_batch_shape, f_value_shape = validate_batch_and_value_shapes(y, "y")
            f_name = "y"
            tensor_first = True

        batch_shape, value_shape = validate_tensor_and_function_output_shapes(
            t_shape,
            f_batch_shape,
            f_value_shape,
            t_name,
            f_name,
            validate_value_shape=validate_value_shape,
            tensor_first=tensor_first,
        )

        return Stf(_operation, value_shape=value_shape, batch_shape=batch_shape)

    # operation(Pwc, Tensor) or operation(Tensor, Pwc)
    if isinstance(x, Pwc) or isinstance(y, Pwc):

        if isinstance(x, Pwc):
            f_batch_shape, f_value_shape = validate_batch_and_value_shapes(x, "x")
            f_name = "x"
            durations = x.durations
            check_argument_numeric(y, "y")
            t_shape = validate_shape(y, "y")
            t_name = "y"
            tensor_first = False
        else:
            check_argument_numeric(x, "x")
            t_shape = validate_shape(x, "x")
            t_name = "x"
            f_batch_shape, f_value_shape = validate_batch_and_value_shapes(y, "y")
            f_name = "y"
            durations = y.durations
            tensor_first = True

        batch_shape, value_shape = validate_tensor_and_function_output_shapes(
            t_shape,
            f_batch_shape,
            f_value_shape,
            t_name,
            f_name,
            validate_value_shape=validate_value_shape,
            tensor_first=tensor_first,
        )

        return Pwc(
            _operation,
            value_shape=value_shape,
            durations=durations,
            batch_shape=batch_shape,
        )

    # operation(Tensor, Tensor)
    check_argument_numeric(x, "x")
    check_argument_numeric(y, "y")
    x_shape = validate_shape(x, "x")
    y_shape = validate_shape(y, "y")
    shape = validate_value_shape(x_shape, y_shape, "x", "y")
    return Tensor(_operation, shape=shape)


class Addition(Node):
    """
    Calculates the element-wise sum between numbers, np.ndarrays, Tensors, Pwcs,
    or Stfs. You can also use the arithmetic operator ``+`` to calculate their sum.

    Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
    so is the returned object. If the objects have different types, Pwcs and Stfs can operate
    with a tensor (returning a Pwc or Stf, respectively).

    This operation supports broadcasting between the different objects. When operating a tensor-like
    object with an Stf or a Pwc, the time dimension of the latter is ignored.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The left summand, :math:`x`.
    y : number or np.ndarray or Tensor or Pwc or Stf
        The right summand, :math:`y`.
    name : str, optional
        The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise sum :math:`x+y`.
    """

    name = "add"
    args = [
        forge.arg("x", type=NumericOrFunction),
        forge.arg("y", type=NumericOrFunction),
    ]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.ARITHMETIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_binary_node_data(_operation, "add", **kwargs)


class Subtraction(Node):
    """
    Calculates the element-wise difference between numbers, np.ndarrays, Tensors, Pwcs,
    or Stfs. You can also use the arithmetic operator ``-`` to calculate their difference.

    Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
    so is the returned object. If the objects have different types, Pwcs and Stfs can operate
    with a tensor (returning a Pwc or Stf, respectively).

    This operation supports broadcasting between the different objects. When operating a tensor-like
    object with an Stf or a Pwc, the time dimension of the latter is ignored.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The minuend, :math:`x`.
    y : number or np.ndarray or Tensor or Pwc or Stf
        The subtrahend, :math:`y`.
    name : str, optional
        The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise difference :math:`x-y`.
    """

    name = "subtract"
    args = [
        forge.arg("x", type=NumericOrFunction),
        forge.arg("y", type=NumericOrFunction),
    ]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.ARITHMETIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_binary_node_data(_operation, "subtract", **kwargs)


class Multiplication(Node):
    r"""
    Calculates the element-wise product between numbers, np.ndarrays, Tensors,
    Pwcs, or Stfs. You can also use the arithmetic operator ``*`` to calculate their product.

    Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
    so is the returned object. If the objects have different types, Pwcs and Stfs can operate
    with a tensor (returning a Pwc or Stf, respectively).

    This operation supports broadcasting between the different objects. When operating a tensor-like
    object with an Stf or a Pwc, the time dimension of the latter is ignored.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The left factor, :math:`x`.
    y : number or np.ndarray or Tensor or Pwc or Stf
        The right factor, :math:`y`.
    name : str, optional
        The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise product :math:`x \times y`.
    """

    name = "multiply"
    args = [
        forge.arg("x", type=NumericOrFunction),
        forge.arg("y", type=NumericOrFunction),
    ]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.ARITHMETIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_binary_node_data(_operation, "multiply", **kwargs)


class TrueDivision(Node):
    """
    Calculates the element-wise division between numbers, np.ndarrays, Tensors, Pwcs,
    or Stfs. You can also use the arithmetic operator ``/`` to calculate their division.

    Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
    so is the returned object. If the objects have different types, Pwcs and Stfs can operate
    with a tensor (returning a Pwc or Stf, respectively).

    This operation supports broadcasting between the different objects. When operating a tensor-like
    object with an Stf or a Pwc, the time dimension of the latter is ignored.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The numerator, :math:`x`.
    y : number or np.ndarray or Tensor or Pwc or Stf
        The denominator, :math:`y`.
    name : str, optional
        The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise division :math:`x/y`.

    See Also
    --------
    floordiv : Divide two values and take the floor of the result.
    """

    name = "truediv"
    args = [
        forge.arg("x", type=NumericOrFunction),
        forge.arg("y", type=NumericOrFunction),
    ]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.ARITHMETIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_binary_node_data(_operation, "truediv", **kwargs)


class FloorDivision(Node):
    r"""
    Calculates the element-wise rounded-down division between real numbers, np.ndarrays, Tensors,
    Pwcs, or Stfs. You can also use the arithmetic operator ``//`` to calculate their floor
    division.

    Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
    so is the returned object. If the objects have different types, Pwcs and Stfs can operate
    with a tensor (returning a Pwc or Stf, respectively).

    This operation supports broadcasting between the different objects. When operating a tensor-like
    object with an Stf or a Pwc, the time dimension of the latter is ignored.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The numerator, :math:`x`. Must be real-valued.
    y : number or np.ndarray or Tensor or Pwc or Stf
        The denominator, :math:`y`. Must be real-valued.
    name : str, optional
        The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise rounded-down division :math:`\lfloor x/y \rfloor`.

    See Also
    --------
    truediv : Divide two values.
    """

    name = "floordiv"
    args = [
        forge.arg("x", type=NumericOrFunction),
        forge.arg("y", type=NumericOrFunction),
    ]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.ARITHMETIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_binary_node_data(_operation, "floordiv", **kwargs)


class Exponentiation(Node):
    """
    Calculates the element-wise power between numbers, np.ndarrays, Tensors, Pwcs,
    or Stfs. You can also use the arithmetic operator ``**`` to calculate their power.

    Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
    so is the returned object. If the objects have different types, Pwcs and Stfs can operate
    with a tensor (returning a Pwc or Stf, respectively).

    This operation supports broadcasting between the different objects. When operating a tensor-like
    object with an Stf or a Pwc, the time dimension of the latter is ignored.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The base, :math:`x`.
    y : number or np.ndarray or Tensor or Pwc or Stf
        The exponent, :math:`y`.
    name : str, optional
        The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise power :math:`x^y`.

    Warnings
    --------
    This function considers that the zeroth power of zero (:math:`0^0`) is
    undefined. This means that you might see an error if you attempt to
    fetch an object that contains :math:`0^0`.
    """

    name = "pow"
    args = [
        forge.arg("x", type=NumericOrFunction),
        forge.arg("y", type=NumericOrFunction),
    ]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.ARITHMETIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_binary_node_data(_operation, "pow", **kwargs)


class ComplexValue(Node):
    """
    Creates element-wise complex values from real numbers, np.ndarrays, Tensors,
    Pwcs, or Stfs, that is, the real and imaginary parts.

    Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
    so is the returned object. If the objects have different types, Pwcs and Stfs can operate
    with a tensor (returning a Pwc or Stf, respectively).

    This operation supports broadcasting between the different objects. When operating a tensor-like
    object with an Stf or a Pwc, the time dimension of the latter is ignored.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The real part, :math:`x`.
    y : number or np.ndarray or Tensor or Pwc or Stf
        The imaginary part, :math:`y`.
    name : str, optional
        The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise complex number :math:`x+iy`.

    See Also
    --------
    abs : Absolute value of a complex object.
    angle : Argument of a complex object.
    conjugate : Conjugate of a complex object.
    imag : Imaginary part of a complex object.
    real : Real part of a complex object.
    """

    name = "complex_value"
    args = [
        forge.arg("x", type=NumericOrFunction),
        forge.arg("y", type=NumericOrFunction),
    ]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.COMPLEX_NUMBERS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_binary_node_data(_operation, "complex", **kwargs)


class Matmul(Node):
    """
    Calculates the matrix multiplication between np.ndarrays, Tensors,
    Pwcs, or Stfs. You can also use the arithmetic operator ``@``
    to calculate their matrix multiplication.

    If any of the inputs is a Pwc or Stf, the output is also a
    Pwc or Stf (mixing Pwcs and Stfs is not supported).
    Otherwise, the output is a Tensor.

    This operation supports broadcasting between the batch dimensions of
    the two input objects. All the dimensions with the exception of the two
    innermost ones (where the matrix multiplication is performed) are
    considered batch dimensions.

    When operating a tensor-like object with an Stf or a Pwc, the time
    dimension of the latter is ignored.

    Parameters
    ----------
    x : np.ndarray or Tensor or Pwc or Stf
        The left multiplicand. It must be a matrix (or batch of matrices)
        and its last dimension must be the same as the second-to-last
        dimension of `y`.
    y : np.ndarray or Tensor or Pwc or Stf
        The right multiplicand. It must be a matrix (or batch of matrices)
        and its second-to-last dimension must be the same as the last
        dimension of `x`.
    name : str, optional
        The name of the node. You can only provide a name if neither `x`
        nor `y` are Stfs.

    Returns
    -------
    Tensor or Pwc or Stf
        The matrix product of the input objects. If any of the input
        objects is a Pwc or Stf, the returned objects has the same
        type. Otherwise, it is a Tensor.

    See Also
    --------
    einsum : Tensor contraction via Einstein summation convention.
    """

    name = "matmul"
    args = [
        forge.arg("x", type=Union[np.ndarray, Tensor, Pwc, Stf]),
        forge.arg("y", type=Union[np.ndarray, Tensor, Pwc, Stf]),
    ]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        def _validate_value_shape(x_shape, y_shape, x_name, y_name):
            if len(x_shape) < 2 or len(y_shape) < 2:
                raise QctrlException(
                    f"The shapes {x_shape} of {x_name} and {y_shape} of"
                    f" {y_name} must have at least two dimensions."
                )
            if not is_broadcastable(x_shape[:-2], y_shape[:-2]):
                raise QctrlException(
                    f"The shapes {x_shape} of {x_name} and {y_shape} of"
                    f" {y_name} must be broadcastable (except in the last two"
                    " dimensions)."
                )

            if x_shape[-1] != y_shape[-2]:
                raise QctrlException(
                    f"The last dimension of the shape {x_shape} of {x_name} must be"
                    f" equal to the second-to-last dimension of the shape {y_shape}"
                    f" of {y_name}."
                )

            # Due to the previous checks, this should never fail.
            trailing_shape = validate_broadcasted_shape(
                x_shape[:-2], y_shape[:-2], f"{x_name} (batch)", f"{y_name} (batch)"
            )

            return trailing_shape + (x_shape[-2], y_shape[-1])

        return _create_flexible_binary_node_data(
            _operation,
            "matmul",
            validate_value_shape=_validate_value_shape,
            **kwargs,
        )


class Kron(Node):
    """
    Calculates the Kronecker product between np.ndarrays, Tensors,
    Pwcs, or Stfs.

    If any of the inputs is a Pwc or Stf, the output is also a
    Pwc or Stf (mixing Pwcs and Stfs is not supported).
    Otherwise, the output is a Tensor.

    This operation supports broadcasting between the batch dimensions of
    the two input objects. All the dimensions with the exception of the two
    innermost ones (where the Kronecker product is performed) are
    considered batch dimensions.

    When operating a tensor-like object with an Stf or a Pwc, the time
    dimension of the latter is ignored.

    Parameters
    ----------
    x : np.ndarray or Tensor or Pwc or Stf
        The left multiplicand. It must be a have at least two dimensions.
    y : np.ndarray or Tensor or Pwc or Stf
        The right multiplicand. It must be a have at least two dimensions.
    name : str, optional
        The name of the node. You can only provide a name if neither `x`
        nor `y` are Stfs.

    Returns
    -------
    Tensor or Pwc or Stf
        The Kronecker product of the input objects. If any of the input
        objects is a Pwc or Stf, the returned objects has the same
        type. Otherwise, it is a Tensor.
    """

    name = "kron"
    args = [
        forge.arg("x", type=Union[np.ndarray, Tensor, Pwc, Stf]),
        forge.arg("y", type=Union[np.ndarray, Tensor, Pwc, Stf]),
    ]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        def _validate_value_shape(x_shape, y_shape, x_name, y_name):
            if len(x_shape) < 2 or len(y_shape) < 2:
                raise QctrlException(
                    f"The shapes {x_shape} of {x_name} and {y_shape} of"
                    f" {y_name} must have at least two dimensions."
                )
            if not is_broadcastable(x_shape[:-2], y_shape[:-2]):
                raise QctrlException(
                    f"The shapes {x_shape} of {x_name} and {y_shape} of"
                    f" {y_name} must be broadcastable (except in the last two"
                    " dimensions)."
                )

            # Due to the previous check, this should never fail.
            trailing_shape = validate_broadcasted_shape(
                x_shape[:-2], y_shape[:-2], f"{x_name}", f"{y_name}"
            )

            return trailing_shape + (
                x_shape[-2] * y_shape[-2],
                x_shape[-1] * y_shape[-1],
            )

        return _create_flexible_binary_node_data(
            _operation,
            "kron",
            validate_value_shape=_validate_value_shape,
            **kwargs,
        )
