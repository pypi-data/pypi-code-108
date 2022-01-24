# -*- coding: utf-8 -*-
from collective.dexteritytextindexer.behavior import IDexterityTextIndexer
from cpskin.core.behaviors.metadata import IAdditionalSearchableText
from cpskin.core.interfaces import ICPSkinCoreLayer
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from cpskin.core.utils import add_behavior
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.textfield.value import RichTextValue
from zope.interface import alsoProvides

import unittest


class TestOrganizations(unittest.TestCase):

    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.request, ICPSkinCoreLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        portal_languages = api.portal.get_tool("portal_languages")
        portal_languages.addSupportedLanguage("fr")
        applyProfile(self.portal, "collective.contact.core:default")
        add_behavior("organization", "collective.taxonomy.generated.types_activites")
        add_behavior("organization", IAdditionalSearchableText.__identifier__)
        add_behavior("organization", IDexterityTextIndexer.__identifier__)
        self.directory = api.content.create(self.portal, "directory", "directory")
        self.organization = api.content.create(self.directory, "organization", "orga")
        self.organization.language = 'fr'

    def test_organization(self):
        catalog = api.portal.get_tool("portal_catalog")
        self.organization.additional_searchable_text = "additional"
        richtextvalue = RichTextValue(u"activity_value", "text/plain", "text/html")
        self.organization.activity = richtextvalue
        richtextvalue = RichTextValue(
            u"informations_complementaires_value", "text/plain", "text/html"
        )
        self.organization.informations_complementaires = richtextvalue
        self.organization.taxonomy_typesactivites = [u"nvf7kib5ed", u"f8bvklelyb"]
        self.organization.reindexObject()

        brain = catalog(UID=self.organization.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        searchable_text = indexes["SearchableText"]
        self.assertTrue("additional" in searchable_text)
        self.assertTrue("activity_value" in searchable_text)
        self.assertTrue("informations_complementaires_value" in searchable_text)
        self.assertTrue("autres" in searchable_text)
        self.assertTrue("animations" in searchable_text)
