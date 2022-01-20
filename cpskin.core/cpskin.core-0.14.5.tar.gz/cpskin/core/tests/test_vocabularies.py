# -*- coding: utf-8 -*-
from collective.geo.behaviour.interfaces import ICoordinates
from cpskin.core.behaviors.metadata import IHiddenTags
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from cpskin.core.utils import add_behavior
from cpskin.core.utils import remove_behavior
from cpskin.core.utils import set_exclude_from_nav
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestVocabularies(unittest.TestCase):

    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_contact_fields_vocabulary(self):
        applyProfile(self.portal, 'collective.contact.core:default')
        name = 'cpskin.core.vocabularies.contact_fields'
        factory = getUtility(IVocabularyFactory, name)
        vocabulary = factory(self.portal)
        keys = vocabulary.by_value.keys()
        self.assertNotIn('im_handle', keys)
        self.assertIn('street', keys)
        self.assertIn('number', keys)
        self.assertIn('zip_code', keys)
        self.assertIn('city', keys)
        self.assertIn('activity', keys)
        self.assertIn('title', keys)
        titles = [val.title for val in vocabulary.by_value.values()]
        self.assertIn(u'Contact details: Email', titles)

    def test_hidden_tags_vocabulary(self):
        name = 'cpskin.core.vocabularies.hiddenTags'
        factory = getUtility(IVocabularyFactory, name)
        vocabulary = factory(self.portal)
        keys = vocabulary.by_value.keys()
        self.assertEqual(keys, [u'a-la-une', u'homepage'])
        add_behavior('Document', IHiddenTags.__identifier__)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(container=self.portal,
                           type='Document', title='document')
        document = self.portal.document
        document.hiddenTags = [u'mot clé caché']
        document.reindexObject()
        vocabulary = factory(self.portal)
        keys = vocabulary.by_value.keys()
        self.assertEqual(
            keys, [u'mot cl\xe9 cach\xe9', u'a-la-une', u'homepage'])

    def test_geo_types_vocabulary(self):
        name = 'cpskin.core.vocabularies.geo_types'
        factory = getUtility(IVocabularyFactory, name)
        vocabulary = factory(self.portal)
        keys = vocabulary.by_value.keys()
        self.assertEqual(len(keys), 0)
        add_behavior('Document', ICoordinates.__identifier__)

        vocabulary = factory(self.portal)
        keys = vocabulary.by_value.keys()
        self.assertEqual(len(keys), 1)
        self.assertIn(u'Document', keys)

        remove_behavior('Document', ICoordinates.__identifier__)

    def test_action_menu_eligible_vocabulary(self):
        name = 'cpskin.core.vocabularies.action_menu_eligible'
        factory = getUtility(IVocabularyFactory, name)
        vocabulary = factory(self.portal)
        orig_keys = vocabulary.by_value.keys()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        testfolder = api.content.create(container=self.portal,
                                        type='Folder', title='testfolder')
        api.content.transition(obj=testfolder, transition='publish')
        vocabulary = factory(self.portal)
        keys = vocabulary.by_value.keys()
        self.assertEqual(len(keys), len(orig_keys))
        api.content.create(container=self.portal,
                           type='Document', title='testdocument')
        vocabulary = factory(self.portal)
        keys = vocabulary.by_value.keys()
        self.assertEqual(len(keys), len(orig_keys))
        set_exclude_from_nav(testfolder)
        testfolder.reindexObject()
        vocabulary = factory(self.portal)
        keys = vocabulary.by_value.keys()
        self.assertEqual(len(keys), len(orig_keys) + 1)
