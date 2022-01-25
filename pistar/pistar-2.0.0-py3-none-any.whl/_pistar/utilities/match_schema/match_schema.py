# -*- coding: utf-8 -*-
"""
description: this module provides the function match_schema.
"""

import builtins
import importlib
from itertools import chain, islice
from types import FunctionType
from typing import Type, Tuple, Union, List

import yaml

from _pistar.utilities.constants import ACTION_WORD_KEYS as KEYS
from _pistar.utilities.exceptions import AssertionFailureException
from _pistar.utilities.exceptions import EnumerationFailureException
from _pistar.utilities.exceptions import MissingPropertyException
from _pistar.utilities.exceptions import TypeMismatchException


def get_lambda_func(code: str, name="<lambda>") -> FunctionType:
    """
    convert lambda string to lambda function.for example:

    code = 'lambda x: x > 1'

    return FunctionType for this lambda function.
    """

    lambda_code = compile(code, "<string>", "exec")
    foo_func = FunctionType(lambda_code.co_consts[0], globals(), name)

    return foo_func


def get_lambda_expression(lambda_expression):
    """
    description: this function is used to convert string to lambda expression.
    """
    return getattr(lambda_expression, "__doc__", None)


def get_value_name(name, parents):
    """
    description: this function is used to get the value display name.
    """
    return name + "".join(["[" + repr(item) + "]" for item in parents])


def instantiate_assertion(schema):
    """
    description: this function is used to
                 instantiate the assertions in the schema.
    """
    if schema is None:
        return schema

    type_name = schema[KEYS.TYPE]
    if type_name == dict.__name__:
        if KEYS.PROPERTIES in schema:
            for property_name in schema[KEYS.PROPERTIES]:
                schema[KEYS.PROPERTIES][property_name] = instantiate_assertion(schema[KEYS.PROPERTIES][property_name])
    elif type_name == list.__name__:
        if KEYS.ITEMS in schema:
            schema[KEYS.ITEMS] = instantiate_assertion(schema[KEYS.ITEMS])

    if KEYS.ASSERTION in schema:
        assertion_expression = schema[KEYS.ASSERTION]
        schema[KEYS.ASSERTION] = get_lambda_func(assertion_expression)
        schema[KEYS.ASSERTION].__doc__ = assertion_expression

    return schema


def test_assertion(value, name, assertion, parents):
    """
    description: |
        this function is used to pass the value into the assertion,
        if assert successfully, return None, else raise exception.
    """

    if assertion(value):
        return None

    return AssertionFailureException(
        name=get_value_name(name, parents), value=value, assertion=get_lambda_expression(assertion)
    )


def test_enumeration(value, name, enumeration, parents):
    """
    description: |
        this function is used to check whether the value in enumeration,
        if the value in enumeration, return None, else raise exception.
    """

    if value in enumeration:
        return None

    return EnumerationFailureException(name=get_value_name(name, parents), value=value, enumeration=enumeration)


def get_types(types: Union[str, List[str]]) -> Tuple[Type, ...]:
    """
    description: this function is used the convert string to
                 type of the schema.
    """
    _types = list()
    if types == "any":
        _types.append(object)
    elif isinstance(types, list):
        _types = [get_type(_type) for _type in types]
    else:
        _types = [get_type(types)]
    return tuple(_types)


def get_type(name: str) -> Type:
    """
    convert a string to type.

    Attempt to get builtin-type firstly.

    if name is a custom type,use absolute package name,example:

    pkg.foo.bar.clazz

    """

    builtins_maybe = getattr(builtins, name, None)

    if builtins_maybe:
        return builtins_maybe
    # spilt name to class name and package name.
    clazz, possibly_module = islice(chain(reversed(name.rsplit(".", 1)), [None]), 2)
    if possibly_module is None:
        msg = f"cannot resolve module name of type {clazz}.use absolute import name."
        raise ModuleNotFoundError(msg)
    mod = importlib.import_module(possibly_module)
    defined_type = getattr(mod, clazz, None)
    if defined_type is None:
        msg = f"no type named '{name}'"
        raise TypeError(msg)
    return defined_type


def match_schema(
        value, schema, parents=None, name="variable"
):
    """
    description: this function is used to
                 check whether the value matches the schema.
    """
    if parents is None:
        parents = list()

    if isinstance(schema, str):
        schema = yaml.load(schema, Loader=yaml.SafeLoader)
        schema = instantiate_assertion(schema)

    # if value is none, and allow_none is true, it is fine.
    if schema.get(KEYS.ALLOW_NONE, False) and value is None:
        return None

    # check the argument type.
    type_names = schema.get(KEYS.TYPE)
    if not type_names:
        raise MissingPropertyException(KEYS.TYPE, get_value_name(KEYS.TYPE, parents))

    types = get_types(type_names)

    if not isinstance(value, types):
        return TypeMismatchException(
            name=get_value_name(name, parents), value=value, expect_type=[_type.__name__ for _type in types]
        )

    # check the argument assertion.
    if KEYS.ASSERTION in schema:
        exception = test_assertion(name=name, value=value, parents=parents, assertion=schema[KEYS.ASSERTION])
        if exception is not None:
            return exception

    # check the argument schema.
    if KEYS.ENUMERATION in schema:
        exception = test_enumeration(name=name, value=value, parents=parents, enumeration=schema[KEYS.ENUMERATION])
        if exception is not None:
            return exception

    for _type in types:
        if issubclass(_type, dict):
            if KEYS.PROPERTIES not in schema:
                return None

            for property_name, property_schema in schema[KEYS.PROPERTIES].items():
                if property_name not in value:
                    if property_schema.get(KEYS.REQUIRED, True):
                        return MissingPropertyException(
                            property_name=property_name, value_name=get_value_name(name, parents)
                        )
                    continue

                exception = match_schema(
                    name=name,
                    value=value[property_name],
                    schema=schema[KEYS.PROPERTIES][property_name],
                    parents=parents + [property_name],
                )
                if exception is not None:
                    return exception
        elif issubclass(_type, (list, tuple)):
            if KEYS.ITEMS not in schema:
                return None

            for index, item in enumerate(value):
                exception = match_schema(name=name, value=item, schema=schema[KEYS.ITEMS], parents=parents + [index])
                if exception is not None:
                    return exception

    return None
