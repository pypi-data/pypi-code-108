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
Module for generic nodes defined in core.
"""
from typing import (
    List,
    Optional,
    Union,
)

import forge
import numpy as np

from qctrlcommons.node.base import Node
from qctrlcommons.node.deprecation import deprecated_node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    Target,
    Tensor,
)
from qctrlcommons.node.utils import validate_shape
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_iterable,
    check_argument_nonzero,
    check_argument_numeric,
    check_argument_orthogonal_projection_operator,
    check_argument_partial_isometry,
    check_operator,
)


class TargetOperation(Node):
    r"""
    Creates information about the target for system time evolution.

    Nodes created with this function contain two types of information: the
    target gate for the system time evolution, and the projection operator
    that defines the subspace of interest for robustness.

    Parameters
    ----------
    operator : np.ndarray or Tensor
         The target gate :math:`U_\mathrm{target}`. Must be a non-zero partial
         isometry.
    filter_function_projector : np.ndarray, optional
        The orthogonal projection matrix :math:`P` onto the subspace used for
        filter function calculations. If you provide a value then it must be
        Hermitian and idempotent. Defaults to the identity matrix.

    Returns
    -------
    Target
        The node containing the specified target information.

    See Also
    --------
    infidelity_pwc : Total infidelity of a system with a piecewise-constant Hamiltonian.
    infidelity_stf : Total infidelity of a system with a sampleable Hamiltonian.

    Notes
    -----
    The target gate :math:`U_\mathrm{target}` is a non-zero partial isometry,
    which means that it can be expressed in the form
    :math:`\sum_j \left|\psi_j\right>\left<\phi_j\right|`, where
    :math:`\left\{\left|\psi_j\right>\right\}` and
    :math:`\left\{\left|\phi_j\right>\right\}` both form (non-empty)
    orthonormal, but not necessarily complete, sets. Such a target represents
    a target state :math:`\left|\psi_j\right>` for each initial state
    :math:`\left|\phi_j\right>`. The resulting operational infidelity is 0
    if and only if, up to global phase, each initial state
    :math:`\left|\phi_j\right>` maps exactly to the corresponding final state
    :math:`\left|\psi_j\right>`.

    The filter function projector :math:`P` is an orthogonal projection
    matrix, which means that it satisfies :math:`P=P^\dagger=P^2`. The image
    of :math:`P` defines the set of initial states from which the calculated
    filter function measures robustness.

    Examples
    --------
    Define a target operation for the Pauli :math:`X` gate.

    >>> target_operation = graph.target(operator=np.array([[0, 1], [1, 0]]))
    >>> target_operation
    <Target: operation_name="target", value_shape=(2, 2)>

    See more examples in the `How to optimize controls robust to strong noise sources
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-robust-
    to-strong-noise-sources>`_ user guide.
    """

    name = "target"
    args = [
        forge.arg("operator", type=Union[np.ndarray, Tensor]),
        forge.arg("filter_function_projector", type=Optional[np.ndarray], default=None),
    ]
    kwargs = {}  # Target should not accept `name` as parameter
    rtype = Target
    categories = [Category.OPTIMAL_AND_ROBUST_CONTROL]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operator = kwargs.get("operator")
        value_shape = validate_shape(operator, "operator")

        if isinstance(operator, np.ndarray):
            check_argument_numeric(operator, "operator")
            check_argument_partial_isometry(operator, "operator")
            check_argument_nonzero(operator, "operator")
        else:
            check_operator(operator, "operator")
            check_argument(
                len(value_shape) == 2,
                "The operator must be a matrix, not a batch.",
                {"operator": operator},
                extras={"operator.shape": value_shape},
            )

        filter_function_projector = kwargs.get("filter_function_projector")
        if filter_function_projector is not None:
            check_argument_numeric(
                filter_function_projector, "filter_function_projector"
            )
            check_argument_orthogonal_projection_operator(
                filter_function_projector, "filter_function_projector"
            )

        return Target(_operation, value_shape=value_shape)


class Gradient(Node):
    r"""
    Calculates a single gradient vector for all the variables.

    The gradient is a vector containing all the first partial derivatives
    of the `tensor` with respect to the `variables`.

    Parameters
    ----------
    tensor : Tensor(scalar, real)
        The real scalar tensor :math:`T` whose gradient vector you want to
        calculate.
    variables : list[Tensor(real)]
        The list of real variables :math:`\{\theta_i\}` with respect to
        which you want to take the first partial derivatives of the
        tensor. If any of the tensors of the list is not scalar, this
        function treats each of the elements of the tensor as a different
        variable. It does this by flattening all tensors and concatenating
        them in the same sequence that you provided in this list.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor(1D, real)
        The gradient vector :math:`\nabla T` containing
        the first partial derivatives of the `tensor` :math:`T` with respect to
        the `variables` :math:`\{\theta_i\}`.

    Warnings
    --------
    This function currently doesn't support calculating a gradient vector for
    a graph which includes an `infidelity_pwc` node if it involves a Hamiltonian
    with degenerate eigenvalues at any segment. In that case, the function
    returns a `nan` gradient vector.

    Notes
    -----
    The :math:`i` element of the gradient contains the partial
    derivative of the `tensor` with respect to the ith
    `variables`:

    .. math::
        (\nabla T)_{i} = \frac{\partial T}{\partial \theta_i}.

    The variables :math:`\{\theta_i\}` follow the same sequence as the
    input list of `variables`. If some of the `variables` are not scalars,
    this function flattens them and concatenates them in the same order of
    the list of `variables` that you provided to create the sequence of
    scalar variables :math:`\{\theta_i\}`.
    """
    name = "gradient"
    args = [
        forge.arg("tensor", type=Tensor),
        forge.arg("variables", type=List[Tensor]),
    ]
    rtype = Tensor
    categories = [Category.DERIVATIVES]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor = kwargs.get("tensor")
        variables = kwargs.get("variables")
        check_argument(
            isinstance(tensor, Tensor),
            "The tensor parameter must be a Tensor.",
            {"tensor": tensor},
        )
        tensor_shape = validate_shape(tensor, "tensor")
        check_argument(
            tensor_shape == (),
            "The tensor must be a scalar tensor.",
            {"tensor": tensor},
        )
        check_argument_iterable(variables, "variables")
        check_argument(
            all(isinstance(variable, Tensor) for variable in variables),
            "Each of the variables must be a Tensor.",
            {"variables": variables},
        )
        variable_count = sum(
            [
                np.prod(validate_shape(variable, f"variables[{n}]"), dtype=int)
                for n, variable in enumerate(variables)
            ]
        )
        shape = (variable_count,)
        return Tensor(_operation, shape=shape)


class Hessian(Node):
    r"""
    Calculates a single Hessian matrix for all the variables.

    The Hessian is a matrix containing all the second partial derivatives
    of the `tensor` with respect to the `variables`.

    Parameters
    ----------
    tensor : Tensor(scalar, real)
        The real scalar tensor :math:`T` whose Hessian matrix you want to
        calculate.
    variables : list[Tensor(real)]
        The list of real variables :math:`\{\theta_i\}` with respect to
        which you want to take the second partial derivatives of the
        tensor. If any of the tensors of the list is not scalar, this
        function treats each of the elements of the tensor as a different
        variable. It does this by flattening all tensors and concatenating
        them in the same sequence that you provided in this list.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor(2D, real)
        The real Hessian matrix :math:`H` containing the second partial
        derivatives of the `tensor` :math:`T` with respect to the
        `variables` :math:`\{\theta_i\}`.

    Warnings
    --------
    This function currently doesn't support calculating a Hessian matrix for
    a graph which includes an `infidelity_pwc` node if it involves a Hamiltonian
    with degenerate eigenvalues at any segment. In that case, the function
    returns a `nan` Hessian matrix.

    Notes
    -----
    The :math:`(i,j)` element of the Hessian contains the partial
    derivative of the `tensor` with respect to the ith and the jth
    `variables`:

    .. math::
        H_{i,j} = \frac{\partial^2 T}{\partial \theta_i \partial \theta_j}.

    The variables :math:`\{\theta_i\}` follow the same sequence as the
    input list of `variables`. If some of the `variables` are not scalars,
    this function flattens them and concatenates them in the same order of
    the list of `variables` that you provided to create the sequence of
    scalar variables :math:`\{\theta_i\}`.

    If you choose a negative log-likelihood as the tensor :math:`T`, you
    can use this Hessian as an estimate of the Fisher information matrix.
    """
    name = "hessian"
    args = [
        forge.arg("tensor", type=Tensor),
        forge.arg("variables", type=List[Tensor]),
    ]
    rtype = Tensor
    categories = [Category.DERIVATIVES]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor = kwargs.get("tensor")
        variables = kwargs.get("variables")
        check_argument(
            isinstance(tensor, Tensor),
            "The tensor parameter must be a Tensor.",
            {"tensor": tensor},
        )
        tensor_shape = validate_shape(tensor, "tensor")
        check_argument(
            tensor_shape == (),
            "The tensor must be a scalar tensor.",
            {"tensor": tensor},
        )
        check_argument_iterable(variables, "variables")
        check_argument(
            all(isinstance(variable, Tensor) for variable in variables),
            "Each of the variables must be a Tensor.",
            {"variables": variables},
        )
        variable_count = sum(
            [
                np.prod(validate_shape(variable, f"variables[{n}]"), dtype=int)
                for n, variable in enumerate(variables)
            ]
        )
        shape = (variable_count, variable_count)
        return Tensor(_operation, shape=shape)


@deprecated_node("hessian")  # deprecated 2021/11/19
class HessianMatrix(Hessian):
    """Deprecated node."""

    name = "hessian_matrix"


class Concatenate(Node):
    """
    Concatenates a list of tensors along a specified dimension.

    Parameters
    ----------
    tensors : list[np.ndarray or Tensor]
        The list of tensors that you want to concatenate. All of them must have the
        same shape in all dimensions except `axis`.
    axis : int
        The dimension along which you want to concatenate the tensors.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The concatenated tensor.

    Notes
    -----
    This node only concatenates on an existing axis, it does not create new
    axes. If you want to stack along a new axis or concatenate scalars, add
    a new axis to the tensors with ``[None]``.

    Examples
    --------
    >>> x = np.array([[1, 2, 3], [4, 5, 6]])
    >>> y = np.array([[7, 8, 9]])

    Concatenate `x` and `y` along their first dimension.

    >>> graph.concatenate(tensors=[x, y], axis=0, name="node_0")
    <Tensor: name="node_0", operation_name="concatenate", shape=(3, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["node_0"])
    >>> result.output["node_0"]["value"]
    array([[1., 2., 3.],
           [4., 5., 6.],
           [7., 8., 9.]])

    Concatenate two `x` arrays along their second dimension.

    >>> graph.concatenate(tensors=[x, x], axis=1, name="node_1")
    <Tensor: name="node_1", operation_name="concatenate", shape=(2, 6)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["node_1"])
    >>> result.output["node_1"]["value"]
    array([[1., 2., 3., 1., 2., 3.],
           [4., 5., 6., 4., 5., 6.]])
    """

    name = "concatenate"
    args = [
        forge.arg("tensors", type=List[Union[np.ndarray, Tensor]]),
        forge.arg("axis", type=int),
    ]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensors = kwargs.get("tensors")
        axis = kwargs.get("axis")
        check_argument_iterable(tensors, "tensors")
        tensor_shapes = []
        for index, tensor in enumerate(tensors):
            check_argument_numeric(tensor, f"tensors[{index}]")
            tensor_shape = validate_shape(tensor, f"tensors[{index}]")
            check_argument(
                len(tensor_shape) > axis,
                "Each tensor must have at least as many axes as the parameter `axis`.",
                {"tensors": tensors, "axis": axis},
                extras={f"tensors[{index}].shape": tensor_shape},
            )
            tensor_shapes.append(tensor_shape)
            check_argument(
                (tensor_shape[:axis] + tensor_shape[axis + 1 :])
                == (tensor_shapes[0][:axis] + tensor_shape[axis + 1 :]),
                "All tensors must have the same size in every dimension,"
                " except in the dimension of axis.",
                {"tensors": tensors},
                extras={
                    "tensors[0].shape": tensor_shapes[0],
                    f"tensors[{index}].shape": tensor_shape,
                },
            )
        shape = (
            tensor_shapes[0][:axis]
            + (sum([tensor_shape[axis] for tensor_shape in tensor_shapes]),)
            + tensor_shapes[0][axis + 1 :]
        )
        return Tensor(_operation, shape=shape)


class TensorOperation(Node):
    """
    Creates a real or complex Tensor with the data provided.

    Parameters
    ----------
    data : number or np.ndarray or Tensor
        The data to convert to an appropriate tensor.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        Real or complex Tensor representation of the input data.

    Notes
    -----
    Use this node to create a Tensor from some numeric `data`. Note that you
    can pass numbers or NumPy arrays to operations that accept Tensors.
    """

    name = "tensor"
    args = [forge.arg("data", type=Union[int, float, complex, np.ndarray, Tensor])]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        data = kwargs.get("data")
        check_argument_numeric(data, "data")
        shape = validate_shape(data, "data")
        return Tensor(_operation, shape=shape)
