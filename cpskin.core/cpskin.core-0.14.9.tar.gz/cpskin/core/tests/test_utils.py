# -*- coding: utf-8 -*-
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from cpskin.core.utils import format_phone
from cpskin.core.utils import set_plonecustom_last
from plone import api

import unittest


class TestTools(unittest.TestCase):

    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_plonecustom_to_last(self):
        portal_css = api.portal.get_tool('portal_css')
        resources = list(portal_css.resources)
        self.assertFalse(resources[-1].getId() == 'ploneCustom.css')
        set_plonecustom_last()
        resources = list(portal_css.resources)
        self.assertTrue(resources[-1].getId() == 'ploneCustom.css')

    def test_format_phone(self):
        good_phone = '+32 (0) 65 32 96 77'
        formated_phone = format_phone('065/32.96.77').get('formated')
        self.assertEqual(formated_phone, good_phone)

        formated_phone = format_phone('65329677').get('formated')
        self.assertEqual(formated_phone, good_phone)

        formated_phone = format_phone('003265/32.96.77').get('formated')
        self.assertEqual(formated_phone, good_phone)

        formated_phone = format_phone('+3265329677').get('formated')
        self.assertEqual(formated_phone, good_phone)
