"""Base TestlibConfig classes."""

from typing import Dict, List

import jsonschema

import yaml

from .schema import default_filler, validator


def schema_violations_from_proposed_config(config: Dict) -> List[str]:

    schema_violation_messages = []
    for error in validator.iter_errors(config):
        schema_violation_messages.append(f"{error.message}")

    return schema_violation_messages


class TestlibConfig(dict):
    def __init__(self, d: Dict):
        super(TestlibConfig, self).__init__(d)

        if not isinstance(d, TestlibConfig):
            # ensure the data conform to the schema
            schema_violation_msgs = schema_violations_from_proposed_config(d)

            if len(schema_violation_msgs) > 0:
                err_msg = "\n".join(schema_violation_msgs)
                raise jsonschema.ValidationError(err_msg)

        # fill defaults not specified by user
        default_filler.validate(d)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self):
        return yaml.safe_dump(dict(self))
