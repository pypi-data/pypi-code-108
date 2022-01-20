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
"""Module for unary operation nodes."""

from typing import (
    Tuple,
    Union,
)

import forge
import numpy as np

from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    Pwc,
    Stf,
    Tensor,
)
from qctrlcommons.node.utils import (
    NumericOrFunction,
    validate_batch_and_value_shapes,
    validate_shape,
)
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_numeric,
)

MatrixOrFunction = Union[np.ndarray, Tensor, Pwc, Stf]


def _create_flexible_unary_node_data(_operation, x, name, value_shape_changer=None):
    """
    Common implementation of `create_node_data` for nodes acting on Tensors, Pwcs, and Stfs
    implementing unary functions.

    Parameters
    ----------
    _operation : Operation
        The operation to implement.
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object on which the operation acts.
    name : str
        The name of the node.
    value_shape_changer : Callable[[tuple], tuple], optional
        Callable that transforms the original shape of the object into the shape after the operation
        is applied. Defaults to an identity operation, that is to say, to not change the shape.

    Returns
    -------
    Tensor or Pwc or Stf
        The operation acting on the object.
    """

    # By default don't change shapes.
    if value_shape_changer is None:
        value_shape_changer = lambda shape: shape

    if isinstance(x, Stf):
        check_argument(
            name is None,
            "You can't assign a name to an Stf node.",
            {"name": name},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(x, "x")
        return Stf(
            _operation,
            value_shape=value_shape_changer(value_shape),
            batch_shape=batch_shape,
        )

    if isinstance(x, Pwc):
        batch_shape, value_shape = validate_batch_and_value_shapes(x, "x")
        return Pwc(
            _operation,
            value_shape=value_shape_changer(value_shape),
            durations=x.durations,
            batch_shape=batch_shape,
        )

    check_argument_numeric(x, "x")
    shape = validate_shape(x, "x")
    return Tensor(_operation, shape=value_shape_changer(shape))


class Sqrt(Node):
    r"""
    Calculates the element-wise square root of an object. This can be a number, an array, a tensor,
    or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose square root you want to calculate, :math:`x`. For numbers, arrays, and
        tensors, the object is converted to a tensor and then the operation is applied. For
        functions of time (Pwcs and Stfs), the composition of the operation with the function
        is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise square root, :math:`\sqrt{x}`, of the values or function you provided.
        The returned object is of the same kind as the one you provided, except if you provide a
        number or an np.ndarray in which case it's a Tensor.
    """

    name = "sqrt"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.BASIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Sin(Node):
    r"""
    Calculates the element-wise sine of an object. This can be a number, an array, a tensor,
    or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose sine you want to calculate, :math:`x`. For numbers, arrays, and
        tensors, the object is converted to a tensor and then the operation is applied. For
        functions of time (Pwcs and Stfs), the composition of the operation with the function
        is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise sine, :math:`\sin{x}`, of the values or function you provided.
        The returned object is of the same kind as the one you provided, except if you provide a
        number or an np.ndarray in which case it's a Tensor.
    """

    name = "sin"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.TRIGONOMETRIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Cos(Node):
    r"""
    Calculates the element-wise cosine of an object. This can be a number, an array, a tensor,
    or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose cosine you want to calculate, :math:`x`. For numbers, arrays, and
        tensors, the object is converted to a tensor and then the operation is applied. For
        functions of time (Pwcs and Stfs), the composition of the operation with the function
        is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise cosine, :math:`\cos{x}`, of the values or function you provided.
        The returned object is of the same kind as the one you provided, except if you provide a
        number or an np.ndarray in which case it's a Tensor.
    """

    name = "cos"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.TRIGONOMETRIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Tan(Node):
    r"""
    Calculates the element-wise tangent of an object. This can be a number, an array, a tensor,
    or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose tangent you want to calculate, :math:`x`. For numbers, arrays, and
        tensors, the object is converted to a tensor and then the operation is applied. For
        functions of time (Pwcs and Stfs), the composition of the operation with the function
        is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise tangent, :math:`\tan{x}`, of the values or function you provided.
        The returned object is of the same kind as the one you provided, except if you provide a
        number or an np.ndarray in which case it's a Tensor.
    """

    name = "tan"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.TRIGONOMETRIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Sinh(Node):
    r"""
    Calculates the element-wise hyperbolic sine of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose hyperbolic sine you want to calculate, :math:`x`. For numbers, arrays, and
        tensors, the object is converted to a tensor and then the operation is applied. For
        functions of time (Pwcs and Stfs), the composition of the operation with the function
        is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise hyperbolic sine, :math:`\sinh{x}`, of the values or function you provided.
        The returned object is of the same kind as the one you provided, except if you provide a
        number or an np.ndarray in which case it's a Tensor.
    """

    name = "sinh"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.HYPERBOLIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Cosh(Node):
    r"""
    Calculates the element-wise hyperbolic cosine of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose hyperbolic cosine you want to calculate, :math:`x`. For numbers, arrays,
        and tensors, the object is converted to a tensor and then the operation is applied. For
        functions of time (Pwcs and Stfs), the composition of the operation with the function
        is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise hyperbolic cosine, :math:`\cosh{x}`, of the values or function you
        provided. The returned object is of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.
    """

    name = "cosh"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.HYPERBOLIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Tanh(Node):
    r"""
    Calculates the element-wise hyperbolic tangent of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose hyperbolic tangent you want to calculate, :math:`x`. For numbers, arrays,
        and tensors, the object is converted to a tensor and then the operation is applied. For
        functions of time (Pwcs and Stfs), the composition of the operation with the function
        is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise hyperbolic tangent, :math:`\tanh{x}`, of the values or function you
        provided. The returned object is of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.
    """

    name = "tanh"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.HYPERBOLIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Log(Node):
    r"""
    Calculates the element-wise natural logarithm of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose natural logarithm you want to calculate, :math:`x`. For numbers, arrays,
        and tensors, the object is converted to a tensor and then the operation is applied. For
        functions of time (Pwcs and Stfs), the composition of the operation with the function
        is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise natural logarithm, :math:`\log{x}`, of the values or function you
        provided. The returned object is of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.
    """

    name = "log"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.BASIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Exp(Node):
    r"""
    Calculates the element-wise exponential of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose exponential you want to calculate, :math:`x`. For numbers, arrays,
        and tensors, the object is converted to a tensor and then the operation is applied. For
        functions of time (Pwcs and Stfs), the composition of the operation with the function
        is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise exponential, :math:`e^{x}`, of the values or function you
        provided. The returned object is of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.
    """

    name = "exp"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.BASIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Negative(Node):
    r"""
    Calculates the element-wise numerical negative value of an object. This can be a number,
    an array, a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose numerical negative value you want to calculate, :math:`x`. For numbers,
        arrays, and tensors, the object is converted to a tensor and then the operation is
        applied. For functions of time (Pwcs and Stfs), the composition of the operation with
        the function is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise negation, :math:`-x`, of the values or function you
        provided. The returned object is of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.
    """

    name = "negative"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.ARITHMETIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Real(Node):
    r"""
    Calculates the element-wise real part of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose real part you want to calculate, :math:`x`. For numbers,
        arrays, and tensors, the object is converted to a tensor and then the operation is
        applied. For functions of time (Pwcs and Stfs), the composition of the operation with
        the function is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise real part, :math:`\Re(x)`, of the values or function you provided. The
        returned object is a real object of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.

    See Also
    --------
    complex_value : Create a complex object from its real and imaginary parts.
    imag : Imaginary part of a complex object.
    """

    name = "real"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.COMPLEX_NUMBERS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Imag(Node):
    r"""
    Calculates the element-wise imaginary part of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose imaginary part you want to calculate, :math:`x`. For numbers,
        arrays, and tensors, the object is converted to a tensor and then the operation is
        applied. For functions of time (Pwcs and Stfs), the composition of the operation with
        the function is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise imaginary part, :math:`\Im(x)`, of the values or function you provided. The
        returned object is a real object of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.

    See Also
    --------
    complex_value : Create a complex object from its real and imaginary parts.
    real : Real part of a complex object.
    """

    name = "imag"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.COMPLEX_NUMBERS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Absolute(Node):
    r"""
    Calculates the element-wise absolute value of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose absolute value you want to calculate, :math:`x`. For numbers,
        arrays, and tensors, the object is converted to a tensor and then the operation is
        applied. For functions of time (Pwcs and Stfs), the composition of the operation with
        the function is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise absolute value, :math:`\left|x\right|`, of the values or function you
        provided. The returned object is a real object of the same kind as the one you provided,
        except if you provide a number or an np.ndarray in which case it's a Tensor.

    See Also
    --------
    angle : Argument of a complex object.
    complex_value : Create a complex object from its real and imaginary parts.
    """

    name = "abs"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.BASIC_FUNCTIONS, Category.COMPLEX_NUMBERS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Angle(Node):
    r"""
    Calculates the element-wise argument of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose argument you want to calculate, :math:`x`. For numbers,
        arrays, and tensors, the object is converted to a tensor and then the operation is
        applied. For functions of time (Pwcs and Stfs), the composition of the operation with
        the function is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise argument, :math:`\arg(x)`, of the values or function you provided. The
        returned object is a real object of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.

    See Also
    --------
    abs : Absolute value of a complex object.
    complex_value : Create a complex object from its real and imaginary parts.
    """

    name = "angle"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.COMPLEX_NUMBERS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Conjugate(Node):
    r"""
    Calculates the element-wise complex conjugate of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object whose complex conjugate you want to calculate, :math:`x`. For numbers,
        arrays, and tensors, the object is converted to a tensor and then the operation is
        applied. For functions of time (Pwcs and Stfs), the composition of the operation with
        the function is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise complex conjugate, :math:`x^\ast`, of the values or function you
        provided. The returned object is of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.

    See Also
    --------
    adjoint : Hermitian adjoint of an operator.
    """

    name = "conjugate"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.COMPLEX_NUMBERS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Arcsin(Node):
    r"""
    Calculates the element-wise arcsine of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : float or np.ndarray or Tensor or Pwc or Stf
        The object whose arcsine you want to calculate, :math:`x`. Must be real. For numbers,
        arrays, and tensors, the object is converted to a tensor and then the operation is applied.
        For functions of time (Pwcs and Stfs), the composition of the operation with the
        function is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise arcsine, :math:`\arcsin{x}`, of the values or function you
        provided. Outputs will be in the range of :math:`[-\pi/2, \pi/2]`.
        The returned object is of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.
    """

    name = "arcsin"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.TRIGONOMETRIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Arccos(Node):
    r"""
    Calculates the element-wise arccosine of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : float or np.ndarray or Tensor or Pwc or Stf
        The object whose arccosine you want to calculate, :math:`x`. Must be real. For numbers,
        arrays, and tensors, the object is converted to a tensor and then the operation is applied.
        For functions of time (Pwcs and Stfs), the composition of the operation with the
        function is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise arccosine, :math:`\arccos{x}`, of the values or function you
        provided. Outputs will be in the range of :math:`[0, \pi]`.
        The returned object is of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.
    """

    name = "arccos"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.TRIGONOMETRIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Arctan(Node):
    r"""
    Calculates the element-wise arctangent of an object. This can be a number, an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf.

    Parameters
    ----------
    x : float or np.ndarray or Tensor or Pwc or Stf
        The object whose arctangent you want to calculate, :math:`x`. Must be real. For numbers,
        arrays, and tensors, the object is converted to a tensor and then the operation is applied.
        For functions of time (Pwcs and Stfs), the composition of the operation with the
        function is computed (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise arctangent, :math:`\arctan{x}`, of the values or function you
        provided. Outputs will be in the range of :math:`[-\pi/2, \pi/2]`.
        The returned object is of the same kind as the one you provided, except if you
        provide a number or an np.ndarray in which case it's a Tensor.
    """

    name = "arctan"
    args = [forge.arg("x", type=NumericOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.TRIGONOMETRIC_FUNCTIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return _create_flexible_unary_node_data(_operation, **kwargs)


class Adjoint(Node):
    r"""
    Calculates the element-wise adjoint of the last two dimensions of an object.
    This can be a an array, a tensor, or a time-dependent function in the form of a
    Pwc or an Stf where values have at least two dimensions.

    Parameters
    ----------
    x : np.ndarray or Tensor or Pwc or Stf
        The object whose adjoint you want to calculate, :math:`X^\dagger`.
        Must be a matrix or a matrix-valued function.
        For arrays and tensors, the object is converted to a tensor and then
        the operation is applied. For functions of time (Pwcs and Stfs), the composition
        of the operation with the function is computed
        (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The element-wise adjoint, of the last two dimension of the given matrix or matrix-valued
        function.

    See Also
    --------
    conjugate : Conjugate of a complex object.
    transpose : Reorder the dimensions of a tensor.
    """

    name = "adjoint"
    args = [forge.arg("x", type=MatrixOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        def value_shape_changer(value_shape: Tuple[int, ...]) -> Tuple[int, ...]:
            check_argument(
                len(value_shape) >= 2,
                "x must be at least 2D.",
                {"x": kwargs.get("x")},
                extras={"x.value_shape": value_shape},
            )
            # Unpacking syntax is awesome.
            *batch, x, y = value_shape
            return (*batch, y, x)

        return _create_flexible_unary_node_data(
            _operation, **kwargs, value_shape_changer=value_shape_changer
        )


class Trace(Node):
    r"""
    Calculates the trace of an object. This can be a an array,
    a tensor, or a time-dependent function in the form of a Pwc or an Stf
    where values have at least two dimensions.
    The trace is calculated on the last two dimensions.

    Parameters
    ----------
    x : np.ndarray or Tensor or Pwc or Stf
        The object whose trace you want to calculate, :math:`\mathop{\mathrm{Tr}}(x)`.
        Must be a matrix or a matrix-valued function.
        For arrays and tensors, the object is converted to a tensor and then
        the operation is applied. For functions of time (Pwcs and Stfs), the composition
        of the operation with the function is computed
        (that is, the operation is applied to the function values).
    name : str, optional
        The name of the node. You can only provide a name if the object is not an Stf.

    Returns
    -------
    Tensor or Pwc or Stf
        The trace of the last two dimension of the given matrix or matrix-valued
        function. Outputs will have two fewer dimensions.

    See Also
    --------
    einsum : Tensor contraction via Einstein summation convention.
    """

    name = "trace"
    args = [forge.arg("x", type=MatrixOrFunction)]
    rtype = Union[Tensor, Pwc, Stf]
    categories = [Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        def value_shape_changer(value_shape: Tuple[int, ...]) -> Tuple[int, ...]:
            check_argument(
                len(value_shape) >= 2,
                "x must be at least 2D.",
                {"x": kwargs.get("x")},
                extras={"x.value_shape": value_shape},
            )
            return value_shape[:-2]

        return _create_flexible_unary_node_data(
            _operation, **kwargs, value_shape_changer=value_shape_changer
        )
