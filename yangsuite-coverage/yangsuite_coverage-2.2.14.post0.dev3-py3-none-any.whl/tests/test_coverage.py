# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Test model coverage for a given CLI."""

import os
import unittest2 as unittest
from yscoverage.coverage import (
    generate_coverage,
    YangCoverage,
    YangCoverageException
)


class TestCoverage(unittest.TestCase):
    """Tests for model coverage."""

    testdir = os.path.join(os.path.dirname(__file__), 'data')

    def test_gen_no_text(self):
        """Raise an exception if no text is sent."""
        with self.assertRaises(YangCoverageException):
            generate_coverage()

    def test_gen_no_url(self):
        """Raise an exception if no URL is sent."""
        with self.assertRaises(YangCoverageException):
            generate_coverage(text='text')

    def test_get_config_bad_device(self):
        """Raise an exception if device is invalid."""
        with self.assertRaises(YangCoverageException):
            YangCoverage.get_config('blah')

    def test_get_local_releases(self):
        """Make sure dict is returned."""
        releases = YangCoverage.get_releases('xe')
        self.assertIn('releases', releases)

    def test_get_base_releases(self):
        """Make sure dict is returned."""
        releases = YangCoverage.get_releases("google.com")
        self.assertIn('releases', releases)

    def test_coverage_failed(self):
        """Only one coverage at a time allowed."""
        result = YangCoverage.get_coverage('text', 0, 'google.com')
        self.assertEqual(result, ('*** failed ***', ''))
