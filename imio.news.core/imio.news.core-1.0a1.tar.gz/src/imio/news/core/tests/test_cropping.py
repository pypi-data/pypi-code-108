# -*- coding: utf-8 -*-

from imio.news.core.testing import IMIO_NEWS_CORE_INTEGRATION_TESTING
from imio.smartweb.common.interfaces import ICropping
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.component import getMultiAdapter

import unittest


class TestCropping(unittest.TestCase):

    layer = IMIO_NEWS_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            title="Entity",
        )
        self.news_folder = api.content.create(
            container=self.entity,
            type="imio.news.NewsFolder",
            title="Folder",
        )
        self.news = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="News",
        )

    def test_cropping_adapter(self):
        adapter = ICropping(self.news, alternate=None)
        self.assertIsNotNone(adapter)
        self.assertEqual(
            adapter.get_scales("image", self.request),
            ["vignette", "slide", "affiche"],
        )

    def test_cropping_view(self):
        cropping_view = getMultiAdapter(
            (self.news, self.request), name="croppingeditor"
        )
        self.assertEqual(len(list(cropping_view._scales("image"))), 3)
