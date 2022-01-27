# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import re
import unittest
from mock import patch

from duplicity import config
from duplicity import manifest
from duplicity import path

from . import UnitTestCase


class VolumeInfoTest(UnitTestCase):
    u"""Test VolumeInfo"""
    def test_basic(self):
        u"""Basic VolumeInfoTest"""
        vi = manifest.VolumeInfo()
        vi.set_info(3, (b"hello", b"there"), None, (), None)
        vi.set_hash(u"MD5", u"aoseutaohe")
        s = vi.to_string()
        assert isinstance(s, (b"".__class__, u"".__class__))
        # print "---------\n%s\n---------" % s
        vi2 = manifest.VolumeInfo()
        vi2.from_string(s)
        assert vi == vi2

    def test_special(self):
        u"""Test VolumeInfo with special characters"""
        vi = manifest.VolumeInfo()
        vi.set_info(3234,
                    (b"\n eu \x233", b"heuo", b'\xd8\xab\xb1Wb\xae\xc5]\x8a\xbb\x15v*\xf4\x0f!\xf9>\xe2Y\x86\xbb\xab\xdbp\xb0\x84\x13k\x1d\xc2\xf1\xf5e\xa5U\x82\x9aUV\xa0\xf4\xdf4\xba\xfdX\x03\x82\x07s\xce\x9e\x8b\xb34\x04\x9f\x17 \xf4\x8f\xa6\xfa\x97\xab\xd8\xac\xda\x85\xdcKvC\xfa#\x94\x92\x9e\xc9\xb7\xc3_\x0f\x84g\x9aB\x11<=^\xdbM\x13\x96c\x8b\xa7|*"\\\'^$@#!(){}?+ ~` '),
                    None,
                    (b"\n",),
                    None)
        s = vi.to_string()
        assert isinstance(s, (str, bytes))
        # print "---------\n%s\n---------" % s
        vi2 = manifest.VolumeInfo()
        vi2.from_string(s)
        assert vi == vi2

    def test_contains(self):
        u"""Test to see if contains() works"""
        vi = manifest.VolumeInfo()
        vi.set_info(1, (u"1", u"2"), None, (u"1", u"3"), None)
        assert vi.contains((u"1",), recursive=1)
        assert not vi.contains((u"1",), recursive=0)

        vi2 = manifest.VolumeInfo()
        vi2.set_info(1, (u"A",), None, (u"Z",), None)
        assert vi2.contains((u"M",), recursive=1)
        assert vi2.contains((u"M",), recursive=0)

        vi3 = manifest.VolumeInfo()
        vi3.set_info(1, (u"A",), None, (u"Z",), None)
        assert not vi3.contains((u"3",), recursive=1)
        assert not vi3.contains((u"3",), recursive=0)


class ManifestTest(UnitTestCase):
    u"""Test Manifest class"""

    def setUp(self):
        UnitTestCase.setUp(self)
        self.old_files_changed = config.file_changed
        config.file_changed = u'testing'

    def tearDown(self):
        config.file_changed = self.old_files_changed

    def test_basic(self):
        vi1 = manifest.VolumeInfo()
        vi1.set_info(3, (b"hello",), None, (), None)
        vi2 = manifest.VolumeInfo()
        vi2.set_info(4, (b"goodbye", b"there"), None, (b"aoeusht",), None)
        vi3 = manifest.VolumeInfo()
        vi3.set_info(34, (), None, (), None)
        m = manifest.Manifest()
        for vi in [vi1, vi2, vi3]:
            m.add_volume_info(vi)

        self.set_config(u'local_path', path.Path(u"Foobar"))
        m.set_dirinfo()
        m.set_files_changed_info([])

        s = m.to_string()
        assert s.lower().startswith(b"hostname")
        assert s.endswith(b"\n")

        m2 = manifest.Manifest().from_string(s)
        assert m == m2

    def test_corrupt_filelist(self):
        vi1 = manifest.VolumeInfo()
        vi1.set_info(3, (b"hello",), None, (), None)
        vi2 = manifest.VolumeInfo()
        vi2.set_info(4, (b"goodbye", b"there"), None, (b"aoeusht",), None)
        vi3 = manifest.VolumeInfo()
        vi3.set_info(34, (), None, (), None)
        m = manifest.Manifest()
        for vi in [vi1, vi2, vi3]:
            m.add_volume_info(vi)

        self.set_config(u'local_path', path.Path(u"Foobar"))
        m.set_dirinfo()
        m.set_files_changed_info([
            (b'one', b'new'),
            (b'two', b'changed'),
            (b'three', b'new'),
            ])

        # build manifest string
        s = m.to_string()

        # make filecount higher than files in list
        s2 = re.sub(b'Filelist 3', b'Filelist 5', s)
        m2 = manifest.Manifest().from_string(s2)
        assert hasattr(m2, u'corrupt_filelist')

    def test_hostname_checks(self):
        self.set_config(u'hostname', u'hostname')
        self.set_config(u'fqdn', u'fqdn')
        m = manifest.Manifest()

        # Matching hostname should work
        m.hostname = u'hostname'
        m.check_dirinfo()

        # Matching fqdn should also work for backwards compatibility
        m.hostname = u'fqdn'
        m.check_dirinfo()

        # Bad match should throw a fatal error and quit
        m.hostname = u'foobar'
        self.assertRaises(SystemExit, m.check_dirinfo)

        # But not if we tell the system to ignore it
        self.set_config(u'allow_source_mismatch', True)
        m.check_dirinfo()


if __name__ == u"__main__":
    unittest.main()
