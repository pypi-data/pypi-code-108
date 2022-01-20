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
"""Module for nodes that access attributes of other nodes."""
from typing import (
    List,
    Union,
)

import forge

from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import Pwc
from qctrlcommons.node.wrapper import NamedNodeData


class GetAttributeNode(Node):
    """
    Gets an attribute from a node value.

    Typically you would use the syntax ``value.attr`` instead of using this function directly.

    Parameters
    ----------
    value : Any
        The value from which to get the item.
    attr : str
        The name of the attribute.
    name : str, optional
        The name of the node.

    Returns
    -------
    Any
        The item or items obtained from ``value.attr``, or to be more precise,
        ``getattr(value, attr)``.

    Notes
    -----
    Only certain combinations of `value` and `attr` are supported:

    ``Pwc.values``
        The tensor of values of a `Pwc`.
    """

    name = "getattr"
    args = [
        forge.arg("value"),
        forge.arg("attr", type=str),
    ]
    categories = [Category.OTHER_OPERATIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        value = kwargs.get("value")
        attr = kwargs.get("attr")

        valid_combinations = [(Pwc, "values")]
        for valid_value_type, valid_attr in valid_combinations:
            if isinstance(value, valid_value_type) and attr == valid_attr:
                return NamedNodeData(_operation)

        # Invalid combination of value type and attr, so show an error message.
        raise QctrlArgumentsValueError(
            "Not allowed to fetch attribute",
            kwargs,
            extras={
                "Valid combinations": [
                    f"{valid_value_type.__name__}.{valid_attr}"
                    for valid_value_type, valid_attr in valid_combinations
                ]
            },
        )


class GetItemNode(Node):
    """
    Gets an item (or items) from a node value.

    Typically you would use slicing syntax ``value[key]`` instead of
    using this function directly.

    Parameters
    ----------
    value : Any
        The value from which to get the item.
    key : int or slice or list[int or slice]
        The key for the item or items.
    name : str, optional
        The name of the node.

    Returns
    -------
    Any
        The item or items obtained from ``value[key]``.
    """

    name = "getitem"
    args = [
        forge.arg("value"),
        forge.arg("key", type=Union[int, slice, List[Union[int, slice]]]),
    ]
    categories = [Category.OTHER_OPERATIONS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        return NamedNodeData(_operation)
