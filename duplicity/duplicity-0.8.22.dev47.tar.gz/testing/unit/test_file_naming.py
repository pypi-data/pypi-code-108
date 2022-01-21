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
from builtins import object
from future import standard_library
standard_library.install_aliases()

import unittest

from duplicity import dup_time
from duplicity import file_naming
from duplicity import log
from duplicity import config
from duplicity import util
from . import UnitTestCase


class Test36(UnitTestCase):
    def test_base36(self):
        u"""Test conversion to/from base 36"""
        numlist = [0, 1, 10, 1313, 34233, 872338, 2342889,
                   134242234, 1204684368, 34972382455]
        for n in numlist:
            b = file_naming.to_base36(n)
            assert file_naming.from_base36(b) == n, (b, n)


class FileNamingBase(object):
    u"""Holds file naming test functions, for use in subclasses"""
    def test_basic(self):
        u"""Check get/parse cycle"""
        dup_time.setprevtime(10)
        dup_time.setcurtime(20)

        file_naming.prepare_regex(force=True)
        filename = file_naming.get(u"inc", volume_number=23)
        log.Info(u"Inc filename: " + util.fsdecode(filename))
        pr = file_naming.parse(filename)
        assert pr and pr.type == u"inc", pr
        assert pr.start_time == 10
        assert pr.end_time == 20
        assert pr.volume_number == 23
        assert not pr.partial

        filename = file_naming.get(u"full-sig")
        log.Info(u"Full sig filename: " + util.fsdecode(filename))
        pr = file_naming.parse(filename)
        assert pr.type == u"full-sig"
        assert pr.time == 20
        assert not pr.partial

        filename = file_naming.get(u"new-sig")
        pr = file_naming.parse(filename)
        assert pr.type == u"new-sig"
        assert pr.start_time == 10
        assert pr.end_time == 20
        assert not pr.partial

    def test_suffix(self):
        u"""Test suffix (encrypt/compressed) encoding and generation"""
        file_naming.prepare_regex(force=True)
        filename = file_naming.get(u"inc", manifest=1, gzipped=1)
        pr = file_naming.parse(filename)
        assert pr and pr.compressed == 1
        assert pr.manifest

        filename2 = file_naming.get(u"full", volume_number=23, encrypted=1)
        pr = file_naming.parse(filename2)
        assert pr and pr.encrypted == 1
        assert pr.volume_number == 23

    def test_more(self):
        u"""More file_parsing tests"""
        file_naming.prepare_regex(force=True)
        pr = file_naming.parse(config.file_prefix + config.file_prefix_signature + b"dns.h112bi.h14rg0.st.g")
        assert pr, pr
        assert pr.type == u"new-sig"
        assert pr.end_time == 1029826800

        if not config.short_filenames:
            pr = file_naming.parse(config.file_prefix + config.file_prefix_signature + b"duplicity-new-signatures.2002-08-18T00:04:30-07:00.to.2002-08-20T00:00:00-07:00.sigtar.gpg")
            assert pr, pr
            assert pr.type == u"new-sig"
            assert pr.end_time == 1029826800

        pr = file_naming.parse(config.file_prefix + config.file_prefix_signature + b"dfs.h5dixs.st.g")
        assert pr, pr
        assert pr.type == u"full-sig"
        assert pr.time == 1036954144, repr(pr.time)

    def test_partial(self):
        u"""Test addition of partial flag"""
        file_naming.prepare_regex(force=True)
        pr = file_naming.parse(config.file_prefix + config.file_prefix_signature + b"dns.h112bi.h14rg0.st.p.g")
        assert pr, pr
        assert pr.partial
        assert pr.type == u"new-sig"
        assert pr.end_time == 1029826800

        if not config.short_filenames:
            pr = file_naming.parse(config.file_prefix + config.file_prefix_signature + b"duplicity-new-signatures.2002-08-18T00:04:30-07:00.to.2002-08-20T00:00:00-07:00.sigtar.part.gpg")
            assert pr, pr
            assert pr.partial
            assert pr.type == u"new-sig"
            assert pr.end_time == 1029826800

        pr = file_naming.parse(config.file_prefix + config.file_prefix_signature + b"dfs.h5dixs.st.p.g")
        assert pr, pr
        assert pr.partial
        assert pr.type == u"full-sig"
        assert pr.time == 1036954144, repr(pr.time)


class FileNamingLong(UnitTestCase, FileNamingBase):
    u"""Test long filename parsing and generation"""
    def setUp(self):
        super(FileNamingLong, self).setUp()
        self.set_config(u'short_filenames', 0)


class FileNamingShort(UnitTestCase, FileNamingBase):
    u"""Test short filename parsing and generation"""
    def setUp(self):
        super(FileNamingShort, self).setUp()
        self.set_config(u'short_filenames', 1)


class FileNamingPrefixes(UnitTestCase, FileNamingBase):
    u"""Test filename parsing and generation with prefixes"""
    def setUp(self):
        super(FileNamingPrefixes, self).setUp()
        self.set_config(u'file_prefix', b"global-")
        self.set_config(u'file_prefix_manifest', b"mani-")
        self.set_config(u'file_prefix_signature', b"sign-")
        self.set_config(u'file_prefix_archive', b"arch-")


if __name__ == u"__main__":
    unittest.main()
