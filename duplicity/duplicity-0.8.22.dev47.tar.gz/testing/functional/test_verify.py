# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2014 Aaron Whitehouse <aaron@whitehouse.kiwi.nz>
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

import os
import unittest

from testing import _runtest_dir
from . import CmdError, FunctionalTestCase


class VerifyTest(FunctionalTestCase):
    u"""
    Test verify using duplicity binary
    """
    def test_verify(self):
        u"""Test that verify (without --compare-data) works in the basic case"""
        self.backup(u"full", u"{0}/testfiles/various_file_types".format(_runtest_dir), options=[])
        self.verify(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), file_to_verify=u'executable', options=[])

    def test_verify_changed_source_file(self):
        u"""Test verify (without --compare-data) gives no error if a source file is changed"""
        # This test was made to pass in fixing Bug #1354880
        self.backup(u"full", u"{0}/testfiles/various_file_types".format(_runtest_dir), options=[])

        # Edit source file
        with open(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), u'r+') as f:
            f.write(u'This changes a source file.')

        # Test verify for the file
        self.verify(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), file_to_verify=u'executable', options=[])

    def test_verify_changed_source_file_adjust_mtime(self):
        u"""Test verify (without --compare-data) gives no error if a source file is changed and the mtime is changed
        (changing anything about the source files shouldn't matter)"""

        # Get the atime and mtime of the file
        file_info = os.stat(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir))

        # Set the atime and mtime of the file to the time that we collected, as on some systems
        # the times from a stat call don't match what a utime will set.
        os.utime(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), (file_info.st_atime, file_info.st_mtime))

        self.backup(u"full", u"{0}/testfiles/various_file_types".format(_runtest_dir), options=[])

        # Edit source file
        with open(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), u'r+') as f:
            f.write(u'This changes a source file.')

        # Set the atime and mtime for the file back to what it was prior to the edit
        os.utime(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), (file_info.st_atime, file_info.st_mtime))

        # Test verify for the file
        self.verify(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), file_to_verify=u'executable', options=[])

    def test_verify_compare_data(self):
        u"""Test that verify works in the basic case when the --compare-data option is used"""
        self.backup(u"full", u"{0}/testfiles/various_file_types".format(_runtest_dir), options=[])

        # Test verify for the file with --compare-data
        self.verify(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), file_to_verify=u'executable',
                    options=[u"--compare-data"])

    def test_verify_compare_data_changed_source_file(self):
        u"""Test verify with --compare-data gives an error if a source file is changed"""
        self.backup(u"full", u"{0}/testfiles/various_file_types".format(_runtest_dir), options=[])

        # Edit source file
        with open(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), u'r+') as f:
            f.write(u'This changes a source file.')

        # Test verify for edited file fails with --compare-data
        try:
            self.verify(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), file_to_verify=u'executable',
                        options=[u"--compare-data"])
        except CmdError as e:
            self.assertEqual(e.exit_status, 1, str(e))
        else:
            self.fail(u'Expected CmdError not thrown')

    def test_verify_compare_data_changed_source_file_adjust_mtime(self):
        u"""Test verify with --compare-data gives an error if a source file is changed, even if the mtime is changed"""

        # Get the atime and mtime of the file
        file_info = os.stat(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir))

        # Set the atime and mtime of the file to the time that we collected, as on some systems
        # the times from a stat call don't match what a utime will set
        os.utime(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), (file_info.st_atime, file_info.st_mtime))

        self.backup(u"full", u"{0}/testfiles/various_file_types".format(_runtest_dir), options=[])
        # Edit source file
        with open(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), u'r+') as f:
            f.write(u'This changes a source file.')

        # Set the atime and mtime for the file back to what it was prior to the edit
        os.utime(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), (file_info.st_atime, file_info.st_mtime))

        # Test verify for edited file fails with --compare-data
        try:
            self.verify(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), file_to_verify=u'executable',
                        options=[u"--compare-data"])
        except CmdError as e:
            self.assertEqual(e.exit_status, 1, str(e))
        else:
            self.fail(u'Expected CmdError not thrown')

    def test_verify_corrupt_archive(self):
        u"""Test verify (without --compare-data) gives an error if the archive is corrupted"""
        self.backup(u"full", u"{0}/testfiles/various_file_types".format(_runtest_dir), options=[])
        output_files = os.listdir(u"{0}/testfiles/output".format(_runtest_dir))
        archives = [elem for elem in output_files if u"vol" in elem]
        for archive in archives:
            # Edit source file
            with open(u"{0}/testfiles/output/".format(_runtest_dir) + archive, u'r+') as f:
                f.write(u'This writes text into each archive file to corrupt it.')
        # Test verify for the file
        try:
            self.verify(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), file_to_verify=u'executable', options=[])
        except CmdError as e:
            # Should return a 21 error code for "hash mismatch"
            self.assertEqual(e.exit_status, 21, str(e))
        else:
            self.fail(u'Expected Hash Mismatch Error not thrown')

    def test_verify_corrupt_archive_compare_data(self):
        u"""Test verify with --compare-data gives an error if the archive is corrupted"""
        self.backup(u"full", u"{0}/testfiles/various_file_types".format(_runtest_dir), options=[])
        output_files = os.listdir(u"{0}/testfiles/output".format(_runtest_dir))
        archives = [elem for elem in output_files if u"vol" in elem]
        for archive in archives:
            # Edit source file
            with open(u"{0}/testfiles/output/".format(_runtest_dir) + archive, u'r+') as f:
                f.write(u'This writes text into each archive file to corrupt it.')
        # Test verify for the file
        try:
            self.verify(u'{0}/testfiles/various_file_types/executable'.format(_runtest_dir), file_to_verify=u'executable',
                        options=[u"--compare-data"])
        except CmdError as e:
            # Should return a 21 error code for "hash mismatch"
            self.assertEqual(e.exit_status, 21, str(e))
        else:
            self.fail(u'Expected Hash Mismatch Error not thrown')

if __name__ == u"__main__":
    unittest.main()
