# lifted from github.com/wandb/sweeps

import json
from pathlib import Path
from typing import Any

import jsonschema  # type:ignore
from jsonschema import Draft7Validator, validators

testlib_config_jsonschema_fname = Path(__file__).parent / "schema-yea.json"
with open(testlib_config_jsonschema_fname, "r") as f:
    testlib_config_jsonschema = json.load(f)


format_checker = jsonschema.FormatChecker()


@format_checker.checks("float")  # type: ignore
def float_checker(value: Any) -> bool:
    return isinstance(value, float)


@format_checker.checks("integer")  # type: ignore
def int_checker(value: Any) -> bool:
    return isinstance(value, int)


validator = Draft7Validator(schema=testlib_config_jsonschema, format_checker=format_checker)


def extend_with_default(validator_class):  # type: ignore
    # https://python-jsonschema.readthedocs.io/en/stable/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):  # type: ignore

        errored = False
        for error in validate_properties(
            validator,
            properties,
            instance,
            schema,
        ):
            errored = True
            yield error

        if not errored:
            for property, subschema in properties.items():
                if "default" in subschema:
                    instance.setdefault(property, subschema["default"])

    return validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


DefaultFiller = extend_with_default(Draft7Validator)  # type: ignore
default_filler = DefaultFiller(schema=testlib_config_jsonschema, format_checker=format_checker)
