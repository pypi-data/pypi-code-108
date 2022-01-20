# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from rer.ufficiostampa.testing import RER_UFFICIOSTAMPA_INTEGRATION_TESTING
from plone.api.portal import set_registry_record
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from transaction import commit
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from plone import api

import unittest
import json


class TestVocabularies(unittest.TestCase):
    """"""

    layer = RER_UFFICIOSTAMPA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        legislatures = [
            {"legislature": "First", "arguments": ["foo", "bar"]},
            {"legislature": "Second", "arguments": ["foo2", "bar2"]},
        ]
        set_registry_record(
            "legislatures",
            json.dumps(legislatures),
            interface=IRerUfficiostampaSettings,
        )
        commit()

    def get_vocab(self, context=None):
        if not context:
            context = self.portal
        factory = getUtility(
            IVocabularyFactory, "rer.ufficiostampa.vocabularies.arguments"
        )
        return factory(context)

    def test_vocab_returns_last_legislature_arguments(self):
        terms = [x.value for x in self.get_vocab()]
        self.assertEqual(terms, ["bar2", "foo2"])

    def test_append_old_value_to_vocab(self):
        doc = api.content.create(
            type="Document",
            title="My Content",
            container=self.portal,
            arguments=["baz"],
        )
        terms = [x.value for x in self.get_vocab(context=doc)]
        self.assertEqual(terms, ["bar2", "baz", "foo2"])
