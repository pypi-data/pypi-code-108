# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from .test_base import TestYSYangSetBase
from ..dir_repository import YSYangDirectoryRepository


class TestYSYangDirectoryRepository(TestYSYangSetBase):
    """Tests for the YSYangDirectoryRepository class."""

    cls = YSYangDirectoryRepository

    def test_repository(self):
        """Verify that it includes all files in the dir."""
        ys = self.cls(self.test_dir, owner='test')
        self.assertEqual('test', ys.owner)
        self.assertIsNone(ys.datastore_mtime)
        self.assertFalse(ys.is_stale)

        # NOTE: because this just lists .yang files in the directory,
        #       it includes the Cisco-IOS-XR-lib-keychain-act file
        #       that pyang is actually unable to parse.
        mods = ys.get_modules_and_revisions()
        self.assertIsInstance(mods, list)
        self.assertEqual([
            ("Cisco-IOS-XR-ipv4-bgp-datatypes", "2015-08-27",
             os.path.join(self.test_dir,
                          "Cisco-IOS-XR-ipv4-bgp-datatypes@2015-08-27.yang")),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper", "2015-11-09",
             os.path.join(self.test_dir,
                          "Cisco-IOS-XR-ipv4-bgp-oc-oper@2015-11-09.yang")),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1", "2015-11-09",
             os.path.join(
                 self.test_dir,
                 "Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1@2015-11-09.yang")),
            ("Cisco-IOS-XR-lib-keychain-act", "2017-04-17",
             os.path.join(self.test_dir,
                          "Cisco-IOS-XR-lib-keychain-act@2017-04-17.yang")),
            ('Cisco-IOS-XR-lib-keychain-cfg', '2015-07-30',
             os.path.join(self.test_dir,
                          'Cisco-IOS-XR-lib-keychain-cfg@2015-07-30.yang')),
            ("Cisco-IOS-XR-types", "2015-06-29",
             os.path.join(self.test_dir,
                          "Cisco-IOS-XR-types@2015-06-29.yang")),
            ("iana-if-type", "2015-06-12",
             os.path.join(self.test_dir, "iana-if-type@2015-06-12.yang")),
            ("ietf-inet-types", "2010-09-24",
             os.path.join(self.test_dir, "ietf-inet-types@2010-09-24.yang")),
            ("ietf-inet-types", "2013-07-15",
             os.path.join(self.test_dir, "ietf-inet-types@2013-07-15.yang")),
            ("ietf-interfaces", "2014-05-08",
             os.path.join(self.test_dir, "ietf-interfaces@2014-05-08.yang")),
            ("ietf-yang-types", "2010-09-24",
             os.path.join(self.test_dir, "ietf-yang-types@2010-09-24.yang")),
            ("ietf-yang-types", "2013-07-15",
             os.path.join(self.test_dir, "ietf-yang-types@2013-07-15.yang")),
            ("openconfig-if-ethernet", "2015-11-20",
             os.path.join(self.test_dir,
                          "openconfig-if-ethernet@2015-11-20.yang")),
            ("openconfig-interfaces", "2015-11-20",
                os.path.join(self.test_dir,
                             "openconfig-interfaces@2015-11-20.yang")),
        ], sorted(mods))

        handle = os.path.join(
            self.test_dir, "Cisco-IOS-XR-lib-keychain-act@2017-04-17.yang")
        filename, fmt, text = ys.get_module_from_handle(handle)

        self.assertEqual(handle, filename)
        self.assertEqual('yang', fmt)
        self.assertEqual(open(handle, 'r').read(), text)

    def test_repo_nonexistent(self):
        """Can't load a nonexistent directory as a repo."""
        self.assertRaises(OSError, self.cls, os.path.join(self.test_dir,
                                                          'nonexistent_repo'))

    def test_equality(self):
        """Test equality checks; overrides TestYSYangSetBase test logic."""
        ys1 = self.cls(self.test_dir)
        ys2 = self.cls(self.test_dir, "owner-doesnt-matter")
        ys3 = self.cls(self.base_dir)

        self.assertTrue(ys1 == ys2)
        self.assertFalse(ys1 == ys3)

        # Check inverse as well for python 2's sake.
        self.assertFalse(ys1 != ys2)
        self.assertTrue(ys1 != ys3)
