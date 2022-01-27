#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_deployv-static
----------------------------------

Tests for `deployv-static` module.
"""

import deployv_static
import unittest
from os.path import isfile


class TestDeployv_static(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_path(self):
        self.assertTrue(isfile(deployv_static.get_template_path('dev_instances.jinja')))

    def test_exception(self):
        with self.assertRaises(IOError):
            deployv_static.get_template_path('nonexistingtemplate.jinja')

    def tearDown(self):
        pass
