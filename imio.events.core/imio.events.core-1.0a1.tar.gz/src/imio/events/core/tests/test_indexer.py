# -*- coding: utf-8 -*-

from imio.events.core.testing import IMIO_EVENTS_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestIndexer(unittest.TestCase):

    layer = IMIO_EVENTS_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_catalog = api.portal.get_tool("portal_catalog")

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            id="imio.events.Entity",
            local_categories="Foo\r\nbaz\r\nbar",
        )
        self.agenda = api.content.create(
            container=self.entity,
            type="imio.events.Agenda",
            id="imio.events.Agenda",
        )

    def _search_all_from_vocabulary(self, vocabulary, context, catalog):
        factory = getUtility(
            IVocabularyFactory,
            vocabulary,
        )
        output = {}
        vocabulary = factory(context)
        for v in vocabulary.by_value:
            result = catalog.searchResults(**{"category_and_topics": v})
            if len(result) == 0:
                continue
            output[v] = [r.getObject().id for r in result]

        return output

    def test_event_with_nothing(self):
        api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            id="imio.events.Event",
        )
        search_result = self._search_all_from_vocabulary(
            "imio.events.vocabulary.EventsCategoriesAndTopicsVocabulary",
            self.agenda,
            self.portal_catalog,
        )

        self.assertEqual(len(search_result), 0)

    def test_event_with_one_of_each(self):
        api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            id="id_news",
            category=u"stroll_discovery",
            local_category=u"Foo",
            topics=[u"culture", u"health"],
        )

        api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            id="id_news2",
            category=u"theater_show",
            local_category=u"baz",
            topics=[u"tourism", u"health"],
        )

        search_result = self._search_all_from_vocabulary(
            "imio.events.vocabulary.EventsCategoriesAndTopicsVocabulary",
            self.agenda,
            self.portal_catalog,
        )

        # check if right number of result
        self.assertEqual(len(search_result), 7)

        # check for good result number
        self.assertEqual(len(search_result["stroll_discovery"]), 1)
        self.assertEqual(len(search_result["Foo"]), 1)
        self.assertEqual(len(search_result["baz"]), 1)
        self.assertEqual(len(search_result["culture"]), 1)
        self.assertEqual(len(search_result["health"]), 2)
        self.assertEqual(len(search_result["theater_show"]), 1)
        self.assertEqual(len(search_result["tourism"]), 1)

        # check for good return object
        self.assertEqual(search_result["stroll_discovery"], ["id_news"])
        self.assertEqual(search_result["Foo"], ["id_news"])
        self.assertEqual(search_result["baz"], ["id_news2"])
        self.assertEqual(search_result["culture"], ["id_news"])
        self.assertEqual(sorted(search_result["health"]), ["id_news", "id_news2"])
        self.assertEqual(search_result["theater_show"], ["id_news2"])
        self.assertEqual(search_result["tourism"], ["id_news2"])
