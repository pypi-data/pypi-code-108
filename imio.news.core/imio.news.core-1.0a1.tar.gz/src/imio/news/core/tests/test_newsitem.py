# -*- coding: utf-8 -*-

from imio.news.core.contents import INewsItem
from imio.news.core.interfaces import IImioNewsCoreLayer
from imio.news.core.testing import IMIO_NEWS_CORE_FUNCTIONAL_TESTING
from imio.news.core.tests.utils import get_leadimage_filename
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.file import NamedBlobFile
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IRelationList
from zope.component import createObject
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import modified
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestNewsItem(unittest.TestCase):

    layer = IMIO_NEWS_CORE_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.authorized_types_in_newsitem = ["File", "Image"]

        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            title="Entity",
        )
        self.entity = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            title="Entity",
        )
        self.news_folder = api.content.create(
            container=self.entity,
            type="imio.news.NewsFolder",
            title="News folder",
        )

    def test_ct_newsitem_schema(self):
        fti = queryUtility(IDexterityFTI, name="imio.news.NewsItem")
        schema = fti.lookupSchema()
        self.assertEqual(INewsItem, schema)

    def test_ct_newsitem_fti(self):
        fti = queryUtility(IDexterityFTI, name="imio.news.NewsItem")
        self.assertTrue(fti)

    def test_ct_newsitem_factory(self):
        fti = queryUtility(IDexterityFTI, name="imio.news.NewsItem")
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            INewsItem.providedBy(obj),
            u"INewsItem not provided by {0}!".format(
                obj,
            ),
        )

    def test_news_local_category(self):
        news = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            id="my-news",
        )
        factory = getUtility(
            IVocabularyFactory, "imio.news.vocabulary.NewsLocalCategories"
        )
        vocabulary = factory(news)
        self.assertEqual(len(vocabulary), 0)

        self.entity.local_categories = "First\nSecond\nThird"
        vocabulary = factory(news)
        self.assertEqual(len(vocabulary), 3)

    def test_view(self):
        newsitem = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="My news item",
        )
        view = queryMultiAdapter((newsitem, self.request), name="view")
        self.assertIn("My news item", view())

    def test_embed_video(self):
        newsitem = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="My news item",
        )
        newsitem.video_url = "https://www.youtube.com/watch?v=_dOAthafoGQ"
        view = queryMultiAdapter((newsitem, self.request), name="view")
        embedded_video = view.get_embed_video()
        self.assertIn("iframe", embedded_video)
        self.assertIn(
            "https://www.youtube.com/embed/_dOAthafoGQ?feature=oembed", embedded_video
        )

    def test_has_leadimage(self):
        newsitem = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="My news item",
        )
        view = queryMultiAdapter((newsitem, self.request), name="view")
        self.assertEqual(view.has_leadimage(), False)
        newsitem.image = NamedBlobFile(
            "ploneLeadImage", filename=get_leadimage_filename()
        )
        self.assertEqual(view.has_leadimage(), True)

    def test_subscriber_to_select_current_news_folder(self):
        news_item = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="My news item",
        )
        self.assertEqual(news_item.selected_news_folders, [self.news_folder.UID()])

    def test_indexes(self):
        news_item1 = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="NewsItem1",
        )
        news_folder2 = api.content.create(
            container=self.entity,
            type="imio.news.NewsFolder",
            title="NewsFolder2",
        )
        news_item2 = api.content.create(
            container=news_folder2,
            type="imio.news.NewsItem",
            title="NewsItem2",
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=news_item1.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("container_uid"), self.news_folder.UID())

        # On va requêter sur self.news_folder et trouver les 2 événements car news_item2 vient de s'ajouter dedans aussi.
        news_item2.selected_news_folders = [self.news_folder.UID()]
        news_item2.reindexObject()
        brains = api.content.find(selected_news_folders=self.news_folder.UID())
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [news_item1.UID(), news_item2.UID()])

        # On va requêter sur news_folder2 et trouver uniquement news_item2 car news_item2 est dans les 2 news folders mais news_item1 n'est que dans self.news_folder
        news_item2.selected_news_folders = [news_folder2.UID(), self.news_folder.UID()]
        news_item2.reindexObject()
        brains = api.content.find(selected_news_folders=news_folder2.UID())
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [news_item2.UID()])

        # Via une recherche catalog sur les news_folder, on va trouver les 2 événements
        brains = api.content.find(
            selected_news_folders=[news_folder2.UID(), self.news_folder.UID()]
        )
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [news_item1.UID(), news_item2.UID()])

        # On va requêter sur les 2 news folders et trouver les 2 événements car 1 dans chaque
        news_item2.selected_news_folders = [news_folder2.UID()]
        news_item2.reindexObject()
        brains = api.content.find(
            selected_news_folders=[news_folder2.UID(), self.news_folder.UID()]
        )
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [news_item1.UID(), news_item2.UID()])

        api.content.move(news_item1, news_folder2)
        brain = api.content.find(UID=news_item1.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("container_uid"), news_folder2.UID())

    def test_searchable_text(self):
        news_item = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="Title",
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=news_item.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("SearchableText"), ["title"])

        news_item.description = "Description"
        news_item.topics = ["agriculture"]
        news_item.category = "works"
        news_item.text = RichTextValue("<p>Text</p>", "text/html", "text/html")
        news_item.reindexObject()

        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=news_item.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("SearchableText"),
            [
                "title",
                "description",
                "text",
                "agriculture",
                "travaux",
            ],
        )

    def test_category_title_index(self):
        news_item = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="Title",
        )
        news_item.category = "works"
        news_item.reindexObject()
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=news_item.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("category_title"), "Travaux")

    def test_referrer_newsfolders(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        intids = getUtility(IIntIds)
        entity2 = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            id="entity2",
        )
        newsfolder2 = api.content.create(
            container=entity2,
            type="imio.news.NewsFolder",
            id="newsfolder2",
        )
        newsitem2 = api.content.create(
            container=newsfolder2,
            type="imio.news.NewsItem",
            id="newsitem2",
        )
        setattr(
            self.news_folder,
            "populating_newsfolders",
            [RelationValue(intids.getId(newsfolder2))],
        )
        modified(self.news_folder, Attributes(IRelationList, "populating_newsfolders"))
        self.assertIn(self.news_folder.UID(), newsitem2.selected_news_folders)

        # if we create an newsitem in an newsfolder that is referred in another newsfolder
        # then, referrer newsfolder UID is in newsitem.selected_news_folders list.
        newsitem2b = api.content.create(
            container=newsfolder2,
            type="imio.news.NewsItem",
            id="newsitem2b",
        )
        self.assertIn(self.news_folder.UID(), newsitem2b.selected_news_folders)

    def test_automaticaly_readd_container_newsfolder_uid(self):
        newsitem = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            id="newsitem",
        )
        self.assertIn(self.news_folder.UID(), newsitem.selected_news_folders)
        newsitem.selected_news_folders = []
        newsitem.reindexObject()
        modified(newsitem)
        self.assertIn(self.news_folder.UID(), newsitem.selected_news_folders)

    def test_name_chooser(self):
        news = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="news",
        )
        self.assertEqual(news.id, news.UID())

        entity = api.content.create(
            container=self.portal,
            type="imio.news.Entity",
            title="my-entity",
        )
        self.assertNotEqual(entity.id, entity.UID())
        self.assertEqual(entity.id, "my-entity")

    def test_js_bundles(self):
        newsitem = api.content.create(
            container=self.news_folder,
            type="imio.news.NewsItem",
            title="NewsItem",
        )

        alsoProvides(self.request, IImioNewsCoreLayer)
        getMultiAdapter((newsitem, self.request), name="view")()
        bundles = getattr(self.request, "enabled_bundles", [])
        self.assertEqual(len(bundles), 0)
        api.content.create(
            container=newsitem,
            type="Image",
            title="Image",
        )
        getMultiAdapter((newsitem, self.request), name="view")()
        bundles = getattr(self.request, "enabled_bundles", [])
        self.assertEqual(len(bundles), 2)
        self.assertListEqual(bundles, ["spotlightjs", "flexbin"])
