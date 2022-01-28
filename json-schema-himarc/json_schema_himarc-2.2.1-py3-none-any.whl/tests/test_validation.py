#!/usr/bin/env python3

from json_schema_himarc.validation import (
    _get_schema,
    get_himarc_validation_errors,
    validate_himarc,
)


def test_get_schema():
    schema = _get_schema()
    assert isinstance(schema, dict)
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["$id"] == "http://issn.org/record.schema.json"
    assert schema["title"] == "MARC 21 Format for Bibliographic Data in ISSN+"
    assert (
        schema["description"]
        == "MARC 21 Format for Bibliographic Data in ISSN+"
    )


def test_get_unknown_schema():
    try:
        _get_schema("unknown")
    except ValueError as error:
        assert (
            str(error) == "Invalid schema category must be : [register, work]"
        )


def test_validate_himarc(valid_himarc, invalid_himarc, empty_dict):
    assert validate_himarc(valid_himarc) is True
    assert validate_himarc(invalid_himarc) is False
    assert validate_himarc(empty_dict) is False


def test_get_himarc_errors(valid_himarc, invalid_himarc, empty_dict):
    assert list(get_himarc_validation_errors(valid_himarc)) == []

    errors = list(get_himarc_validation_errors(invalid_himarc))
    assert len(errors) == 4
    err_msgs = [f"{err.validator}: {err.message}" for err in errors]

    assert [  # noqa
        "required: '10' is a required property",
        "required: '11' is a required property",
        "required: '17' is a required property",
        "pattern: 'GBRA' does not match '^([a-zA-Z]{3}|[a-zA-Z]{2}|[0-9]{3})$'",  # noqa
    ] == err_msgs

    errors = list(get_himarc_validation_errors(empty_dict))
    assert len(errors) == 1
    err = errors[0]
    assert err.message == "'fields' is a required property"
