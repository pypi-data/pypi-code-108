# -*- coding: utf-8 -*-
from cpskin.core.browser.folderview import configure_folderviews
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from cpskin.core.utils import add_behavior
from cpskin.core.utils import add_keyword
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter

import unittest


class TestKeywords(unittest.TestCase):

    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        configure_folderviews(self.portal)
        self.folder = api.content.create(self.portal, 'Folder', 'folder')

    def test_keyword_indexview_behavior(self):
        add_behavior(
            'Collection',
            'cpskin.core.behaviors.indexview.ICpskinIndexViewSettings')
        collection = api.content.create(
            container=self.folder,
            type='Collection',
            id='testcollection')
        self.assertEqual(getattr(collection, 'index_view_keywords'), None)
        collection.index_view_keywords = (u'homepage',)
        self.assertEqual(
            getattr(collection, 'index_view_keywords'), (u'homepage',))

    def test_folderview_without_keyword_homepage(self):
        add_behavior('News Item', 'cpskin.core.behaviors.metadata.IHiddenTags')
        view = getMultiAdapter((self.portal, self.request), name='folderview')
        result = view.getResults(self.portal.actualites.actualites)
        self.assertTrue(result is None)

        # Adding content for fill collection
        news = api.content.create(
            container=self.portal.actualites,
            type='News Item',
            id='testnewsitem')
        api.content.transition(obj=news, transition='publish')
        result = view.getResults(self.portal.actualites.actualites)
        self.assertEqual(len(result.get('standard-results', 0)), 1)

        add_keyword(news, 'hiddenTags', ['homepage'])
        add_keyword(news, 'hiddenTags', ['non-homepage'])

        result = view.getResults(self.portal.actualites.actualites)
        self.assertEqual(len(result.get('standard-results', 0)), 1)

    def test_folderview_with_keyword_homepage(self):
        add_behavior(
            'Collection',
            'cpskin.core.behaviors.indexview.ICpskinIndexViewSettings')
        add_behavior('News Item', 'cpskin.core.behaviors.metadata.IHiddenTags')
        self.portal.actualites.actualites.index_view_keywords = (u'homepage',)
        view = getMultiAdapter((self.portal, self.request), name='folderview')
        news = api.content.create(
            container=self.portal.actualites,
            type='News Item',
            id='testnewsitem')
        api.content.transition(obj=news, transition='publish')
        result = view.getResults(self.portal.actualites.actualites)
        self.assertTrue(result is None)

        add_keyword(news, 'hiddenTags', ['non-homepage'])
        result = view.getResults(self.portal.actualites.actualites)
        self.assertTrue(result is None)

        add_keyword(news, 'hiddenTags', ['homepage'])
        result = view.getResults(self.portal.actualites.actualites)
        self.assertEqual(len(result.get('standard-results', 0)), 1)
