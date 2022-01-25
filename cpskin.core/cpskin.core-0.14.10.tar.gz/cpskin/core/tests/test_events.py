# -*- coding: utf-8 -*-
from collective.geo.behaviour.interfaces import ICoordinates
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from cpskin.core.utils import add_behavior
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


class TestEvents(unittest.TestCase):

    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_modified_orga_events(self):
        # add some contacts
        applyProfile(self.portal, 'collective.contact.core:default')
        add_behavior('organization', ICoordinates.__identifier__)
        directory = api.content.create(
            container=self.portal, type='directory', id='directory')
        orga = api.content.create(
            container=directory, type='organization', id='orga')
        orga.use_parent_address = False
        orga.street = u'Rue Léon Morel'
        orga.number = u'1'
        # notify(ObjectAddedEvent(orga))
        coord = ICoordinates(orga).coordinates
        self.assertFalse(coord.startswith('POINT '))
        orga.zip_code = u'5032'
        orga.city = u'Isnes'
        notify(ObjectModifiedEvent(orga))
        coord = ICoordinates(orga).coordinates
        self.assertTrue(coord.startswith('POINT '))
