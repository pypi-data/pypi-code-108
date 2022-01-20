import unittest2 as unittest

from plone.app.testing import applyProfile

from cpskin.theme.testing import CPSKIN_THEME_INTEGRATION_TESTING


class TestProfiles(unittest.TestCase):

    layer = CPSKIN_THEME_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_installation(self):
        portal = self.layer['portal']
        applyProfile(portal, 'cpskin.theme:uninstall')
        applyProfile(portal, 'cpskin.theme:default')
