# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
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

import unittest
import duplicity

class TestExc(unittest.TestCase):

    def test_uexc(self):

        e = Exception(u'test')
        msg = duplicity.util.uexc(e)
        self.assertEqual(msg, u'test')

        # Test for Bug #1770929
        # https://bugs.launchpad.net/duplicity/+bug/1770929
        e = Exception(b'\xe3\x83\x86\xe3\x82\xb9\xe3\x83\x88')
        msg = duplicity.util.uexc(e)
        self.assertEqual(msg, u'\u30c6\u30b9\u30c8')

        e = Exception(u'\u30c6\u30b9\u30c8')
        msg = duplicity.util.uexc(e)
        self.assertEqual(msg, u'\u30c6\u30b9\u30c8')


if __name__ == u'__main__':
    unittest.main()
