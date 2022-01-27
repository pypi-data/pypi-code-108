"""Tests for pycddl."""

import pytest
import cbor2

from pycddl import Schema, ValidationError


def assert_invalid_caught(schema, data):
    """
    The schema correctly identifies that data as invalid.
    """
    with pytest.raises(ValidationError):
        schema.validate_cbor(cbor2.dumps(data))


def test_invalid_schema_errors_out():
    """
    Attempting to create a new ``CDDLSchema`` with an invalid CDDL schema
    results in a ValueError.
    """
    with pytest.raises(ValueError):
        Schema(
            """
    reputation-object = {
        application: text
        reputons: [* reputon]

    """
        )


REPUTON_SCHEMA = """\
reputation-object = {
  application: text
  reputons: [* reputon]
}

reputon = {
  rater: text
  assertion: text
  rated: text
  rating: float16
  ? confidence: float16
  ? normal-rating: float16
  ? sample-size: uint
  ? generated: uint
  ? expires: uint
  * text => any
}
"""


def test_schema_validates_good_document():
    """
    A valid schema will validate a valid document (i.e. no exception is
    raised).
    """
    schema = Schema(REPUTON_SCHEMA)
    for document in [
        {"application": "blah", "reputons": []},
        {
            "application": "conchometry",
            "reputons": [
                {
                    "rater": "Ephthianura",
                    "assertion": "codding",
                    "rated": "sphaerolitic",
                    "rating": 0.34133473256800795,
                    "confidence": 0.9481983064298332,
                    "expires": 1568,
                    "unplaster": "grassy",
                },
                {
                    "rater": "nonchargeable",
                    "assertion": "raglan",
                    "rated": "alienage",
                    "rating": 0.5724646875815566,
                    "sample-size": 3514,
                    "Aldebaran": "unchurched",
                    "puruloid": "impersonable",
                    "uninfracted": "pericarpoidal",
                    "schorl": "Caro",
                },
            ],
        },
    ]:
        schema.validate_cbor(cbor2.dumps(document))


def test_schema_fails_bad_documents():
    """
    Bad documents cause ``validate_cbor()`` to raise a ``ValidationError``.
    """
    schema = Schema(REPUTON_SCHEMA)
    for bad_document in [
        b"",
        cbor2.dumps({"application": "blah"}),  # missing reputons key
        cbor2.dumps({"application": "blah", "reputons": "NOT A LIST"}),
    ]:
        with pytest.raises(ValidationError):
            schema.validate_cbor(bad_document)


@pytest.mark.xfail
def test_bad_schema_fails_validation_of_good_document():
    """
    Some invalid schemas are not caught by initial loading.  They will however
    fail to validate documents, which is sufficient for correct program
    behavior, even if it is annoying during development of schemas.

    Actual behavior is buggy: validation passes. This will be fixed in
    https://github.com/anweiss/cddl/issues/106
    """
    schema = Schema(
        """
    reputation-object = {
        application: text
        reputons: [* reputon]
    }
    """
    )
    assert_invalid_caught(
        schema, {"application": "blah", "reputons": [{"reputon": "xx"}]}
    )


def test_integer_value_enforcement():
    """
    Schemas that limit minimum integer value are enforced.  This is important
    for security, for example.
    """
    uint_schema = Schema(
        """
    object = {
        xint: uint
    }
    """
    )
    for i in [0, 1, 4, 5, 500, 1000000]:
        uint_schema.validate_cbor(cbor2.dumps({"xint": i}))
    for i in [-1, -10000, "x", 0.3]:
        assert_invalid_caught(uint_schema, i)

    more_than_3_schema = Schema(
        """
    object = {
        xint: int .gt 3
    }
    """
    )
    for i in [4, 5, 500, 1000000]:
        more_than_3_schema.validate_cbor(cbor2.dumps({"xint": i}))
    for i in [-1, -10000, "x", 0.3, 0, 1, 2, 3]:
        assert_invalid_caught(more_than_3_schema, {"xint": i})
