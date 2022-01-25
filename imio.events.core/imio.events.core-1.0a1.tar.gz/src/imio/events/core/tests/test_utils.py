# -*- coding: utf-8 -*-

from imio.events.core.testing import IMIO_EVENTS_CORE_INTEGRATION_TESTING
from imio.events.core.utils import get_agenda_for_event
from imio.events.core.utils import get_agendas_uids_for_faceted
from imio.events.core.utils import get_entity_for_obj
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestAgenda(unittest.TestCase):

    layer = IMIO_EVENTS_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.authorized_types_in_agenda = [
            "imio.events.Folder",
            "imio.events.Event",
        ]
        self.unauthorized_types_in_agenda = [
            "imio.events.Agenda",
            "Document",
            "File",
            "Image",
        ]

        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.parent = self.portal
        self.entity1 = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            id="entity1",
        )
        self.agenda1 = api.content.create(
            container=self.entity1,
            type="imio.events.Agenda",
            id="agenda1",
        )
        self.event1 = api.content.create(
            container=self.agenda1,
            type="imio.events.Event",
            id="event1",
        )
        self.entity2 = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            id="entity2",
        )
        self.agenda2 = api.content.create(
            container=self.entity2,
            type="imio.events.Agenda",
            id="agenda2",
        )
        self.event2 = api.content.create(
            container=self.agenda2,
            type="imio.events.Event",
            id="event2",
        )
        self.agenda3 = api.content.create(
            container=self.entity1,
            type="imio.events.Agenda",
            id="agenda3",
        )

    def test_get_entity_for_obj(self):
        self.assertEqual(get_entity_for_obj(self.entity1), self.entity1)
        self.assertEqual(get_entity_for_obj(self.agenda1), self.entity1)
        self.assertEqual(get_entity_for_obj(self.event1), self.entity1)

    def test_get_agenda_for_event(self):
        self.assertEqual(get_agenda_for_event(self.event1), self.agenda1)
        self.assertEqual(get_agenda_for_event(self.event2), self.agenda2)

    def test_get_agendas_uids_for_faceted(self):
        with self.assertRaises(NotImplementedError):
            get_agendas_uids_for_faceted(self.event1)
        self.assertEqual(
            get_agendas_uids_for_faceted(self.agenda1), [self.agenda1.UID()]
        )
        self.assertEqual(
            get_agendas_uids_for_faceted(self.entity1),
            [self.agenda1.UID(), self.agenda3.UID()],
        )
