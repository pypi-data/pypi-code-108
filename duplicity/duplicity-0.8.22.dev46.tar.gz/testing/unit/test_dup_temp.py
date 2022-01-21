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

import gzip
import unittest

from duplicity import dup_temp
from duplicity import file_naming
from . import UnitTestCase


class TempTest(UnitTestCase):
    u"""Test various temp files methods"""

    def test_temppath(self):
        u"""Allocate new temppath, try open_with_delete"""
        tp = dup_temp.new_temppath()
        assert not tp.exists()
        fileobj = tp.open(u"wb")
        fileobj.write(b"hello, there")
        fileobj.close()
        tp.setdata()
        assert tp.isreg()

        fin = tp.open_with_delete(u"rb")
        buf = fin.read()
        assert buf == b"hello, there", buf
        fin.close()
        assert not tp.exists()

    def test_tempduppath(self):
        u"""Allocate new tempduppath, then open_with_delete"""
        # pr indicates file is gzipped
        pr = file_naming.ParseResults(u"inc", manifest=1,
                                      start_time=1, end_time=3,
                                      compressed=1)

        tdp = dup_temp.new_tempduppath(pr)
        assert not tdp.exists()
        fout = tdp.filtered_open(u"wb")
        fout.write(b"hello, there")
        fout.close()
        tdp.setdata()
        assert tdp.isreg()

        fin1 = gzip.GzipFile(tdp.name, u"rb")
        buf = fin1.read()
        assert buf == b"hello, there", buf
        fin1.close()

        fin2 = tdp.filtered_open_with_delete(u"rb")
        buf2 = fin2.read()
        assert buf2 == b"hello, there", buf
        fin2.close()
        assert not tdp.exists()


if __name__ == u"__main__":
    unittest.main()
