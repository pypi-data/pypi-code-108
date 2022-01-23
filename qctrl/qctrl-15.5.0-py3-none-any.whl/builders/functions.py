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
from typing import (
    Callable,
    Union,
)

import forge
from gql.transport.exceptions import TransportQueryError
from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLType,
    is_required_input_field,
)
from qctrlcommons.exceptions import QctrlGqlException
from qctrlcommons.utils import get_gql_error_dict

from qctrl.queries import StartActionQuery
from qctrl.utils import _is_undefined

from .async_result import AsyncResult
from .doc import (
    FunctionArgument,
    FunctionDocstring,
    Returns,
)
from .graphql_utils import GraphQLEnvironment
from .result_mixin import ResultMixin
from .utils import _get_function_name

LOGGER = logging.getLogger(__name__)


def build_function(
    qctrl: "Qctrl",
    mutation_name: str,
    mutation_field: GraphQLField,
) -> Callable:
    """Returns a function which can be used to execute a GraphQL mutation.

    Parameters
    ----------
    qctrl: Qctrl
        The Qctrl object.

    mutation_name: str
        The name of the mutation.

    mutation_field: GraphQLField
        The corresponding mutation field.

    Returns
    -------
    func : Callable
        A callable function.
    """

    input_type = _get_mutation_input_type(mutation_field)

    def get_query(**kwargs) -> StartActionQuery:
        return qctrl.gql_env.build_mutation_query(
            mutation_name,
            input_type,
            mutation_field.type,
            kwargs,
        )

    def func(**kwargs):
        disable_result_cache = kwargs.pop("disable_result_cache", False)
        query = get_query(**kwargs)

        LOGGER.debug("query:%s", query)

        if qctrl.is_collecting():
            result = query.create_result_object({"action": {}})
            qctrl.collector.add(query, AsyncResult(mutation_field.type, result))
            return result

        try:
            response = query(disable_result_cache=disable_result_cache)
        except TransportQueryError as exc:
            LOGGER.debug("query execution failed: %s", exc)
            error_dict = get_gql_error_dict(exc)
            raise QctrlGqlException(error_dict["message"]) from exc

        LOGGER.debug("response:%s", response)

        if mutation_name not in response:
            LOGGER.error("response:%s", response)
            raise ValueError(f"response missing mutation name: {mutation_name}")

        result = query.create_result_object(response[mutation_name])

        LOGGER.info(
            "Remote function %s called - Action ID: %s", result.name, result.action_id
        )
        refresh_query = query.get_refresh_query()
        qctrl.gql_env.wait_for_completion(
            refresh_query, AsyncResult(mutation_field.type, result)
        )

        return result

    # set function name
    func.__name__ = _get_function_name(mutation_name)

    # build signature and sign function
    signature = build_signature(
        qctrl.gql_env,
        input_type,
        mutation_field.type,
    )

    func = signature(func)

    # build docstring
    docstring = FunctionDocstring.from_markdown(mutation_field.description)
    return_type = forge.fsignature(func).return_annotation
    output_field_type = _get_mutation_output_type(mutation_field.type)
    docstring.returns = Returns(
        return_type=f"{return_type.__module__}.{return_type.__name__}",
        description=output_field_type.description,
    )

    for field_name, field in input_type.fields.items():
        docstring.params.append(
            FunctionArgument(
                qctrl.gql_env.field_to_attr(field_name),
                arg_type=qctrl.gql_env.type_registry.get_doc_field_type(field.type),
                optional=not is_required_input_field(field),
                description=field.description,
            )
        )

    # set function docstring
    func.__doc__ = str(docstring)

    func.request = get_query

    return func


def build_signature(
    env: GraphQLEnvironment, input_type: GraphQLType, return_type: GraphQLType = None
):
    """
    Returns a function signature based on the input fields. All fields
    are added as keyword args.
    """

    args = []

    for field_name, field in input_type.fields.items():
        default_value = field.default_value

        # if no default value
        if _is_undefined(default_value):

            # use special flag for required field
            if isinstance(field.type, GraphQLNonNull):
                default_value = forge.FParameter.empty

            # otherwise, use None
            else:
                default_value = None

        # build arg and add to list
        args.append(
            forge.kwarg(
                env.field_to_attr(field_name),
                type=_get_type_hint(env, field.type),
                default=default_value,
            )
        )

    LOGGER.debug("signature args:%s", args)

    # build signature
    signature = forge.sign(*args, **forge.kwargs)

    if return_type:
        returns = _get_type_hint(env, return_type, base=ResultMixin)

        if returns is not forge.FParameter.empty:
            signature = forge.compose(
                signature,
                forge.returns(returns),
            )

    return signature


def _get_mutation_input_type(field: GraphQLField) -> GraphQLType:
    """Given a mutation field, return the input
    argument type. Every mutation is expected to
    have exactly one argument, named `input`.

    Parameters
    ----------
    field: GraphQLField
        The mutation field


    Returns
    -------
    GraphQLType
        type of input arguments

    Raises
    ------
    KeyError
        if mutation field does not have `input` arg
    ValueError
        if argument is not type of GraphQLArgument.
    TypeError
        if the input type is not GraphQLNonNull or GraphQLInputObjectType.
    """
    try:
        input_arg = field.args["input"]
    except KeyError as error:
        raise KeyError(f"mutation field does not have input arg: {field}") from error

    if not isinstance(input_arg, GraphQLArgument):
        raise ValueError(f"unexpected input arg type: {input_arg}")

    _type = input_arg.type

    if not isinstance(_type, GraphQLNonNull):
        raise TypeError(f"expected non-null type; got: {_type}")

    _type = _type.of_type

    if not isinstance(_type, GraphQLInputObjectType):
        raise TypeError(f"expected input object type; got: {_type}")

    return _type


def _get_mutation_output_type(field_type: GraphQLType) -> GraphQLType:
    """
    Given a mutation field, return the output
    argument type. Every mutation is expected to
    have exactly one NonNull output type.

    Parameters
    ----------
    field_type: GraphQLType
        the type of the mutation field

    Returns
    -------
    GraphQLType
        the final output type.

    Raises
    ------
    TypeError
        if it is not GraphQLObjectType.
    """
    if isinstance(field_type, (GraphQLNonNull, GraphQLList)):
        return _get_mutation_output_type(field_type.of_type)

    if not isinstance(field_type, GraphQLObjectType):
        raise TypeError(f"expected object type; got: {field_type}")
    return field_type


def _get_type_hint(
    env: GraphQLEnvironment, field_type: GraphQLType, **build_opts
) -> Union[type, forge.FParameter.empty]:
    """
    Returns a type hint for the GraphQL field type. If a type registry
    is being used, `build_opts` can be used.

    for configuration if a new type is being created - see
    `TypeRegistry.get_type_hint`.
    If no type hint can be determined, forge.FParameter.empty
    is returned.

    Parameters
    ----------
    field_type: GraphQLType

    build_opts


    Returns
    -------
    Union[type, forge.FParameter.empty]
        type hint.
    """
    type_hint = env.type_registry.get_type_hint(field_type, **build_opts)
    return type_hint or forge.FParameter.empty
