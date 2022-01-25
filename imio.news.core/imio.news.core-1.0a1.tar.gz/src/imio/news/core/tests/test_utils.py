# -*- coding: utf-8 -*-

from imio.news.core.testing import IMIO_NEWS_CORE_INTEGRATION_TESTING
from imio.news.core.utils import get_news_folder_for_news_item
from imio.news.core.utils import get_news_folders_uids_for_faceted
from imio.news.core.utils import get_entity_for_obj
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestNewsFolder(unittest.TestCase):

    layer = IMIO_NEWS_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.authorized_types_in_news_folder = [
            "imio.news.Folder",
            "imio.news.NewsItem",
        ]
        self.unauthorized_types_in_news_folder = [
            "imio.news.NewsFolder",
            "Document",
            "File",
            "Image",
        ]

        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.parent = self.portal
        self.entity1 = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            id="entity1",
        )
        self.news_folder1 = api.content.create(
            container=self.entity1,
            type="imio.news.NewsFolder",
            id="news_folder1",
        )
        self.news1 = api.content.create(
            container=self.news_folder1,
            type="imio.news.NewsItem",
            id="news1",
        )
        self.entity2 = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            id="entity2",
        )
        self.news_folder2 = api.content.create(
            container=self.entity2,
            type="imio.news.NewsFolder",
            id="news_folder2",
        )
        self.news2 = api.content.create(
            container=self.news_folder2,
            type="imio.news.NewsItem",
            id="news2",
        )
        self.news_folder3 = api.content.create(
            container=self.entity1,
            type="imio.news.NewsFolder",
            id="news_folder3",
        )

    def test_get_entity_for_obj(self):
        self.assertEqual(get_entity_for_obj(self.entity1), self.entity1)
        self.assertEqual(get_entity_for_obj(self.news_folder1), self.entity1)
        self.assertEqual(get_entity_for_obj(self.news1), self.entity1)

    def test_get_news_folder_for_news_item(self):
        self.assertEqual(get_news_folder_for_news_item(self.news1), self.news_folder1)
        self.assertEqual(get_news_folder_for_news_item(self.news2), self.news_folder2)

    def test_get_news_folders_uids_for_faceted(self):
        with self.assertRaises(NotImplementedError):
            get_news_folders_uids_for_faceted(self.news1)
        self.assertEqual(
            get_news_folders_uids_for_faceted(self.news_folder1),
            [self.news_folder1.UID()],
        )
        self.assertEqual(
            get_news_folders_uids_for_faceted(self.entity1),
            [self.news_folder1.UID(), self.news_folder3.UID()],
        )
