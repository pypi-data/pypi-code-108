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
"""Module for Node."""
import threading
from typing import (
    Any,
    Optional,
)

import forge

from qctrlcommons.node.wrapper import Operation

LOCAL_THREADING = threading.local()


class Node:
    """
    Custom structure.

    Parameters
    ----------
    node_id: str
        Graph node identity (user-specified name of the node).
    input_kwargs: Dict
        Dictionary of inputs passed to the graph node.

    Attributes
    ----------
    node_id: str
        Graph node identity (user-specified name of the node).
    input_kwargs: Dict:
        Dictionary of inputs passed to the graph node.
    name: str
        Name of node class (corresponding to the name of the generated function).
    args: List
        List of supported arguments for building the function signature.
    kwargs: Dict
        Dictionary of keyword-only arguments for building the function signature.
    rtype: TypeVar
        Return type for the generated function signature.
    categories: List[Category]
        The categories to which this node belongs.
    """

    name = None
    args = []
    kwargs = {"name": forge.kwarg("name", type=Optional[str], default=None)}
    rtype = Any
    optimizable_variable = False
    categories = []

    def __init__(self, node_id, input_kwargs):
        self.node_id = node_id
        self.input_kwargs = input_kwargs

    @classmethod
    def create_node_data(cls, _operation, **kwargs):  # pylint:disable=unused-argument
        """
        Creates the `NodeData` (or sub-class thereof, as determined by the `rtype`) to be returned
        as the node value.

        Can optionally perform validation of the inputs (which themselves will be `NodeData`
        objects, if they come from other graph function calls).
        """
        # create_node_data should be overridden by the subclass.
        raise NotImplementedError

    @classmethod
    def create_pf(cls):
        """Creates the corresponding operation function."""

        def func(name=None, **kwargs):
            operation = Operation(
                graph=LOCAL_THREADING.default_graph,
                operation_name=cls.name,
                name=name,
                **kwargs,
            )
            return cls.create_node_data(_operation=operation, name=name, **kwargs)

        func.__doc__ = cls.__doc__
        func.__name__ = cls.name  # pylint:disable=non-str-assignment-to-dunder-name
        sig = forge.sign(*cls.args, **cls.kwargs)
        func = sig(func)
        func = forge.returns(cls.rtype)(func)

        return func

    @classmethod
    def create_graph_method(cls):
        """
        Creates a callable that can be attached as a method to the Graph class for creating nodes of
        this type.
        """

        def func(self, name=None, **kwargs):
            operation = Operation(
                graph=self, operation_name=cls.name, name=name, **kwargs
            )
            return cls.create_node_data(_operation=operation, name=name, **kwargs)

        func.__doc__ = cls.__doc__
        func.__name__ = cls.name  # pylint:disable=non-str-assignment-to-dunder-name
        sig = forge.sign(forge.arg("self"), *cls.args, **cls.kwargs)
        func = sig(func)
        func = forge.returns(cls.rtype)(func)

        return func
