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
"""Module for NodeRegistry."""
import inspect
from collections import defaultdict
from typing import List

from qctrlcommons.node import node_data
from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import create_documentation_sections

# pylint:disable=unused-wildcard-import, wildcard-import
from .attribute import *
from .binary import *
from .core import *
from .infidelity import *
from .ms import *
from .optimization import *
from .oqs import *
from .pwc import *
from .sparse import *
from .stf import *
from .stochastic import *
from .tensorflow import *
from .unary import *

# Registry of all types created by operations.
TYPE_REGISTRY = [
    node_data.ConvolutionKernel,
    node_data.Pwc,
    node_data.SparsePwc,
    node_data.Stf,
    node_data.Target,
    node_data.Tensor,
]


class NodeRegistry:
    """Register all the imported Node type class."""

    def __init__(self, nodes):
        self._nodes = {}
        self._module_map = defaultdict(list)

        for node in nodes:
            if node.name in self._nodes:
                raise ValueError(f"duplicate name: {node.name}")
            module = node.__module__
            submodule = module.split(".")[-1]
            self._module_map[submodule].append(node.name)
            self._nodes[node.name] = node

    def get_node_cls(self, name: str) -> Node.__class__:
        """Get the Node class by name from the operation.

        Parameters
        ----------
        name : str
            the requested name.

        Returns
        -------
        Node
            the match Node class.

        Raises
        ------
        KeyError
            if the node doesn't exist in registry.
        """
        if name not in self._nodes:
            raise KeyError(f"unknown node: {name}")

        return self._nodes[name]

    def as_list(self, exclude_node_types=None) -> List:
        """Converts the nodes to a list. Allows exclusion of certain nodes, if
        not all nodes are needed.

        Parameters
        ----------
        exclude_node_types : List[string]
            The node types to exclude from the list. (Default value = None)

        Returns
        -------
        List
            list of Node classes.

        Raises
        ------
        KeyError
            if `excluded_node` does not exist in registry.
        """

        if exclude_node_types is not None:
            exclusion_list = []
            for excluded_node in exclude_node_types:
                if excluded_node not in self._module_map:
                    raise KeyError(f"unknown excluded node: {excluded_node}")

                exclusion_list.extend(self._module_map[excluded_node])

            list_difference = list(set(list(self._nodes.keys())) - set(exclusion_list))
            node_subset = {key: self._nodes[key] for key in list_difference}
            return list(node_subset.values())

        # TODO order by name?
        return list(self._nodes.values())

    @classmethod
    def load(cls):
        """Load all the register Node class.

        Parameters
        ----------
        cls : class
            class object.

        Returns
        -------
        NodeRegistry
            an updated NodeRegistry with all different types of Node class.
        """
        nodes = []

        for obj in globals().values():
            if inspect.isclass(obj) and issubclass(obj, Node) and obj.name is not None:
                nodes.append(obj)

        return cls(nodes)


NODE_REGISTRY = NodeRegistry.load()

# Prepare documentation categories.
NODE_DOCUMENTATION_SECTIONS = create_documentation_sections(
    {node_cls.name: node_cls.categories for node_cls in NODE_REGISTRY.as_list()}
)
