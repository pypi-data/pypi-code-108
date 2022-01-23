# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import datetime
from tlsmate.cert_chain import CertChain
from tlsmate.server_profile import SPObject, ProfileSchema, ServerProfileSchema
from tlsmate import utils

from marshmallow import fields
import pytest


class SPUnitTest(SPObject):
    pass


class SPUnitTestSchema(ProfileSchema):
    __profile_class__ = SPUnitTest

    unit_test_1 = fields.Integer()
    unit_test_2 = fields.String()


@ServerProfileSchema.augment
class SPUnitTestAugment(ProfileSchema):
    unit_test = fields.Nested(SPUnitTestSchema)


def test_cert_paras(tlsmate, guballa_de_pem, quo_vadis_root_ca3):
    chain = CertChain()
    for cert in (quo_vadis_root_ca3, guballa_de_pem):
        chain.append_pem_cert(cert.as_bytes())

    prof = tlsmate.server_profile
    prof.allocate_versions()
    prof.append_unique_cert_chain(chain)

    quo_vadis = prof.cert_chains[0].cert_chain[0]
    guballa = prof.cert_chains[0].cert_chain[1]

    cert_policies = quo_vadis.extensions[1].cert_policies
    explicit_text = cert_policies[0].policy_qualifiers[0].explicit_text
    assert type(explicit_text) is str
    assert len(explicit_text)

    text = cert_policies[0].policy_qualifiers[1].text
    assert type(text) is str
    assert len(text)

    signed_ct = guballa.extensions[8].signed_certificate_timestamps
    assert len(signed_ct) == 2
    for ct in signed_ct:
        assert ct.entry_type == "PRE_CERTIFICATE"
        assert type(ct.log_id) is bytes
        assert len(ct.log_id)
        assert type(ct.timestamp) is datetime.datetime
        assert ct.version == "v1"


def test_augment_profile(tlsmate):
    tlsmate.server_profile.unit_test = SPUnitTest(unit_test_1=1, unit_test_2="hello")
    data = tlsmate.server_profile.make_serializable()
    assert "unit_test" in data
    assert data["unit_test"]["unit_test_1"] == 1
    assert data["unit_test"]["unit_test_2"] == "hello"


def test_deserialize_profile_ok(tlsmate):
    data = {"unit_test": {"unit_test_1": 1, "unit_test_2": "hello"}}
    tlsmate.server_profile.load(data)
    assert tlsmate.server_profile.unit_test.unit_test_1 == 1
    assert tlsmate.server_profile.unit_test.unit_test_2 == "hello"


def test_deserialize_profile_nok(tlsmate):
    data = {
        "unit_test": {"unit_test_1": 1, "unit_test_2": "hello"},
        "too_much": "outch",
    }

    with pytest.raises(ValueError, match="fields not defined in schema"):
        tlsmate.server_profile.load(data)


def test_deserialize_full_profile(tlsmate, server_profile):
    tlsmate.server_profile.load(utils.deserialize_data(server_profile))
