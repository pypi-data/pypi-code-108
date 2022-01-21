# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
# Copyright 2012 Canonical Ltd
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
from builtins import range
from future import standard_library
standard_library.install_aliases()

import os
import pexpect
import platform
import sys
import time

from duplicity import backend
from duplicity import util
from .. import DuplicityTestCase
from .. import _top_dir
from .. import _runtest_dir
from pkg_resources import parse_version


class CmdError(Exception):
    u"""Indicates an error running an external command"""
    def __init__(self, code):
        Exception.__init__(self, code)
        self.exit_status = code


class FunctionalTestCase(DuplicityTestCase):

    _setsid_w = None

    @classmethod
    def _check_setsid(cls):
        if cls._setsid_w is not None:
            return
        if platform.platform().startswith(u'Linux'):
            # setsid behavior differs between distributions.
            # If setsid supports -w ("wait"), use it.
            import subprocess
            try:
                with open(u"/dev/null", u"w") as sink:
                    subprocess.check_call([u"setsid", u"-w", u"ls"], stdout=sink, stderr=sink)
            except subprocess.CalledProcessError:
                cls._setsid_w = False
            else:
                cls._setsid_w = True

    def setUp(self):
        super(FunctionalTestCase, self).setUp()

        self.unpack_testfiles()

        self.class_args = []
        self.backend_url = u"file://{0}/testfiles/output".format(_runtest_dir)
        self.last_backup = None
        self.set_environ(u'PASSPHRASE', self.sign_passphrase)
        self.set_environ(u"SIGN_PASSPHRASE", self.sign_passphrase)

        backend_inst = backend.get_backend(self.backend_url)
        bl = backend_inst.list()
        if bl:
            backend_inst.delete(backend_inst.list())
        backend_inst.close()
        self._check_setsid()

    def run_duplicity(self, options=[], current_time=None, fail=None,
                      passphrase_input=[]):
        u"""
        Run duplicity binary with given arguments and options
        """
        # We run under setsid and take input from /dev/null (below) because
        # this way we force a failure if duplicity tries to read from the
        # console unexpectedly (like for gpg password or such).

        # Check all string inputs are unicode -- we will convert to system encoding before running the command
        for item in options:
            if sys.version_info.major == 2:
                assert not isinstance(item, str), u"item " + unicode(item) + u" in options is not unicode"

        for item in passphrase_input:
            assert isinstance(item, u"".__class__), u"item " + unicode(item) + u" in passphrase_input is not unicode"

        if platform.platform().startswith(u'Linux'):
            cmd_list = [u'setsid']
            if self._setsid_w:
                cmd_list.extend([u"-w"])
        else:
            cmd_list = []
        basepython = os.environ.get(u'TOXPYTHON', None)
        if basepython is not None:
            cmd_list.extend([basepython])
        run_coverage = os.environ.get(u'RUN_COVERAGE', None)
        if run_coverage is not None:
            cmd_list.extend([u"-m", u"coverage", u"run", u"--source=duplicity", u"-p"])
        cmd_list.extend([u"{0}/bin/duplicity".format(_top_dir)])
        cmd_list.extend(options)
        cmd_list.extend([u"-v0"])
        cmd_list.extend([u"--no-print-statistics"])
        cmd_list.extend([u"--allow-source-mismatch"])
        cmd_list.extend([u"--archive-dir={0}/testfiles/cache".format(_runtest_dir)])
        if current_time:
            cmd_list.extend([u"--current-time", current_time])
        cmd_list.extend(self.class_args)
        if fail:
            cmd_list.extend([u"--fail", u"".__class__(fail)])
        cmdline = u" ".join([u'"%s"' % x for x in cmd_list])

        if not passphrase_input:
            cmdline += u" < /dev/null"

        # The immediately following block is the nicer way to execute pexpect with
        # unicode strings, but we need to have the pre-4.0 version for some time yet,
        # so for now this is commented out so tests execute the same way on all systems.

        # if parse_version(pexpect.__version__) >= parse_version("4.0"):
        #     # pexpect.spawn only supports unicode from version 4.0
        #     # there was a separate pexpect.spawnu in 3.x, but it has an error on readline
        #     child = pexpect.spawn(u'/bin/sh', [u'-c', cmdline], timeout=None, encoding=sys.getfilesystemencoding())
        #
        #     for passphrase in passphrase_input:
        #         child.expect(u'passphrase.*:')
        #         child.sendline(passphrase)
        # else:

        # Manually encode to filesystem encoding and send to spawn as bytes
        # ToDo: Remove this once we no longer have to support systems with pexpect < 4.0
        if sys.version_info.major > 2:
            child = pexpect.spawn(u'/bin/sh', [u'-c', cmdline], timeout=None)
        else:
            child = pexpect.spawn(b'/bin/sh', [b'-c', cmdline.encode(sys.getfilesystemencoding(),
                                                                 u'replace')], timeout=None)

        for passphrase in passphrase_input:
            child.expect(b'passphrase.*:')
            child.sendline(passphrase)

        # if the command fails, we need to clear its output
        # so it will terminate cleanly.
        child.expect_exact(pexpect.EOF)
        lines = child.before.splitlines()
        child.wait()
        child.ptyproc.delayafterclose = 0.0
        return_val = child.exitstatus

        if fail:
            self.assertEqual(30, return_val)
        elif return_val:
            print(u"\n...command:", cmdline, file=sys.stderr)
            print(u"...cwd:", os.getcwd(), file=sys.stderr)
            print(u"...output:", file=sys.stderr)
            for line in lines:
                line = line.rstrip()
                if line:
                    print(line, file=sys.stderr)
            print(u"...return_val:", return_val, file=sys.stderr)
            raise CmdError(return_val)

    def backup(self, type, input_dir, options=[], **kwargs):  # pylint: disable=redefined-builtin
        u"""Run duplicity backup to default directory"""
        options = [type, input_dir, self.backend_url, u"--volsize", u"1"] + options
        before_files = self.get_backend_files()

        # If a chain ends with time X and the next full chain begins at time X,
        # we may trigger an assert in dup_collections.py.  If needed, sleep to
        # avoid such problems
        now = time.time()
        if self.last_backup == int(now):
            time.sleep(1)

        self.run_duplicity(options=options, **kwargs)
        self.last_backup = int(time.time())

        after_files = self.get_backend_files()
        return after_files - before_files

    def restore(self, file_to_restore=None, time=None, options=[], **kwargs):
        assert not os.system(u"rm -rf {0}/testfiles/restore_out".format(_runtest_dir))
        options = [self.backend_url, u"{0}/testfiles/restore_out".format(_runtest_dir)] + options
        if file_to_restore:
            options.extend([u'--file-to-restore', file_to_restore])
        if time:
            options.extend([u'--restore-time', u"".__class__(time)])
        self.run_duplicity(options=options, **kwargs)

    def verify(self, dirname, file_to_verify=None, time=None, options=[],
               **kwargs):
        options = [u"verify", self.backend_url, dirname] + options
        if file_to_verify:
            options.extend([u'--file-to-restore', file_to_verify])
        if time:
            options.extend([u'--restore-time', u"".__class__(time)])
        self.run_duplicity(options=options, **kwargs)

    def cleanup(self, options=[]):
        u"""
        Run duplicity cleanup to default directory
        """
        options = [u"cleanup", self.backend_url, u"--force"] + options
        self.run_duplicity(options=options)

    def get_backend_files(self):
        backend_inst = backend.get_backend(self.backend_url)
        bl = backend_inst.list()
        backend_inst.close()
        return set(bl)

    def make_largefiles(self, count=3, size=2):
        u"""
        Makes a number of large files in /tmp/testfiles/largefiles that each are
        the specified number of megabytes.
        """
        assert not os.system(u"mkdir {0}/testfiles/largefiles".format(_runtest_dir))
        for n in range(count):
            assert not os.system(
                u"dd if=/dev/urandom of={0}/testfiles/largefiles/file{1} bs=1024 count={2} > /dev/null 2>&1".format(
                    _runtest_dir, n + 1, size * 1024))
