# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for marshmallow Identifiers schema."""

import idutils
import pytest
from marshmallow import ValidationError
from marshmallow.fields import Str

from marshmallow_utils.schemas import IdentifierSchema


def validate_other(identifier):
    """Validates a numeric identifier."""
    return identifier.isnumeric()


dummy_allowed_schemes = {
    "dummy": {"label": "Dummy", "validator": validate_other}
}
#
# Test cases when identifier is not provided:
#


def test_identifier_required_no_value():
    schema = IdentifierSchema(allowed_schemes=dummy_allowed_schemes)
    with pytest.raises(ValidationError) as e:
        schema.load({})

    errors = e.value.normalized_messages()
    assert errors == {'identifier': 'Missing data for required field.',
                      'scheme': 'Missing data for required field.'}


def test_identifier_required_only_scheme():
    schema = IdentifierSchema(allowed_schemes=dummy_allowed_schemes)
    only_scheme = {"scheme": "dummy"}
    with pytest.raises(ValidationError) as e:
        schema.load(only_scheme)

    errors = e.value.normalized_messages()
    assert errors == {'identifier': 'Missing data for required field.'}


def test_identifier_required_empty_value():
    schema = IdentifierSchema(allowed_schemes=dummy_allowed_schemes)
    empty_identifier = {"identifier": "", "scheme": "dummy"}
    with pytest.raises(ValidationError) as e:
        schema.load(empty_identifier)

    errors = e.value.normalized_messages()
    assert errors == {'identifier': 'Missing data for required field.'}


# required, only identifier -> detect schee


def test_identifier_not_required_no_value():
    schema = IdentifierSchema(
        allowed_schemes=dummy_allowed_schemes,
        identifier_required=False
    )
    assert schema.load({}) == {}


def test_identifier_not_required_only_scheme():
    schema = IdentifierSchema(
        allowed_schemes=dummy_allowed_schemes,
        identifier_required=False,
    )
    only_scheme = {"scheme": "dummy"}
    with pytest.raises(ValidationError) as e:
        schema.load(only_scheme)

    errors = e.value.normalized_messages()
    assert errors == {'identifier': 'Missing data for required field.'}


#
# Test cases when identifier provided:
#

# This schema accepts two attributes: scheme and identifier. The use
# cases are provided in the following table, `-` means that the value
# does not apply.

# 1- The scheme is given -> is allowed (idutils) -> validate -> pass
# 2- The scheme is given -> is NOT allowed -> fail
# 3- The scheme is given -> allowed is empty -> fail
# 4- The scheme is given -> is allowed (custom)  -> validate -> pass
# 5- The scheme is NOT given -> is detected -> is allowed -> validate -> pass
# 6- The scheme is NOT given -> is detected -> is NOT allowed -> fail
# 7- The scheme is NOT given -> is detected -> allowed is empty -> fail
# 8- The scheme is NOT given -> is detected (several) -> is allowed (one of them) -> pass  # noqa
# 9- The scheme is NOT given -> is detected (several) -> is allowed (not the first) -> pass  # noqa
# 10- The scheme is NOT given -> is NOT detected -> fail

# | given  | detected |
# | scheme |  scheme  |  alllowed schemes   | given identifier | result |
# |:------:|:--------:|:-------------------:|:----------------:|:------:|
# |   DOI  |     -    |        [DOI]        | 10.12345/foo.bar |  pass  |
# |   DOI  |     -    |       [Other]       | 10.12345/foo.bar |  fail  |
# |   DOI  |     -    |         []          | 10.12345/foo.bar |  fail  |
# |  Other |     -    | [(Other, val_func)] |     123456       |  pass  |
# |    -   |   [DOI]  |        [DOI]        | 10.12345/foo.bar |  pass  |
# |    -   |   [DOI]  |       [Other]       | 10.12345/foo.bar |  fail  |
# |    -   |   [DOI]  |         []          | 10.12345/foo.bar |  fail  |
# |    -   |  [isni,  |       [isni]        |     0317-8471    |  pass  |  (scheme = isni)  # noqa
# |        |  orcid]  |                     |                  |        |
# |    -   |  [isni,  |       [orcid]       |     0317-8471    |  pass  |  (scheme = orcid)  # noqa
# |        |  orcid]  |                     |                  |        |
# |    -   |     -    |       [isni]        |    00:11:22:33   |  fail  |


