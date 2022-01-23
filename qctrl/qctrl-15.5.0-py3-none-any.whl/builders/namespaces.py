# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring
import logging
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    List,
)

import inflection

from qctrl.dynamic import dynamic_class

LOGGER = logging.getLogger(__name__)


FUNCTION_NAMESPACE_DOCSTRING = """
    Namespace for functions. Functions are computations using objects
    created from the `types` namespace.
"""


OPERATION_NAMESPACE_DOCSTRING = """
    Namespace for operations. Operations are used to build graphs for
    remote execution of complex computation.

    The types in this namespace each represent the result of some remote
    graph computation. As a result, you cannot directly access data from
    the objects of these types (although where documented you can access
    attributes of objects, which similarly correspond to results of remote
    computations). Instead, you can represent complex computations by
    feeding the objects output from one operation as the inputs to the
    next, and you can fetch the final computed values of objects by
    requesting them as outputs from the appropriate `functions`.
"""


TYPE_NAMESPACE_DOCSTRING = """
    Namespace for types. Objects created from these types are used
    when performing computations defined in the `functions` namespace.
"""


class BaseNamespace(SimpleNamespace):
    """Base namespace class for Qctrl components."""

    @classmethod
    def extend(cls, attrs: Dict[str, Any]) -> None:
        """Extends the namespace class by adding attributes.

        Parameters
        ----------
        attrs : dict
            dict of attributes to add to the namespace.
        attrs: Dict[str, Any]

        Raises
        ------
        AttributeError
            existing attribute found.
        """
        for attr, value in attrs.items():
            if hasattr(cls, attr):
                raise AttributeError(f"existing attr ({attr}) on namespace: {cls}")

            LOGGER.debug("adding attr %s to namespace: %s", attr, cls)
            setattr(cls, attr, value)

    @classmethod
    def extend_functions(cls, *funcs: Callable):
        """Extends the namespace class by adding functions as attributes. The
        function will be added as a staticmethod.

        Parameters
        ----------
        funcs : Callable
            functions to be added to the namespace.

        Returns
        -------
        """
        for func in funcs:
            cls.extend({func.__name__: staticmethod(func)})


class TypeNamespaceMixin:  # pylint:disable=too-few-public-methods
    """
    Mixin to handle namespaced types.
    """

    @classmethod
    def add_registry(cls, type_registry: "TypeRegistry"):
        """
        Adds the registered types as attributes of the namespace.
        """
        for name, type_cls in type_registry.get_type_map().items():
            attr, namespace = type_registry.parse_name(name)
            cls._namespace_extend(namespace or [], attr, type_cls)

        cls.registry = type_registry

    @classmethod
    def _namespace_extend(cls, namespace: List[str], attr: str, obj: Any):
        """
        Recursively create nested namespaces, then use extend
        to set the attribute.
        """
        current = cls
        prefix = ""  # name prefix for nested namespaces

        for item in namespace:
            nested_attr = inflection.underscore(item)
            prefix += inflection.camelize(nested_attr)

            # nested namespace already exists
            if hasattr(current, nested_attr):
                current = getattr(current, nested_attr)

            # created nested namespace
            else:
                nested_namespace_cls = _create_namespace_cls(prefix + "Type")
                nested_namespace = nested_namespace_cls()
                current.extend({nested_attr: nested_namespace})

                # update current for any further nesting
                current = nested_namespace_cls

        current.extend({attr: obj})


@dynamic_class("namespaces")
def _create_namespace_cls(
    prefix: str,
    docstring: str = None,
    base: SimpleNamespace = BaseNamespace,
    mixins: List[type] = None,
) -> SimpleNamespace:
    """Creates a new namespace class and returns an instance of it.

    Parameters
    ----------
    prefix: str
        prefix for the all core namespace. (i.e core__ )
    docstring: str
         namespace docstring. (Default value = None)
    base: SimpleNamespace
         namespace base. (Default value = BaseNamespace)
    mixins: List[type]
         nested mixins (Default value = None)

    Returns
    -------
    SimpleNamespace
        formatted namespace.
    """
    name = f"{inflection.camelize(prefix)}Namespace"
    parents = [base]

    if mixins:
        parents += mixins

    attrs = {}

    if docstring:
        attrs.update({"__doc__": docstring})

    new_cls = type(name, tuple(parents), attrs)
    return new_cls


def create_function_namespace():
    """Creates the function namespace."""
    cls = _create_namespace_cls("Function", FUNCTION_NAMESPACE_DOCSTRING)
    return cls()


def create_operation_namespace():
    """Creates the operation namespace."""
    cls = _create_namespace_cls("Operation", OPERATION_NAMESPACE_DOCSTRING)
    return cls()


def create_type_namespace():
    """Creates the type namespace."""
    cls = _create_namespace_cls(
        "Type", TYPE_NAMESPACE_DOCSTRING, mixins=[TypeNamespaceMixin]
    )
    return cls()


__all__ = [
    "BaseNamespace",
    "create_function_namespace",
    "create_operation_namespace",
    "create_type_namespace",
]
