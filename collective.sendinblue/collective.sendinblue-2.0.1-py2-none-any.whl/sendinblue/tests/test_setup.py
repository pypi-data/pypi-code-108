# -*- coding: utf-8 -*-

from collective.sendinblue.testing import COLLECTIVE_SENDINBLUE_INTEGRATION_TESTING
import unittest


class TestSetup(unittest.TestCase):

    layer = COLLECTIVE_SENDINBLUE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_browserlayer_available(self):
        from plone.browserlayer import utils
        from collective.sendinblue.interfaces import ICollectiveSendinblueLayer
        self.failUnless(ICollectiveSendinblueLayer in utils.registered_layers())

    def test_sendinblue_css_available(self):
        css_url = '++resource++collective.sendinblue.stylesheets/sendinblue.css'
        self.assertIsNotNone(self.portal.restrictedTraverse(css_url))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
