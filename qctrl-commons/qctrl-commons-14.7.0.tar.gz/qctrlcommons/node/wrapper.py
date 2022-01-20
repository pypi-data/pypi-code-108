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
"""Module for all Node wrappers."""
from dataclasses import dataclass
from typing import Any

from qctrlcommons.exceptions import QctrlGraphIntegrityError


class Operation:  # pylint:disable=abstract-method
    """
    Custom class for storing a reference to a named computation method.
    It performs some validation during initialization to check
    that all the argument nodes belong to the same graph.
    """

    def __init__(self, graph, operation_name, *args, **kwargs):
        self.graph = graph
        self.args = args
        self.kwargs = kwargs
        self._name = None

        node_name = kwargs.pop("name", None)
        if node_name is None:
            node_name = operation_name + "_#" + str(len(self.graph.operations))
        elif "#" in node_name:
            raise ValueError(f"'#' is not allowed in name :'{node_name}'.")

        self.set_name(node_name)
        self.operation_name = operation_name

        self._iter_validate_op_graph(args)
        self._iter_validate_op_graph(kwargs)

    @property
    def name(self):
        """
        unique node name.
        """
        return self._name

    @name.setter
    def name(self, name):
        self.set_name(name)

    def set_name(self, name):
        """
        Set name and add to graph operation.
        """

        if self._name:
            self.graph.operations.pop(self._name)
            # only check this when the name is explicitly set by user after
            # they have created the node
            if "#" in name:
                raise ValueError(f"'#' is not allowed in name :'{name}'.")

        if name in self.graph.operations:
            raise ValueError(f"duplicate name '{name}'.")

        self._name = name
        self.graph.operations[name] = self

    def _iter_validate_op_graph(self, value: Any) -> None:
        """
        Validates that `value.graph` (if it exists) is the
        same as `self.graph`. This is to avoid having arguments of type `Operation`
        that belong to a different graph.

        Parameters
        ----------
        value: Any
            One of the args/kwargs passed to the __init__ function.

        Raises
        ------
        QctrlGraphIntegrityError
            In case any of the arguments of the current operations
            belongs to a different instance `Graph`
        """
        if isinstance(value, (list, tuple)):
            for val in value:
                self._iter_validate_op_graph(val)
        elif isinstance(value, dict):
            for val in value.values():
                self._iter_validate_op_graph(val)
        elif isinstance(value, NodeData):
            if self.graph != value.operation.graph:
                raise QctrlGraphIntegrityError(
                    f"{value.operation.name} does not "
                    f"belong to the same graph as {self.name!r}."
                )


@dataclass
class NodeData:
    """
    Base class for information about a created node in a client-side graph.

    Contains information about the corresponding operation, together with type-specific
    validation data.
    """

    operation: Operation


class NameMixin:
    """
    Mixin to be used by nodes whose name can be chosen and accessed by the
    user. That is, the nodes that are fetchable.
    """

    @property
    def name(self):
        """
        Get the name/id of operation.
        """
        return self.operation.name

    @name.setter
    def name(self, name):
        self.operation.name = name


@dataclass
class NamedNodeData(NodeData, NameMixin):
    """
    NodeData subclass to be used by basic nodes that also have names.
    """
