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

from graphql import GraphQLField
from qctrlcommons.node.registry import (
    NODE_REGISTRY,
    TYPE_REGISTRY,
)

from .async_result import AsyncResult
from .client_builder import (
    create_client_auth,
    create_gql_client,
    get_jwt_token,
)
from .custom_environment import create_environment
from .doc import (
    FunctionArgument,
    FunctionDocstring,
)
from .functions import (
    build_function,
    build_signature,
)
from .namespaces import (
    BaseNamespace,
    create_function_namespace,
    create_operation_namespace,
    create_type_namespace,
)
from .result_mixin import ResultMixin
from .type_registry import TypeRegistry

LOGGER = logging.getLogger(__name__)


def _is_valid_function_mutation(name: str) -> bool:
    """Checks if the mutation field corresponds to a valid function which
    should be available to the user. Mutations that should be exposed have a
    single argument named `input`.

    Parameters
    ----------
    name: GraphQLField
        The mutation field to check.

    Returns
    -------
    bool
        True if field is a valid mutation to be exposed to a user.
    """
    return name.startswith("core__")


def build_namespaces(qc: "Qctrl"):  # pylint:disable=invalid-name
    """Builds features and organizes them into namespaces.

    Parameters
    ----------
    qc : Qctrl
        The Qctrl object.


    Returns
    -------
    tuple
        The BaseNamespace objects in the following
        order - function, operation, type.
    """
    function_namespace = create_function_namespace()
    operation_namespace = create_operation_namespace()
    type_namespace = create_type_namespace()

    # operations
    for node_cls in NODE_REGISTRY.as_list():
        func = node_cls.create_pf()
        operation_namespace.extend_functions(func)
    for type_cls in TYPE_REGISTRY:
        operation_namespace.extend({type_cls.__name__: type_cls})

    # functions and types
    mutation_type = qc.gql_api.schema.mutation_type

    for name, field in mutation_type.fields.items():
        if _is_valid_function_mutation(name):
            func = build_function(qc, name, field)
            function_namespace.extend_functions(func)

    type_namespace.add_registry(qc.gql_env.type_registry)

    return (
        function_namespace,
        operation_namespace,
        type_namespace,
    )


__all__ = ["build_namespaces"]
