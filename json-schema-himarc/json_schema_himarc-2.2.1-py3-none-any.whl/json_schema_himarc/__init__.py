#!/usr/bin/env python3

"""
Validate instance using Himarc JSON schema

    >>> from json_schema_himarc import
    ...     validate_himarc, get_himarc_validation_errors
    ... )
    >>> instance = {}
    >>> if not validate_himarc(instance):
    >>>     errors = get_himarc_validation_errors(instance)
"""

from json_schema_himarc.validation import (  # noqa: E501
    get_himarc_validation_errors,
    validate_himarc,
)

__all__ = ["get_himarc_validation_errors", "validate_himarc"]
