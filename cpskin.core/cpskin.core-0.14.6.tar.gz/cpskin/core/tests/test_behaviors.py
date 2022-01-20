# -*- coding: utf-8 -*-
from collective.dexteritytextindexer.behavior import IDexterityTextIndexer
from cpskin.core.behaviors.indexview import ICpskinIndexViewSettings
from cpskin.core.behaviors.metadata import IAdditionalSearchableText
from cpskin.core.behaviors.metadata import IHiddenTags
from cpskin.core.behaviors.metadata import IRelatedContacts
from cpskin.core.interfaces import ICPSkinCoreLayer
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from cpskin.core.utils import add_behavior
from cpskin.core.utils import remove_behavior
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from zope.interface import alsoProvides

import unittest


class TestBehaviors(unittest.TestCase):

    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.request, ICPSkinCoreLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder = api.content.create(self.portal, "Folder", "folder")
        self.document = api.content.create(self.folder, "Document", "document")
        self.collection = api.content.create(self.folder, "Collection", "collection")

    def test_use_slider_image_scale(self):
        add_behavior("Collection", ICpskinIndexViewSettings.__identifier__)
        slider_image_scale = getattr(self.collection, "slider_image_scale")
        self.assertEqual(slider_image_scale, "slider")
        remove_behavior("Collection", ICpskinIndexViewSettings.__identifier__)

    def test_use_carousel_image_scale(self):
        add_behavior("Collection", ICpskinIndexViewSettings.__identifier__)
        carousel_image_scale = getattr(self.collection, "carousel_image_scale")
        self.assertEqual(carousel_image_scale, "carousel")

    def test_use_link_text(self):
        add_behavior("Collection", ICpskinIndexViewSettings.__identifier__)
        link_text = getattr(self.collection, "link_text")
        self.assertEqual(link_text, "")

    def test_use_keyword_homepage(self):
        add_behavior("Collection", ICpskinIndexViewSettings.__identifier__)
        index_view_keywords = getattr(self.collection, "index_view_keywords")
        self.assertEqual(
            index_view_keywords, None, "Index view keyword is empty by default"
        )

    def test_related_contacts(self):
        add_behavior("Document", IRelatedContacts.__identifier__)
        aboveContentContact = getattr(self.document, "aboveContentContact")
        self.assertEqual(aboveContentContact, [])
        belowContentContact = getattr(self.document, "belowContentContact")
        self.assertFalse(belowContentContact)
        remove_behavior("Document", IRelatedContacts.__identifier__)

    def test_related_contacts_see_map(self):
        add_behavior("Document", IRelatedContacts.__identifier__)
        see_map = getattr(self.document, "see_map")
        self.assertTrue(see_map)
        setattr(self.document, "see_map", False)
        see_map = getattr(self.document, "see_map")
        self.assertFalse(see_map)
        remove_behavior("Document", IRelatedContacts.__identifier__)

    def test_related_contacts_see_logo_in_popup(self):
        add_behavior("Document", IRelatedContacts.__identifier__)
        see_logo_in_popup = getattr(self.document, "see_logo_in_popup")
        self.assertTrue(see_logo_in_popup)
        setattr(self.document, "see_logo_in_popup", False)
        see_logo_in_popup = getattr(self.document, "see_logo_in_popup")
        self.assertFalse(see_logo_in_popup)
        remove_behavior("Document", IRelatedContacts.__identifier__)

    def test_hidden_tags(self):
        add_behavior("Document", IHiddenTags.__identifier__)
        hiddenTags = getattr(self.document, "hiddenTags")
        self.assertEqual(hiddenTags, None)
        self.document.hiddenTags = ("mon-test",)
        self.document.reindexObject()
        hiddenTags = getattr(self.document, "hiddenTags")
        self.assertEqual(hiddenTags, ("mon-test",))
        catalog = api.portal.get_tool("portal_catalog")
        query = {"hiddenTags": "mon-test"}
        brains = catalog(query)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), self.document)

    def test_taxonomy_category(self):
        applyProfile(self.portal, "collective.taxonomy:default")
        add_behavior("Collection", ICpskinIndexViewSettings.__identifier__)
        test_taxonomy_category = getattr(self.collection, "taxonomy_category")
        self.assertEqual(test_taxonomy_category, "")

    def test_indexview_hide_title(self):
        add_behavior("Collection", ICpskinIndexViewSettings.__identifier__)
        hide_title = getattr(self.collection, "hide_title")
        self.assertEqual(hide_title, False)

    def test_additional_searchable_text(self):
        catalog = api.portal.get_tool("portal_catalog")
        add_behavior("Document", IAdditionalSearchableText.__identifier__)
        add_behavior("Document", IDexterityTextIndexer.__identifier__)
        additional_searchable_text = getattr(
            self.document, "additional_searchable_text"
        )
        self.assertEqual(additional_searchable_text, None)
        additional_searchable_text = setattr(
            self.document, "additional_searchable_text", "trash"
        )
        additional_searchable_text = getattr(
            self.document, "additional_searchable_text"
        )
        self.assertEqual(additional_searchable_text, "trash")

        # check that additional_searchable_text is correctly indexed
        # and that body text is still indexed
        richtextvalue = RichTextValue(
            u'richtext_value',
            'text/plain',
            'text/html'
        )
        self.document.text = richtextvalue
        self.document.reindexObject()

        brain = catalog(UID=self.document.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        searchable_text = indexes['SearchableText']
        self.assertTrue("trash" in searchable_text)
        self.assertTrue("document" in searchable_text)
        self.assertTrue("richtext_value" in searchable_text)
