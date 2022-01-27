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

import unittest
import os

from duplicity import path
from testing import _top_dir
from testing import _runtest_dir
from . import FunctionalTestCase


class RdiffdirTest(FunctionalTestCase):
    u"""Test rdiffdir command line program"""

    def run_cmd(self, command):
        assert not os.system(command)

    def run_rdiffdir(self, argstring):
        u"""Run rdiffdir with given arguments"""
        cmd_list = list()
        basepython = os.environ.get(u'TOXPYTHON', None)
        if basepython is not None:
            cmd_list.extend([basepython])
        cmd_list.extend([u"{0}/bin/rdiffdir".format(_top_dir)])
        cmd_list.extend(argstring.split())
        cmdline = u" ".join([u'"%s"' % x for x in cmd_list])
        self.run_cmd(cmdline)

    def run_cycle(self, dirname_list):
        u"""Run diff/patch cycle on directories in dirname_list"""
        assert len(dirname_list) >= 2

        seq_path = path.Path(u"{0}/testfiles/output/sequence".format(_runtest_dir))
        new_path = path.Path(dirname_list[0])
        delta_path = path.Path(u"{0}/testfiles/output/delta.tar".format(_runtest_dir))
        sig_path = path.Path(u"{0}/testfiles/output/sig.tar".format(_runtest_dir))

        self.run_cmd(u"cp -pR %s %s" % (new_path.uc_name, seq_path.uc_name))
        seq_path.setdata()
        self.run_rdiffdir(u"sig %s %s" % (seq_path.uc_name, sig_path.uc_name))
        sig_path.setdata()
        assert sig_path.exists()

        assert new_path.compare_recursive(seq_path, verbose = 1)

        for dirname in dirname_list[1:]:
            new_path = path.Path(dirname)

            # Make delta
            if delta_path.exists():
                delta_path.delete()
            assert not delta_path.exists()
            self.run_rdiffdir(u"delta %s %s %s" %
                              (sig_path.uc_name, new_path.uc_name, delta_path.uc_name))
            delta_path.setdata()
            assert delta_path.exists()

            # patch and compare
            self.run_rdiffdir(u"patch %s %s" % (seq_path.uc_name, delta_path.uc_name))
            seq_path.setdata()
            new_path.setdata()
            assert new_path.compare_recursive(seq_path, verbose=1)

            # Make new signature
            sig_path.delete()
            assert not sig_path.exists()
            self.run_rdiffdir(u"sig %s %s" % (seq_path.uc_name, sig_path.uc_name))
            sig_path.setdata()
            assert sig_path.isreg()

    def test_dirx(self):
        u"""Test cycle on {0}/testfiles/dirx"""
        self.run_cycle([u'{0}/testfiles/empty_dir'.format(_runtest_dir),
                        u'{0}/testfiles/dir1'.format(_runtest_dir),
                        u'{0}/testfiles/dir2'.format(_runtest_dir),
                        u'{0}/testfiles/dir3'.format(_runtest_dir),
                        u'{0}/testfiles/empty_dir'.format(_runtest_dir)])


if __name__ == u"__main__":
    unittest.main()
