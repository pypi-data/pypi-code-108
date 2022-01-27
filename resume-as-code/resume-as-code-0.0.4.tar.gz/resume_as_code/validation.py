import logging
import os
from typing import Dict, Tuple

import yaml
from cerberus import Validator


def validate_resume(
    yaml_resume: Dict[str, Dict], schema_filename: str
) -> Tuple[str, bool]:
    """
    [Validates a certain resume ]

    Args:
        context_location (str): [description]
        yaml_resume (Dict[str, Dict]): [description]

    Raises:
        ValueError: [description]

    Returns:
        [type]: [description]
    """
    with open(schema_filename, "r") as file:
        yaml_schema = yaml.load(file, Loader=yaml.FullLoader)

    validator = Validator(yaml_schema)
    validator.allow_unknown = True  # type: ignore

    if validator.validate(yaml_resume):  # type: ignore
        info_message = f"Resume validates to the resume_schema"
        validation_flag = True
        return info_message, validation_flag
    else:
        warning_message = "The resume does not validate to the resume_schema\n\tErrors: {validation_error}".format(validation_error=validator.errors)  # type: ignore
        validation_flag = False
        return warning_message, validation_flag