def test_given_and_allowed_scheme_valid_value():  # 1
    allowed_schemes = {
        "doi": {"label": "DOI", "validator": idutils.is_doi}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    valid_doi = {
        "scheme": "doi",
        "identifier": "10.12345/foo.bar"
    }
    data = schema.load(valid_doi)
    assert data == valid_doi


def test_given_and_allowed_scheme_invalid_value():  # 1
    allowed_schemes = {
        "doi": {"label": "DOI", "validator": idutils.is_doi}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    invalid_doi = {
        "scheme": "doi",
        "identifier": "12345"
    }
    with pytest.raises(ValidationError) as e:
        schema.load(invalid_doi)

    errors = e.value.normalized_messages()
    assert errors == {'identifier': 'Invalid DOI identifier.'}


def test_given_and_not_allowed_scheme_valid_value():  # 2
    allowed_schemes = {
        "other": {"label": "Other", "validator": validate_other}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    valid_doi = {
        "scheme": "doi",
        "identifier": "10.12345/foo.bar"
    }
    with pytest.raises(ValidationError) as e:
        schema.load(valid_doi)

    errors = e.value.normalized_messages()
    assert errors == {'scheme': 'Invalid scheme.'}


def test_given_custom_and_allowed_scheme_valid_value():  # 4
    allowed_schemes = {
        "other": {"label": "Other", "validator": validate_other}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    valid_other = {
        "scheme": "other",
        "identifier": "12345"
    }

    data = schema.load(valid_other)
    assert data == valid_other


def test_given_custom_and_allowed_scheme_invalid_value():  # 4
    allowed_schemes = {
        "other": {"label": "Other", "validator": validate_other}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    invalid_other = {
        "scheme": "other",
        "identifier": "12345abc"
    }

    with pytest.raises(ValidationError) as e:
        schema.load(invalid_other)

    errors = e.value.normalized_messages()
    assert errors == {
        'identifier': 'Invalid Other identifier.'
    }


def test_detected_and_allowed_scheme_valid_value():  # 5
    allowed_schemes = {
        "doi": {"label": "DOI", "validator": idutils.is_doi}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    valid_doi = {
        "identifier": "10.12345/foo.bar"
    }
    data = schema.load(valid_doi)

    valid_doi["scheme"] = "doi"
    assert data == valid_doi


def test_detected_and_not_allowed_scheme_valid_value():  # 6
    allowed_schemes = {
        "other": {"label": "Other", "validator": validate_other}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    valid_doi = {
        "identifier": "10.12345/foo.bar"
    }

    with pytest.raises(ValidationError) as e:
        schema.load(valid_doi)

    errors = e.value.normalized_messages()
    assert errors == {
        'scheme': 'Missing data for required field.'
    }


def test_detected_and_allowed_scheme_respect_detection_order():  # 8
    allowed_schemes = {
        "orcid": {"label": "ORCID", "validator": idutils.is_orcid},
        "isni": {"label": "ISNI", "validator": idutils.is_isni}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    valid_orcid = {
        "identifier": "0000-0001-6759-6273"
    }
    data = schema.load(valid_orcid)

    valid_orcid["scheme"] = "orcid"
    assert data == valid_orcid


def test_detected_and_allowed_scheme_second_detected():  # 8
    allowed_schemes = {
        "isni": {"label": "ISNI", "validator": idutils.is_isni}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    valid_isni = {
        "identifier": "0000-0001-6759-6273"
    }
    data = schema.load(valid_isni)

    valid_isni["scheme"] = "isni"
    assert data == valid_isni


def test_not_given_not_detected_scheme_for_identifier():  # 10
    allowed_schemes = {
        "isni": {"label": "ISNI", "validator": idutils.is_isni}
    }
    schema = IdentifierSchema(allowed_schemes=allowed_schemes)
    invalid_no_scheme = {
        "identifier": "00:11:22:33"
    }

    with pytest.raises(ValidationError) as e:
        schema.load(invalid_no_scheme)

    errors = e.value.normalized_messages()
    assert errors == {
        'scheme': 'Missing data for required field.'
    }
