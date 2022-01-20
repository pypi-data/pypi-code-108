# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from rer.sitesearch.testing import RER_SITESEARCH_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that rer.sitesearch is properly installed."""

    layer = RER_SITESEARCH_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if rer.sitesearch is installed."""
        self.assertTrue(self.installer.isProductInstalled("rer.sitesearch"))

    def test_browserlayer(self):
        """Test that IRERSiteSearchLayer is registered."""
        from rer.sitesearch.interfaces import IRERSiteSearchLayer
        from plone.browserlayer import utils

        self.assertIn(IRERSiteSearchLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = RER_SITESEARCH_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["rer.sitesearch"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if rer.sitesearch is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled("rer.sitesearch"))

    def test_browserlayer_removed(self):
        """Test that IRERSiteSearchLayer is removed."""
        from rer.sitesearch.interfaces import IRERSiteSearchLayer
        from plone.browserlayer import utils

        self.assertNotIn(IRERSiteSearchLayer, utils.registered_layers())
