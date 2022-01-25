# -*- coding: utf-8 -*-
"""Setup tests views of this package."""
from AccessControl import Unauthorized
from imio.gdpr.testing import IMIO_GDPR_INTEGRATION_TESTING
from plone import api
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue

import unittest


class TestGDPRView(unittest.TestCase):
    """Test that imio.gdpr is properly installed."""

    layer = IMIO_GDPR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

    def test_gdpr_default_view(self):
        """Test if imio.gdpr is installed."""
        view = api.content.get_view(
            name='gdpr-view',
            context=self.portal,
            request=self.portal.REQUEST,
        )
        content = view.content()
        self.assertTrue(content.startswith('<h2>'))  # noqa

    def test_gdpr_file_view(self):
        view = api.content.get_view(
            name='gdpr-view',
            context=self.portal,
            request=self.portal.REQUEST,
        )
        called_view = view()
        self.assertIn(u'<h2>D\xe9claration relative', called_view)  # noqa

        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        gdpr_file = api.content.create(
            type='Document',
            title='My Content',
            container=self.portal,
            id='mentions-legales',
            language='en'
        )
        rtv = RichTextValue('My New GDPR text')
        gdpr_file.text = rtv
        gdpr_file.reindexObject()
        setRoles(self.portal, TEST_USER_ID, roles_before)
        view = api.content.get_view(
            name='gdpr-view',
            context=self.portal,
            request=self.portal.REQUEST,
        )
        called_view = view()
        self.assertEqual(called_view, 'http://nohost/plone/mentions-legales')

    def test_control_panel_view(self):
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        view = api.content.get_view(
            name='gdpr-settings',
            context=self.portal,
            request=self.portal.REQUEST,
        )
        view = view.__of__(self.portal)
        self.assertTrue(view())
        self.assertTrue(u'administration communale' in view())
        setRoles(self.portal, TEST_USER_ID, roles_before)
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@gdpr-settings')
