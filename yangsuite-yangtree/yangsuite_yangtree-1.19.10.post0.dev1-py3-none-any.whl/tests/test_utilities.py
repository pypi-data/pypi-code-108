# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Test cases for ysyangtree.utilities module."""

import unittest2 as unittest

from ysyangtree.utilities import xpath_iterator, XPathInvalidError


class TestXPathIterator(unittest.TestCase):
    """Test cases for the xpath_iterator() function."""

    def test_xpath_iterator_negative(self):
        """Negative (input validation) tests for xpath_iterator()."""
        paths = [
            # Path must be absolute, not relative
            "a/relative/path",
            # Missing segment between //
            "/openconfig-interfaces:interfaces//name",
            # Trailing slash
            "/openconfig-interfaces:interfaces/",
            # Need at least one segment
            "/",
            # Prefix with empty localname
            "/openconfig-interfaces:/interface",
            # Localname with empty prefix
            "/:interfaces/interface",
            # Extra : separator
            "/openconfig-interfaces::interfaces/interface",
            # Malformed list key predicate
            "/openconfig-interfaces:interfaces/interface[foo",
        ]
        for path in paths:
            with self.assertRaises(XPathInvalidError):
                for _ in xpath_iterator(path):
                    pass

    # xpath_iterator positive test is implemented as a doctest
