#!/usr/bin/env python3

"""Validate instance using Himarc JSON schema"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from typing import Any, Dict

from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

__all__ = ["validate_himarc", "get_himarc_validation_errors"]


def _get_schema(category="register") -> Dict[str, Any]:
    """Get Himarc JSON schema data."""
    schema_available = ["register", "work"]
    schema_filename = f"himarc-{category}.schema.json"
    if category not in schema_available:
        raise ValueError(
            f"Invalid schema category must be : [{', '.join(schema_available)}]"  # noqa: E501
        )

    schema_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "schema"
    )
    path_schema = os.path.join(schema_dir, schema_filename)
    with open(path_schema, "r") as json_schema_file:
        return json.load(json_schema_file)


def validate_himarc(instance: Dict[str, Any]) -> bool:
    """Validate himarc instance using JSON schema validator."""
    try:
        schema = _get_schema()
        validator = Draft7Validator(schema)
        validator.validate(instance)
        return True
    except ValidationError:
        return False


def get_himarc_validation_errors(
    instance: Dict[str, Any]
) -> Iterable[ValidationError]:
    """Get himarc instance errors using JSON schema validator.

    Returns an iterable of
    <https://python-jsonschema.readthedocs.io/en/stable/errors/#jsonschema.exceptions.ValidationError>
    """
    schema = _get_schema()
    validator = Draft7Validator(schema)
    return validator.iter_errors(instance)
