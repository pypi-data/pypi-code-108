# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from imio.gdpr.interfaces import IGDPRSettings
from imio.gdpr.interfaces import IImioGdprLayer
from imio.gdpr.testing import IMIO_GDPR_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestSetup(unittest.TestCase):
    """Test that imio.gdpr is properly installed."""

    layer = IMIO_GDPR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if imio.gdpr is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'imio.gdpr'))

    def test_browserlayer(self):
        """Test that IImioGdprLayer is registered."""
        from plone.browserlayer import utils
        self.assertIn(
            IImioGdprLayer,
            utils.registered_layers())

    def test_default_values(self):
        record = api.portal.get_registry_record(
            'text',
            interface=IGDPRSettings
        )
        self.assertIn(u'<h2>D\xe9claration relative', record)

        record = api.portal.get_registry_record(
            'cookies_text',
            interface=IGDPRSettings
        )
        self.assertIn(u"<h1>Politique d'utilisation des cookies", record)


class TestUninstall(unittest.TestCase):

    layer = IMIO_GDPR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['imio.gdpr'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if imio.gdpr is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'imio.gdpr'))

    def test_browserlayer_removed(self):
        """Test that IImioGdprLayer is removed."""
        from plone.browserlayer import utils
        self.assertNotIn(
            IImioGdprLayer,
            utils.registered_layers())
