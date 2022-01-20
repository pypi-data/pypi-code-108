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
"""Utilities for deprecating commons nodes."""
import warnings
from typing import Optional

import forge

from qctrlcommons.exceptions import QctrlException
from qctrlcommons.node.documentation import Category
from qctrlcommons.preconditions import check_argument


def deprecated_node(
    updated_node_name: Optional[str] = None,
    extra_info: Optional[str] = None,
):
    """
    Creates a decorator to mark a node as deprecated. If the deprecation is only a renaming, the
    deprecated node class can be made a subclass of the new node class and left otherwise empty.

    When you mark a node as deprecated, remember to remove the existing "See Also" references to it
    or redirect them to the node with the updated name.

    Parameters
    ----------
    updated_node_name : str, optional
        The name of the node to use instead of the the deprecated node. Defaults to None, in which
        case no alternative is provided in the docstring or when calling the node.
    extra_info : str, optional
        Additional information to provide in the node's docstring and warning when it is called.

    Returns
    -------
    callable
        A callable (decorator) that accepts a node class, replaces its docstring with a deprecation
        notice, and throws a warning when the node is called.

    Example
    -------
    @deprecated_node("new_node_name")  # deprecated 2019/04/14
    class DeprecatedNode(NewNode):
        \"""Deprecated node.\"""

        name = "deprecated_node_name"
    """

    def decorator(node):
        # Replace docstring with deprecation notice.
        docstring = "This node will be removed in the future."
        if updated_node_name is not None:
            docstring += f" Please use :py:func:`{updated_node_name}` instead."
        if extra_info is not None:
            docstring += "\n\n" + extra_info
        node.__doc__ = docstring

        # Mark node as deprecated so it can be skipped in some tests.
        node.is_deprecated = True

        # Ensure the node is in the deprecated documentation category.
        node.categories = [Category.DEPRECATED_OPERATIONS]

        # Update create_node_data to throw a warning if called.
        original_create_node_data = node.create_node_data

        def new_create_node_data(*args, **kwargs):
            warning = f"The '{node.name}' node will be removed in the future."
            if updated_node_name is not None:
                warning += f" Please use '{updated_node_name}' instead."
            if extra_info is not None:
                warning += " " + extra_info
            warnings.warn(warning)
            return original_create_node_data(*args, **kwargs)

        node.create_node_data = new_create_node_data

        return node

    return decorator


def deprecated_parameter(deprecated_name: str, new_name: str):
    """
    Creates a decorator to mark a parameter as deprecated. Use this to mark an argument
    as deprecated on a node written only in terms of the "new" parameter.
    You can deprecate multiple parameters by sequentially applying the decorator for each one.

    The following cases are not supported by this decorator:
        - Parameter is required and occurs before other required parameters.
        - Parameter is required but allowed to be None.

    Parameters
    ----------
    deprecated_name : str
        The deprecated parameter.
    new_name : str
        The parameter name to replace the deprecated one.

    Returns
    -------
    callable
        A callable (decorator) that accepts a node class, adds the deprecated parameter to its
        parameter list in the docstring and to the forge arguments, and wraps its `create_node_data`
        to pass the updated parameter if the deprecated parameter is passed (throwing a warning).

    Example
    -------
    @deprecated_parameter(  # deprecated 2019/08/24
        deprecated_name="pulses_count", new_name="pulse_count"
    )
    class FunctionNode(Node):
        # node definition in terms of pulse_count
    """

    def decorator(node):
        docstring = node.__doc__
        returns_str = "\n\n    Returns"
        if returns_str not in docstring:
            raise QctrlException(
                f"The docstring of {node.name} does not include a Returns section."
            )

        # Split the docstring after the last parameter.
        docstring, docstring_end = docstring.split(returns_str)
        docstring_end = returns_str + docstring_end

        # Add deprecated parameter to docstring.
        deprecated_str = (
            f"\n    {deprecated_name} : deprecated"
            "\n        This parameter will be removed in the future,"
            f"\n        please use `{new_name}` instead."
        )
        docstring = docstring + deprecated_str

        node.__doc__ = docstring + docstring_end

        # Check if the updated parameter is required (i.e. has an empty default).
        # If so, add a None default.
        node_args = []
        for forge_arg in node.args:
            if forge_arg.name == new_name:
                is_required = forge_arg.default == forge.empty
                arg_type = forge_arg.type
                if is_required:
                    forge_arg = forge_arg.replace(default=None)
            node_args.append(forge_arg)
        node.args = node_args

        # Add deprecated parameter as a keyword parameter.
        node_kwargs = node.kwargs.copy()
        node_kwargs[deprecated_name] = forge.kwarg(
            deprecated_name, type=Optional[arg_type], default=None
        )
        node.kwargs = node_kwargs

        # Update create_node_data to throw a warning if called with the deprecated parameter.
        original_create_node_data = node.create_node_data

        def new_create_node_data(*args, **kwargs):
            deprecated_value = kwargs[deprecated_name]
            if deprecated_value is not None:
                warnings.warn(
                    f"The parameter `{deprecated_name}` of `{node.name}` will be "
                    f"removed in the future. Please use `{new_name}` instead."
                )
                kwargs[new_name] = deprecated_value
            updated_value = kwargs[new_name]
            if is_required:
                check_argument(
                    updated_value is not None,
                    f"You need to provide a value for `{new_name}`.",
                    {new_name: updated_value},
                )

            return original_create_node_data(*args, **kwargs)

        node.create_node_data = new_create_node_data

        return node

    return decorator
