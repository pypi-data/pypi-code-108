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
import re
from functools import wraps
from typing import (
    Callable,
    Optional,
    Union,
)

import commonmark
import requests
from gql.transport.exceptions import TransportServerError
from graphql import (
    GraphQLField,
    GraphQLInputField,
    GraphQLSchema,
    GraphQLType,
)
from graphql.pyutils.undefined import UndefinedType
from packaging import version
from qctrlcommons.exceptions import QctrlException
from requests import codes
from requests.exceptions import HTTPError

from qctrl import __version__

LOGGER = logging.getLogger(__name__)


class VersionError(QctrlException):
    """Raised when QCTRL client version is incompatible with the API."""


def _is_undefined(value: any) -> bool:
    """Checks if a GraphQL value is of Undefined type.

    Parameters
    ----------
    value: any


    Returns
    -------
    bool
        True if is undefined otherwise False.
    """
    return isinstance(value, UndefinedType)


def _is_deprecated(field: Union[GraphQLField, GraphQLInputField]) -> bool:
    """Checks if the field is deprecated.

    Parameters
    ----------
    field: Union[GraphQLField, GraphQLInputField]


    Returns
    -------
    bool
        True if is deprecated field, otherwise False.

    Raises
    ------
    TypeError
        invalid field.
    """

    if isinstance(field, GraphQLField):
        return field.is_deprecated

    if isinstance(field, GraphQLInputField):
        return bool(re.search("deprecated", (field.description or "").lower()))

    raise TypeError(f"invalid field: {field}")


def abstract_property(func: Callable):
    """Decorator for a property which
    should be overridden by a subclass.
    """

    @wraps(func)
    def decorator(self):
        value = func(self)

        if value is None:
            raise ValueError("abstract property value not set")

        return value

    return property(decorator)


def _clean_text(text: Optional[str]) -> str:
    if text is None:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def _convert_md_to_rst(markdown_text: str) -> str:
    """Converts markdown text to rst.
    Parameters
    ----------

    markdown_text: str
        The text to be converted to rst.

    Returns
    -------
    str
        The rst formatted text
    """
    if markdown_text is None:
        return ""
    parser = commonmark.Parser()
    ast = parser.parse(markdown_text)
    return _clean_text(_parse_to_rst(ast))


def _parse_to_rst(ast_node: commonmark.node.Node) -> str:
    """Converts the markdown formatted ast node to rst text.

    Parameters
    ----------
    ast_node: commonmark.node.Node
        The ast node to be converted to rst.

    Returns
    -------
    str
        The rst formatted text.
    """

    # convert to rst
    renderer = commonmark.ReStructuredTextRenderer()
    text = renderer.render(ast_node)

    # replace double back-tick with single back-tick
    text = text.replace("``", "`")
    function_link_regex = r"(`(\S[^\$\n]+\S)`)__"
    text = re.sub(function_link_regex, r":func:`\2`", text)

    # post processing for unconverted math
    math_block_regex = r"(.. code:: math)"
    math_inline_regex = r"(`\$(.*?)\$`)"

    text = re.sub(math_block_regex, ".. math::", text)
    text = re.sub(math_inline_regex, r":math:`\2`", text)

    reference_link_regex = r"\[\^([\d.]+)\]"
    text = re.sub(reference_link_regex, r"[\1]_", text)

    return text


def check_client_version(func):
    """
    Decorator for functions and methods that may require a minimum version for
    the Q-CTRL Python package defined by the API.
    """

    def raise_exception(exc):
        """
        Raises the `VersionError` exception if the response is a 426 (Upgrade Required).
        Raises the original exception in any other situation.
        """
        # pylint: disable=misplaced-bare-raise

        if not isinstance(exc, HTTPError):
            raise

        if (
            exc.response.status_code
            != codes.UPGRADE_REQUIRED  # pylint: disable=no-member
        ):
            raise

        raise VersionError(
            "Current version of Q-CTRL Python package is not compatible with API. "
            f"Reason: {exc.response.reason}"
        ) from None

    @wraps(func)
    def _check_client_version(*args, **kwargs):
        """
        Handles any exception from the function or method to inject a `VersionError`
        when appropriate.
        """

        try:
            return func(*args, **kwargs)

        except HTTPError as exc:
            raise_exception(exc)

        except (QctrlException, TransportServerError) as exc:
            if not hasattr(exc, "__cause__"):
                raise exc

            raise_exception(exc.__cause__)

        return None

    return _check_client_version


def _check_qctrl_latest_version():
    """
    Checks the latest version of QCTRL in Pypi and
    shows upgrade message if the current version is outdated.
    """
    latest_version = _get_latest_qctrl_version()
    if version.parse(__version__) < version.parse(latest_version):
        print(
            f"Q-CTRL package update available. Your version is {__version__}. "
            f"New version is {latest_version}.",
        )


def _get_latest_qctrl_version() -> str:
    """
    Get the latest version of Q-CTRL python package in Pypi.

    Returns
    -------
    str
        latest version.
    """
    contents = requests.get("https://pypi.org/pypi/qctrl/json").json()
    latest_version = contents["info"]["version"]
    return latest_version


def _get_mutation_result_type(schema: GraphQLSchema, mutation_name: str) -> GraphQLType:
    """Returns the GraphQLType for the given mutation.

    Parameters
    ----------
    mutation_name : str
        The name of the mutation field in the schema.


    Returns
    -------
    GraphQLType
        Result type of the mutation

    Raises
    ------
    KeyError
        invalid mutation name.
    """
    mutation_type = schema.get_type("Mutation")
    assert mutation_type

    try:
        mutation_field = mutation_type.fields[mutation_name]
    except KeyError as error:
        raise KeyError(f"unknown mutation: {mutation_name}") from error

    return mutation_field.type
