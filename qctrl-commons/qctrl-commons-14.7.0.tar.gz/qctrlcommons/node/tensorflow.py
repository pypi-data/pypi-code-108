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
"""Module for nodes that call straight through to TensorFlow functions."""

from typing import (
    List,
    Optional,
    Tuple,
    Union,
)

import forge
import numpy as np

from qctrlcommons.exceptions import QctrlException
from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import Tensor
from qctrlcommons.node.utils import validate_shape
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_numeric,
    check_sequence_dtype,
)


class Sum(Node):
    """
    Sums the elements in a tensor (or a list of tensors with the same shape) along one or multiple
    of its axes.

    Parameters
    ----------
    input_tensor : np.ndarray or Tensor or list[Tensor]
        The tensor whose elements you want to sum. If you pass a list of tensors, they must all have
        the same shape, and are interpreted as being stacked along a new first dimension (for
        example, if you pass two 2D tensors of shape ``[3, 4]``, the result is equivalent to passing
        the stacked 3D tensor of shape ``[2, 3, 4]``).
    axis : int or list[int] or tuple[int], optional
        The dimension or dimensions along which you want to sum the tensor. Defaults to `None`, in
        which case this node sums along all axes of the tensor.
    keepdims : bool, optional
        Whether or not to retain summed axes in the output tensor. If true, each dimension in
        `axis` has size 1 in the result; otherwise, the dimensions in `axis` are removed from the
        result. Defaults to false.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The tensor obtained by summing the input tensor along the specified axes (or, if `axis` was
        `None`, the tensor obtained by summing the input tensor along all of the specified axes).

    See Also
    --------
    einsum : Tensor contraction via Einstein summation convention.

    Examples
    --------
    >>> x = np.array([1, 2, 3])
    >>> y = np.array([[1, 2, 3], [4, 5, 6]])

    Sum elements of an array.

    >>> graph.sum(x, 0, name="sum_a")
    <Tensor: name="sum_a", operation_name="sum", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_a"])
    >>> result.output["sum_a"]["value"]
    6

    Sum elements of a 2D array along its first dimension.

    >>> graph.sum(y, 0, name="sum_b")
    <Tensor: name="sum_b", operation_name="sum", shape=(3,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_b"])
    >>> result.output["sum_b"]["value"]
    array([5, 7, 9])

    Sum elements of a 2D array along its second dimension.

    >>> graph.sum(y, 1, name="sum_c")
    <Tensor: name="sum_c", operation_name="sum", shape=(2,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_c"])
    >>> result.output["sum_c"]["value"]
    array([ 6, 15])

    Sum elements of a 2D array along its first and second dimension.

    >>> graph.sum(y, [0, 1], name="sum_d")
    <Tensor: name="sum_d", operation_name="sum", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_d"])
    >>> result.output["sum_d"]["value"]
    21
    """

    name = "sum"
    args = [
        forge.arg(
            "input_tensor",
            type=Union[np.ndarray, Tensor, List[Tensor]],
        ),
        forge.arg(
            "axis",
            type=Optional[Union[List[int], Tuple[int, ...]]],
            default=None,
        ),
        forge.arg(
            "keepdims",
            type=bool,
            default=False,
        ),
    ]
    rtype = Tensor
    categories = [Category.ARITHMETIC_FUNCTIONS, Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        input_tensor = kwargs.get("input_tensor")
        # Make a copy of the input, since we'll mutate it.
        axis = kwargs.get("axis")
        keepdims = kwargs.get("keepdims")

        check_argument_numeric(input_tensor, "input_tensor")
        if isinstance(input_tensor, list):
            shapes = [
                validate_shape(tensor, f"input_tensor[{n}]")
                for n, tensor in enumerate(input_tensor)
            ]
            for index, shape in enumerate(shapes[1:]):
                check_argument(
                    shape == shapes[0],
                    "All elements of the input_tensor list must have the same shape.",
                    {"input_tensor": input_tensor},
                    extras={
                        "input_tensor[0].shape": shapes[0],
                        f"input_tensor[{index}].shape": shape,
                    },
                )
            # Note that if the input is an empty list then the shape is somewhat ambiguous (it
            # could be an empty list of tensors of any shape), but for consistency with TF and NP
            # we interpret it as 1D.
            shape = (len(shapes), *shapes[0]) if shapes else ()
        else:
            shape = validate_shape(input_tensor, "input_tensor")

        # Validate and sanitize the reduction axes.
        if axis is None:
            axis = list(range(len(shape)))
        elif isinstance(axis, int):
            axis = [axis]
        else:
            axis = list(axis)
        for i, dimension in enumerate(axis):
            check_argument(
                -len(shape) <= dimension < len(shape),
                f"Elements of axis must be valid axes of the input_tensor (between {-len(shape)} "
                f"and {len(shape)-1}, inclusive).",
                {"input_tensor": input_tensor, "axis": axis},
            )
            if dimension < 0:
                axis[i] = dimension + len(shape)
        axis_set = set(axis)
        check_argument(
            len(axis_set) == len(axis),
            "Elements of axis must refer to unique dimensions of the input_tensor.",
            {"input_tensor": input_tensor, "axis": axis},
        )

        # Calculate the output shape.
        output_shape = []
        for i, size in enumerate(shape):
            if i not in axis_set:
                output_shape.append(size)
                continue
            if keepdims:
                output_shape.append(1)
                continue

        return Tensor(_operation, shape=tuple(output_shape))


class Reverse(Node):
    """
    Reverses a tensor along some specified dimensions.

    Parameters
    ----------
    tensor : np.ndarray or Tensor
        The tensor that you want to reverse.
    axis : list[int]
        The dimensions along which you want to reverse the tensor.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The reversed tensor.

    Examples
    --------
    >>> x = np.array([[1, 2, 3], [4, 5, 6]])

    Reverse an array along its first dimension.

    >>> graph.reverse(x, [0], name="a")
    <Tensor: name="a", operation_name="reverse", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["a"])
    >>> result.output["a"]["value"]
    array([[4, 5, 6],
           [1, 2, 3]])

    Reverse an array along its first and second dimension.

    >>> graph.reverse(x, [0, 1], name="b")
    <Tensor: name="b", operation_name="reverse", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["b"])
    >>> result.output["b"]["value"]
    array([[6, 5, 4],
           [3, 2, 1]])
    """

    name = "reverse"
    args = [
        forge.arg("tensor", type=Union[np.ndarray, Tensor]),
        forge.arg("axis", type=List[int]),
    ]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor = kwargs.get("tensor")
        check_argument_numeric(tensor, "tensor")
        shape = validate_shape(tensor, "tensor")
        return Tensor(_operation, shape=shape)


class Repeat(Node):
    """
    Repeats elements of a tensor.

    Parameters
    ----------
    input : np.ndarray or Tensor
        The tensor whose elements you want to repeat.
    repeats : int or list[int]
        The number of times to repeat each element. If you pass a single int or singleton list, that
        number of repetitions is applied to each element. Otherwise, you must pass a list with the
        same length as `input` along the specified `axis` (or the same total length as `input` if
        you omit `axis`).
    axis : int, optional
        The axis along which you want to repeat elements. If you omit this value then the input is
        first flattened, and the repetitions applied to the flattened array.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The repeated tensor. The result has the same shape as `input` except along `axis`, where its
        size is either the sum of `repeats` (if `repeats` is a list with at least two elements) or
        the product of the original size along `axis` with `repeats` (if `repeats` is a single int
        or singleton list). If `axis` is `None` then the output is 1D, with the sizes as described
        above applied to the flattened input tensor.

    Examples
    --------
    >>> x = np.array([1, 2, 3])
    >>> y = np.array([[1, 2, 3], [4, 5, 6]])

    Duplicate each entry in an array once.

    >>> graph.repeat(x, 2, axis=0, name="a")
    <Tensor: name="a", operation_name="repeat", shape=(6,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["a"])
    >>> result.output["a"]["value"]
    array([1, 1, 2, 2, 3, 3])

    Creates a new array with different repetitions for each element in the original array along its
    second dimension.

    >>> graph.repeat(x, [2, 3, 4], axis=0, name="b")
    <Tensor: name="b", operation_name="repeat", shape=(9,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["b"])
    >>> result.output["b"]["value"]
    array([1, 1, 2, 2, 2, 3, 3, 3, 3])

    Duplicate each entry in an array along its second dimension.

    >>> graph.repeat(y, 2, axis=1, name="c")
    <Tensor: name="c", operation_name="repeat", shape=(2, 6)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["c"])
    >>> result.output["c"]["value"]
    array([[1, 1, 2, 2, 3, 3],
           [4, 4, 5, 5, 6, 6]])

    Creates a new array with different repetitions for each element in the original array along its
    first dimension.

    >>> graph.repeat(y, [2, 3], axis=0, name="d")
    <Tensor: name="d", operation_name="repeat", shape=(5, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["d"])
    >>> result.output["d"]["value"]
    array([[1, 2, 3],
           [1, 2, 3],
           [4, 5, 6],
           [4, 5, 6],
           [4, 5, 6]])
    """

    name = "repeat"
    args = [
        forge.arg("input", type=Union[np.ndarray, Tensor]),
        forge.arg("repeats", type=Union[int, List[int]]),
        forge.arg("axis", type=Optional[int], default=None),
    ]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor = kwargs.get("input")
        repeats = kwargs.get("repeats")
        axis = kwargs.get("axis")

        check_argument_numeric(tensor, "tensor")
        shape = validate_shape(tensor, "tensor")

        if axis is None:
            shape = (np.prod(shape),)
            axis = 0

        if axis < 0:
            axis = len(shape) + axis

        if isinstance(repeats, int):
            repeats = [repeats]

        if len(repeats) == 1:
            repeats = [repeats[0] for _ in range(shape[axis])]
        else:
            check_argument(
                len(repeats) == shape[axis],
                "Length of repeats must be one or must match length of input along axis.",
                kwargs,
                extras={"length of input along axis": shape[axis]},
            )

        return Tensor(
            _operation, shape=shape[:axis] + (sum(repeats),) + shape[axis + 1 :]
        )


class CumulativeSum(Node):
    """
    Calculates the cumulative sum of a tensor along a specified dimension.

    Parameters
    ----------
    x : np.ndarray or Tensor
        The tensor whose elements you want to sum. It must have at least
        one dimension.
    axis : int, optional
        The dimension along which you want to sum the tensor. Defaults to 0.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The cumulative sum of `x` along dimension `axis`.

    Examples
    --------
    >>> x = np.array([1, 2, 3])
    >>> y = np.array([[1, 2, 3], [4, 5, 6]])

    Calculate the cumulative sum of an array.

    >>> graph.cumulative_sum(x, axis=0, name="a")
    <Tensor: name="a", operation_name="cumulative_sum", shape=(3,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["a"])
    >>> result.output["a"]["value"]
    array([1, 3, 6])

    Calculate the cumulative sum of a 2D array along its first dimension.

    >>> graph.cumulative_sum(y, axis=0, name="b")
    <Tensor: name="b", operation_name="cumulative_sum", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["b"])
    >>> result.output["b"]["value"]
    array([[1, 2, 3],
           [5, 7, 9]])

    Calculate the cumulative sum of a 2D array along its second dimension.

    >>> graph.cumulative_sum(y, axis=1, name="c")
    <Tensor: name="c", operation_name="cumulative_sum", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["c"])
    >>> result.output["c"]["value"]
    array([[ 1,  3,  6],
           [ 4,  9, 15]])
    """

    name = "cumulative_sum"
    args = [
        forge.arg("x", type=Union[np.ndarray, Tensor]),
        forge.arg("axis", default=0, type=int),
    ]
    rtype = Tensor
    categories = [Category.ARITHMETIC_FUNCTIONS, Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        x_value = kwargs.get("x")
        check_argument_numeric(x_value, "x")
        shape = validate_shape(x_value, "x")
        if len(shape) == 0:
            raise QctrlException(
                f"The shape of x={x_value} must have at least 1 dimension."
            )
        return Tensor(_operation, shape=shape)


class Transpose(Node):
    """
    Reorders the dimensions of a tensor.

    Parameters
    ----------
    a : np.ndarray or Tensor
        The tensor whose dimensions you want to permute, :math:`x`.
    perm : list[int] or np.ndarray(int), optional
        The order of the input dimensions for the returned tensor. If you provide it, it must
        be a permutation of all integers between 0 and ``N-1``, where `N` is the rank of `a`.
        If you don't provide it, the order of the dimensions is inverted, that is to say,
        it defaults to ``[N-1, …, 1, 0]``.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The input tensor with its dimensions permuted. The `i`-th dimension of the returned tensor
        corresponds to the `perm[i]`-th input dimension.

    See Also
    --------
    adjoint : Hermitian adjoint of an operator.
    einsum : Tensor contraction via Einstein summation convention.

    """

    name = "transpose"
    args = [
        forge.arg("a", type=Union[np.ndarray, Tensor]),
        forge.arg(
            "perm",
            type=Optional[Union[List[int], np.ndarray]],
            default=None,
        ),
    ]
    rtype = Tensor
    categories = [Category.LINEAR_ALGEBRA, Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        a_value = kwargs.get("a")
        perm = kwargs.get("perm")
        check_argument_numeric(a_value, "a")
        check_argument_numeric(perm, "perm")
        a_shape = validate_shape(a_value, "a")
        if perm is None:
            shape = a_shape[::-1]
        else:
            sorted_perm = np.sort(np.array(perm) % len(perm))
            check_argument(
                np.all(sorted_perm == range(len(a_shape))),
                "The value of perm must be a valid permutation of the indices of a.",
                {"perm": perm},
                extras={"a.shape": a_shape},
            )
            shape = tuple(a_shape[dimension] for dimension in perm)
        return Tensor(_operation, shape=shape)


class Einsum(Node):
    r"""
    Performs tensor contraction via Einstein summation convention.

    Use this node to perform multi-dimensional, linear algebraic array operations between tensors.

    Parameters
    ----------
    equation : str
        The equation describing the tensor contraction.
        The format is the same as in NumPy's einsum.
    tensors : list[Tensor or np.ndarray]
        The tensors to be contracted.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The contracted Tensor.

    See Also
    --------
    matmul : Matrix multiplication between objects.
    sum : Sum elements in a tensor along one or multiple axes.
    trace : Trace of an object.
    transpose : Reorder the dimensions of a tensor.

    Notes
    -----
    You can use tensor contraction with Einstein summation convention to create a new tensor from
    its element-wise computation from other tensors. This applies to any tensor operation that you
    can write as an equation relating the elements of the result as sums over products of elements
    of the inputs.

    The element-wise equation of the operation is summarized by a string describing the Einstein
    summation to be performed on the inputs. For example, the matrix multiplication between two
    matrices can be written as

    .. math::
        R_{ik} = \sum_j P_{ij} Q_{jk} .

    To convert this element-wise equation to the appropriate string, you can:
    remove summations and variable names (`ik = ij * jk`),
    move the output to the right (`ij * jk = ik`), and
    replace "`*`" with "`,`" and "`=`" with "`->`" (`ij,jk->ik`).
    You can also use an ellipsis (...) to broadcast over unchanged dimensions.

    For more information about Einstein summation, see `Einstein notation on Wikipedia`_.

    .. _Einstein notation on Wikipedia:
        https://en.wikipedia.org/wiki/Einstein_notation

    Examples
    --------
    >>> x = np.arange(16, dtype=float)

    Diagonal of a matrix.

    >>> graph.einsum("ii->i", [x.reshape(4, 4)], name="diagonal")
    <Tensor: name="diagonal", operation_name="einsum", shape=(4,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["diagonal"])
    >>> result.output["diagonal"]["value"]
    array([0., 5., 10., 15.])

    Trace of a matrix.

    >>> graph.einsum('ii->', [x.reshape(4, 4)], name="trace")
    <Tensor: name="trace", operation_name="einsum", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["trace"])
    >>> result.output["trace"]["value"]
    30.0

    Sum over matrix axis.

    >>> graph.einsum('ij->i', [x.reshape((4, 4))], name="sum_1")
    <Tensor: name="sum_1", operation_name="einsum", shape=(4,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_1"])
    >>> result.output["sum_1"]["value"]
    array([ 6., 22., 38., 54.])

    Sum over tensor axis ignoring leading dimensions.

    >>> graph.einsum('...ji->...i', [x.reshape((2, 2, 4))], name='sum_2')
    <Tensor: name="sum_2", operation_name="einsum", shape=(2, 4)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_2"])
    >>> result.output["sum_2"]["value"]
    array([[ 4.,  6.,  8., 10.],
           [20., 22., 24., 26.]])

    Reorder tensor axes.

    >>> graph.einsum('ijk->jki', [x.reshape((8, 1, 2))], name="reorder")
    <Tensor: name="reorder", operation_name="einsum", shape=(1, 2, 8)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["reorder"])
    >>> result.output["reorder"]["value"]
    array([[[ 0.,  2.,  4.,  6.,  8., 10., 12., 14.],
            [ 1.,  3.,  5.,  7.,  9., 11., 13., 15.]]])

    Vector inner product.

    >>> graph.einsum('i,i->', [x, np.ones(16)], name="inner")
    <Tensor: name="inner", operation_name="einsum", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["inner"])
    >>> result.output["inner"]["value"]
    120.0

    Matrix-vector multiplication.

    >>> graph.einsum('ij,j->i', [x.reshape((4, 4)), np.ones(4)], name="multiplication")
    <Tensor: name="multiplication", operation_name="einsum", shape=(4,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["multiplication"])
    >>> result.output["multiplication"]["value"]
    array([ 6., 22., 38., 54.])

    Vector outer product.

    >>> graph.einsum("i,j->ij", [x[:2], x[:3]], name="outer")
    <Tensor: name="outer", operation_name="einsum", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["outer"])
    >>> result.output["outer"]["value"]
    array([[0., 0., 0.],
           [0., 1., 2.]])

    Tensor contraction.

    >>> graph.einsum(
    ...     "ijk,jil->kl", [x.reshape((4, 2, 2)), x.reshape((2, 4, 2))], name="contraction"
    ... )
    <Tensor: name="contraction", operation_name="einsum", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["contraction"])
    >>> result.output["contraction"]["value"]
    array([[504., 560.],
           [560., 624.]])

    Trace along first two axes.

    >>> graph.einsum("ii...->i...", [x.reshape((2, 2, 4))], name="trace_2")
    <Tensor: name="trace_2", operation_name="einsum", shape=(2, 4)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["trace_2"])
    >>> result.output["trace_2"]["value"]
    array([[ 0.,  1.,  2.,  3.],
           [12., 13., 14., 15.]])

    Matrix multiplication using the left-most indices.

    >>> graph.einsum(
    ...     "ij...,jk...->ik...", [x.reshape((1, 4, 4)), x.reshape((4, 1, 4))], name="left_most"
    ... )
    <Tensor: name="left_most", operation_name="einsum", shape=(1, 1, 4)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["left_most"])
    >>> result.output["left_most"]["value"]
    array([[[224., 276., 336., 404.]]])
    """

    name = "einsum"
    args = [
        forge.arg("equation", type=str),
        forge.arg("tensors", type=List[Union[np.ndarray, Tensor]]),
    ]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS, Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensors = kwargs.get("tensors")

        check_argument(
            isinstance(tensors, list),
            "The tensors must be in a list.",
            {"tensors": tensors},
        )
        check_argument(
            all(isinstance(tensor, (Tensor, np.ndarray)) for tensor in tensors),
            "Each of the tensors must be a Tensor or a np.ndarray.",
            {"tensors": tensors},
        )

        equation = kwargs.get("equation")
        check_argument(
            isinstance(equation, str),
            "The equation must be a string.",
            {"equation": equation},
        )

        try:
            shape = np.einsum(
                equation, *[np.zeros(tensor.shape) for tensor in tensors]
            ).shape
        except ValueError:
            check_argument(
                False,
                "The equation is not valid or is incompatible with the inputs.",
                {"tensors": tensors, "equation": equation},
            )

        return Tensor(_operation, shape=shape)


class Reshape(Node):
    """
    Reshapes a tensor into a new shape, keeping the order of its elements.

    Parameters
    ----------
    tensor : np.ndarray or Tensor
        The tensor you want to reshape.
    shape : tuple[int]
        The new shape of the tensor.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The reshaped tensor.
    """

    name = "reshape"
    args = [
        forge.arg("tensor", type=Union[np.ndarray, Tensor]),
        forge.arg("shape", type=Tuple[int, ...]),
    ]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor_value = kwargs.get("tensor")
        shape_value = kwargs.get("shape")

        check_argument_numeric(tensor_value, "tensor")
        tensor_shape = validate_shape(tensor_value, "tensor")
        check_sequence_dtype(shape_value, int, "shape")

        tensor_element_count = np.prod(tensor_shape)
        shape_element_count = np.prod(shape_value)
        unique, counts = np.unique(shape_value, return_counts=True)
        if unique[0] <= 0:
            check_argument(
                unique[0] == -1,
                "Axis lengths in the new shape must be positive or -1.",
                {"shape": shape_value},
            )
            check_argument(
                counts[0] == 1,
                "Can only specify one axis with -1 in the new shape.",
                {"shape": shape_value},
            )
            missing_dim = (-1) * tensor_element_count / shape_element_count
            check_argument(
                int(missing_dim) == missing_dim,
                "Unable to allocate a whole number of elements for the unspecified axis (-1).",
                {"tensor": tensor_value, "shape": shape_value},
            )
            shape_new = tuple(
                np.where(np.array(shape_value) == -1, missing_dim, shape_value)
            )
        else:
            check_argument(
                tensor_element_count == shape_element_count,
                "New shape must have the same number of elements as the input tensor.",
                {"tensor.shape": tensor_shape, "shape": shape_value},
                extras={
                    "np.prod(tensor.shape)": tensor_element_count,
                    "np.prod(shape)": shape_element_count,
                },
            )
            shape_new = shape_value
        return Tensor(_operation, shape=shape_new)
