# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Placeholder for the validations done in this package."""
import jsonschema
import sys

from typing import Dict

from azureml._common._error_definition import AzureMLError
from azureml.exceptions import UserErrorException

from azureml.responsibleai.common._errors.error_definitions import ArtifactSizeLimitExceededError


_DEFAULT_UPLOAD_BYTES_LIMIT = 20 * 1024 * 1024


def _check_serialization_size(rai_insights_str: str, max_bytes: int = _DEFAULT_UPLOAD_BYTES_LIMIT) -> None:
    """Ensure a rai insight isn't too large.

    :param rai_insights_str: A serialized version of RAI insight that needs to be uploaded.
    :type rai_insights_str: str
    :param max_bytes: Maximum size in bytes that the RAI insight shouldn't exceed.
    :type max_bytes: int
    """
    rai_insights_str_bytes = sys.getsizeof(rai_insights_str)
    if rai_insights_str_bytes > max_bytes:
        raise UserErrorException._with_error(
            AzureMLError.create(
                ArtifactSizeLimitExceededError, actual=rai_insights_str_bytes, limit=max_bytes
            )
        )


def _check_against_json_schema(schema_json: Dict, rai_output_dict: Dict) -> None:
    """Validate a RAI insight dictionary against a schema json.

    :param schema_json: Schema json against which the RAI insight dictionary needs to be validated.
    :type schema_json: Dict
    :param rai_output_dict: Actual RAI insight dictionary.
    :type rai_output_dict: Dict
    """
    jsonschema.validate(rai_output_dict, schema_json)
