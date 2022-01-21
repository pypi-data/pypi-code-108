# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest

import fixtures

from arbiterd_tests import base

LOG = logging.getLogger(__name__)


class TestPytest(unittest.TestCase):

    def test_framework_is_working(self):
        self.assertTrue(True)

    def test_import_worked(self):
        import arbiterd
        self.assertIsNotNone(arbiterd)


class TestATTestCase(base.ATTestCase):

    def test_fixture_are_present(self):
        for fixture in ('sys_fixture', 'log_fixture'):
            self.assertTrue(hasattr(self, fixture))
            fixture_obj = getattr(self, fixture)
            self.assertIsNotNone(fixture_obj)
            self.assertIsInstance(fixture_obj, fixtures.Fixture)

    def test_logging_is_captured(self):
        message = 'this is a test of error logging'
        # default logging configuration of the fixture is to log Info and above
        # so we are just using error so that we know it will be printed.
        LOG.error(message)
        self.assertIn(message, self.log_fixture.output)
        message = 'this should not be logged'
        LOG.debug(message)
        self.assertNotIn(message, self.log_fixture.output)

    def test_logging_at_debug_can_be_enabled(self):

        self.replace_log_fixture(logging.DEBUG)
        message = 'this is a test of debug logging'
        LOG.debug(message)
        self.assertIn(message, self.log_fixture.output)
