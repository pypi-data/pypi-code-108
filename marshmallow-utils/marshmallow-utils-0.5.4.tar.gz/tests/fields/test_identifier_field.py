# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for marshmallow Identifiers field."""

from functools import partial

import idutils
import pytest
from marshmallow import Schema, ValidationError
from marshmallow.fields import Nested

from marshmallow_utils.fields import IdentifierSet
from marshmallow_utils.schemas import IdentifierSchema


class TestSchema(Schema):
    allowed_schemes = {
        "orcid": {"label": "ORCID", "validator": idutils.is_orcid},
        "doi": {"label": "DOI", "validator": idutils.is_doi}
    }
    identifiers = IdentifierSet(
        Nested(
            partial(IdentifierSchema, allowed_schemes=allowed_schemes)
        )
    )


def test_valid_identifiers():
    valid_identifiers = {
        "identifiers": [{
            "identifier": "0000-0001-6759-6273",
            "scheme": "orcid"
            }, {
            "identifier": "10.5281/zenodo.9999999",
            "scheme": "doi"
        }]
    }

    assert TestSchema().load(valid_identifiers) == valid_identifiers


def test_invalid_duplicate_identifiers():
    duplicate_identifiers = [
        {
            "identifiers": [{  # full duplication
                "identifier": "10.5281/zenodo.9999999",
                "scheme": "doi"
                }, {
                "identifier": "10.5281/zenodo.9999999",
                "scheme": "doi"
            }]
        }, {
            "identifiers": [{  # no scheme provided
                "identifier": "10.5281/zenodo.9999999",
                }, {
                "identifier": "10.5281/zenodo.9999999",
            }]
        }
    ]

    for case in duplicate_identifiers:
        with pytest.raises(ValidationError) as e:
            TestSchema().load(case)
        errors = e.value.normalized_messages()
        assert errors == {
            'identifiers': ['Only one identifier per scheme is allowed.']
        }
