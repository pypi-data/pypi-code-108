# -*- coding: utf-8 -*-

from imio.events.core.contents.entity.content import IEntity  # NOQA E501
from imio.events.core.testing import IMIO_EVENTS_CORE_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class TestEntity(unittest.TestCase):

    layer = IMIO_EVENTS_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.authorized_types_in_entity = [
            "imio.events.Agenda",
        ]
        self.unauthorized_types_in_entity = [
            "imio.events.Entity",
            "imio.events.Folder",
            "imio.events.Event",
            "Document",
            "File",
            "Image",
        ]

        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.parent = self.portal

    def test_ct_entity_schema(self):
        fti = queryUtility(IDexterityFTI, name="imio.events.Entity")
        schema = fti.lookupSchema()
        self.assertEqual(IEntity, schema)

    def test_ct_entity_fti(self):
        fti = queryUtility(IDexterityFTI, name="imio.events.Entity")
        self.assertTrue(fti)

    def test_ct_entity_factory(self):
        fti = queryUtility(IDexterityFTI, name="imio.events.Entity")
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IEntity.providedBy(obj),
            u"IEntity not provided by {0}!".format(
                obj,
            ),
        )

    def test_ct_entity_adding(self):
        obj = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            id="imio.events.Entity",
        )

        self.assertTrue(
            IEntity.providedBy(obj),
            u"IEntity not provided by {0}!".format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn("imio.events.Entity", parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn("imio.events.Entity", parent.objectIds())

    def test_ct_entity_globally_addable(self):
        fti = queryUtility(IDexterityFTI, name="imio.events.Entity")
        self.assertTrue(
            fti.global_allow, u"{0} is not globally addable!".format(fti.id)
        )

    def test_ct_entity_filter_content_type_true(self):
        fti = queryUtility(IDexterityFTI, name="imio.events.Entity")
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            "imio.events.Entity_id",
            title="imio.events.Entity container",
        )
        folder = self.portal[parent_id]
        for t in self.unauthorized_types_in_entity:
            with self.assertRaises(InvalidParameterError):
                api.content.create(
                    container=folder,
                    type=t,
                    title="My {}".format(t),
                )
        for t in self.authorized_types_in_entity:
            api.content.create(
                container=folder,
                type=t,
                title="My {}".format(t),
            )
