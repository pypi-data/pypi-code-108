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
"""Utilities in common packages."""
import hashlib
import platform
import re
import uuid
from typing import (
    Any,
    Dict,
)


def get_nested_value(dictionary: dict, ref: str, default=None) -> Any:
    """Returns a nested value in dictionary of dictionaries. Returns default if
    cant be found.

    Example:
    >>> d = {"key1": {"key2": 1}}
    >>> get_nested_value(d, "key1.key2")
    1
    >>> get_nested_value(d, "key1.invalid")
    None
    >>> get_nested_value(d, "key1")
    {"key2": 1}

    Parameters
    ----------
    dictionary: dict
        nested dictionary.
    ref: str
        reference string.
    default : Any
         default value when nested value cannot be found. (Default value = None)

    Returns
    -------
    Any
        nested value from dictionary.
    """

    # unable to continue
    if not isinstance(dictionary, dict):
        return default

    try:
        key, remaining_ref = ref.split(".", 1)

    # no more nesting
    except ValueError:
        return dictionary.get(ref, default)

    # remaining nesting
    return get_nested_value(dictionary.get(key, default), remaining_ref, default)


def generate_user_agent(lib_name: str, version: str) -> str:
    """Generates custom user agents to be forward with API requests headers.

    Parameters
    ----------
    lib_name: str
        package name.
    version: str
        api version.

    Returns
    -------
    str
        formatted user agent.
    """
    return (
        f"{lib_name}/{version} "
        f"({platform.platform()}) "
        f"Python/{platform.python_version()} "
        f"({platform.python_implementation()}) "
        f"Q-CTRL Client UUID/{generate_hashed_uuid()} "
    )


def generate_hashed_uuid() -> str:
    """
    Generates hashed uuid.
    """
    return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()


def is_signature_match(sig1: str, sig2: str) -> bool:
    """Checks if two function signatures match. Compares by removing all
    whitespace.

    Parameters
    ----------
    sig1: str
        function signature.
    sig2: str
        function signature.

    Returns
    -------
    bool
        True if is matched, False otherwise.
    """
    pattern = re.compile(r"\s+")
    return pattern.sub("", sig1) == pattern.sub("", sig2)


def get_gql_error_dict(exc: Exception) -> Dict[str, str]:
    """The gql package stringifies a dictionary when raising an error during
    query execution. Convert the raw error message back to a dict.

    Parameters
    ----------
    exc: Exception
        graphql exception generate from api.

    Returns
    -------
    dict
        formatted error message.
    """
    try:
        error_dict = eval(exc.args[0])  # pylint:disable=eval-used
        assert "message" in error_dict
    except Exception:  # pylint:disable=broad-except
        # if this fails for some reason, return a dict
        # with the error message
        error_dict = {"message": exc.args[0]}

    return error_dict
