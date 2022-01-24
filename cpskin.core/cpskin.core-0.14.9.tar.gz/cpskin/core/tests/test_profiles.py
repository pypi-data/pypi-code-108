# -*- coding: utf-8 -*-
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from plone.app.testing import applyProfile

import unittest


class TestProfiles(unittest.TestCase):

    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_uninstall(self):
        applyProfile(self.portal, 'cpskin.core:uninstall')

    def test_reinstall(self):
        applyProfile(self.portal, 'cpskin.core:uninstall')
        applyProfile(self.portal, 'cpskin.core:default')
