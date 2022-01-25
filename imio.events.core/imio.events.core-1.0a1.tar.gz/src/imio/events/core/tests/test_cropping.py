# -*- coding: utf-8 -*-

from imio.events.core.testing import IMIO_EVENTS_CORE_INTEGRATION_TESTING
from imio.smartweb.common.interfaces import ICropping
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.component import getMultiAdapter

import unittest


class TestCropping(unittest.TestCase):

    layer = IMIO_EVENTS_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            title="Entity",
        )
        self.agenda = api.content.create(
            container=self.entity,
            type="imio.events.Agenda",
            title="Folder",
        )
        self.event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="News",
        )

    def test_cropping_adapter(self):
        adapter = ICropping(self.event, alternate=None)
        self.assertIsNotNone(adapter)
        self.assertEqual(
            adapter.get_scales("image", self.request),
            ["vignette", "slide", "affiche"],
        )

    def test_cropping_view(self):
        cropping_view = getMultiAdapter(
            (self.event, self.request), name="croppingeditor"
        )
        self.assertEqual(len(list(cropping_view._scales("image"))), 3)
