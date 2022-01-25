# -*- coding: utf-8 -*-

from imio.events.core.testing import IMIO_EVENTS_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestVocabularies(unittest.TestCase):

    layer = IMIO_EVENTS_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_news_categories(self):
        factory = getUtility(
            IVocabularyFactory, "imio.events.vocabulary.EventsCategories"
        )
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 10)

    def test_events_local_categories_on_root(self):
        factory = getUtility(
            IVocabularyFactory, "imio.events.vocabulary.EventsLocalCategories"
        )
        vocabulary = factory(self.portal)
        self.assertEqual(len(vocabulary), 0)

    def test_event_categories_topics(self):
        entity = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            id="imio.events.Entity",
            local_categories="",
        )

        factory = getUtility(
            IVocabularyFactory,
            "imio.events.vocabulary.EventsCategoriesAndTopicsVocabulary",
        )
        vocabulary = factory(entity)
        self.assertEqual(len(vocabulary), 27)  # must be updated if add new vocabulary

    def test_news_categories_topics_local_cat(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        entity = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            id="imio.events.Entity",
            local_categories="Foo\r\nbaz\r\nbar",
        )
        agenda = api.content.create(
            container=entity,
            type="imio.events.Agenda",
            id="imio.events.Agenda",
        )
        event_item = api.content.create(
            container=agenda,
            type="imio.events.Event",
            id="imio.events.Event",
        )

        factory = getUtility(
            IVocabularyFactory,
            "imio.events.vocabulary.EventsCategoriesAndTopicsVocabulary",
        )
        vocabulary = factory(event_item)
        self.assertEqual(len(vocabulary), 30)  # must be updated if add new vocabulary

    def test_agendas_UIDs(self):
        entity1 = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            title="Entity1",
        )
        entity2 = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            title="Entity2",
        )
        agenda1 = api.content.create(
            container=entity1,
            type="imio.events.Agenda",
            title="Agenda1",
        )
        agenda2 = api.content.create(
            container=entity2,
            type="imio.events.Agenda",
            title="Agenda2",
        )
        folder = api.content.create(
            container=agenda1,
            type="imio.events.Folder",
            title="Folder",
        )
        event1 = api.content.create(
            container=folder,
            type="imio.events.Event",
            title="Event1",
        )
        event2 = api.content.create(
            container=agenda2,
            type="imio.events.Event",
            title="Event2",
        )
        factory = getUtility(IVocabularyFactory, "imio.events.vocabulary.AgendasUIDs")
        vocabulary = factory(self.portal)
        self.assertEqual(len(vocabulary), 2)

        vocabulary = factory(event1)
        self.assertEqual(len(vocabulary), 2)

        vocabulary = factory(event2)
        uid = agenda2.UID()
        vocabulary.getTerm(uid)
        self.assertEqual(vocabulary.getTerm(uid).title, "Entity2 » Agenda2")

        vocabulary = factory(self.portal)
        ordered_agendas = [a.title for a in vocabulary]
        self.assertEqual(ordered_agendas, ["Entity1 » Agenda1", "Entity2 » Agenda2"])
        entity1.title = "Z Change order!"
        agenda1.reindexObject()
        vocabulary = factory(self.portal)
        ordered_agendas = [a.title for a in vocabulary]
        self.assertEqual(
            ordered_agendas, ["Entity2 » Agenda2", "Z Change order! » Agenda1"]
        )

    def test_event_types(self):
        factory = getUtility(IVocabularyFactory, "imio.events.vocabulary.EventTypes")
        vocabulary = factory(self.portal)
        self.assertEqual(len(vocabulary), 2)
